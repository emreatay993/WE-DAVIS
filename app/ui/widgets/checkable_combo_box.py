"""Reusable multi-select combo-box widget.

Visual target: ``mockups/multiselect_variations.html`` Variation 1
("Checkable Dropdown"). The widget is built from scratch as a ``QWidget``
composition rather than by subclassing ``QComboBox`` because Qt's combo
popup is awkward to extend with a search box and action bar.

Two modes are supported:

* **Flat** via :meth:`set_items` — every string becomes a plain checkable row.
* **Grouped** via :meth:`set_grouped_items` — each ``(header, children)`` tuple
  renders a disabled header row (matching the mockup's ``.hier-group-head``)
  followed by indented checkable child rows.

The widget emits :attr:`selectionChanged` through a 100 ms debounced timer so
that rapid multi-check interactions collapse into a single signal, and it only
re-emits when the actual checked set changes.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

from app import config_manager


# --------------------------------------------------------------------------- #
# UserRole markers attached to each list item
# --------------------------------------------------------------------------- #

_ROLE_KIND = QtCore.Qt.UserRole + 1      # "header" | "child" | "empty"
_ROLE_VALUE = QtCore.Qt.UserRole + 2     # the original item string (for children)
_ROLE_GROUP = QtCore.Qt.UserRole + 3     # the group-header text a child belongs to


class CheckableComboBox(QtWidgets.QWidget):
    """Combo-box-like multi-select widget with search and Select all / Clear.

    See module docstring for the overall design. The trigger button mimics a
    ``QComboBox`` field; the popup is a floating ``QFrame`` containing a
    search box, a checkable ``QListWidget``, and two ghost action buttons.
    """

    # Emitted (debounced) when the checked set actually changes.
    selectionChanged = QtCore.pyqtSignal()

    _DEBOUNCE_MS = 100
    _MIN_POPUP_WIDTH = 300

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        # Identity for QSS targeting.
        self.setObjectName("CheckableComboBox")

        # -------- Configuration state --------
        self._placeholder: str = "Select items…"
        self._noun_singular: str = "item"
        self._noun_plural: str = "items"

        # "flat" or "grouped" — tracks which populate call was last used so we
        # can preserve semantics on repopulation.
        self._mode: str = "flat"

        # Last emitted selection, used to dedupe emissions.
        self._last_emitted_selection: Tuple[str, ...] = ()

        # Event filter installation tracker (avoid double-install).
        self._outside_filter_installed: bool = False

        # -------- Trigger button --------
        self._trigger = QtWidgets.QPushButton(self)
        self._trigger.setObjectName("CheckableComboBoxTrigger")
        self._trigger.setCursor(QtCore.Qt.PointingHandCursor)
        self._trigger.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._trigger.clicked.connect(self._toggle_popup)

        # Inside the trigger: [badge] [summary label] <stretch> [caret]
        trigger_layout = QtWidgets.QHBoxLayout(self._trigger)
        trigger_layout.setContentsMargins(4, 0, 4, 0)
        trigger_layout.setSpacing(6)

        self._count_badge = QtWidgets.QLabel(self._trigger)
        self._count_badge.setObjectName("CheckableComboBoxCountBadge")
        self._count_badge.setAlignment(QtCore.Qt.AlignCenter)
        self._count_badge.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self._count_badge.hide()

        self._summary_label = QtWidgets.QLabel(self._trigger)
        self._summary_label.setObjectName("CheckableComboBoxSummary")
        self._summary_label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self._summary_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        self._caret = QtWidgets.QLabel("\u25BE", self._trigger)
        self._caret.setObjectName("CheckableComboBoxCaret")
        self._caret.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        trigger_layout.addWidget(self._count_badge, 0, QtCore.Qt.AlignVCenter)
        trigger_layout.addWidget(self._summary_label, 1, QtCore.Qt.AlignVCenter)
        trigger_layout.addStretch(0)
        trigger_layout.addWidget(self._caret, 0, QtCore.Qt.AlignVCenter)

        # Widget-level layout just hosts the trigger.
        outer = QtWidgets.QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._trigger)

        # -------- Popup --------
        # Parent set to ``self`` so lifetime is managed by the widget.
        self._popup = QtWidgets.QFrame(
            self,
            QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint,
        )
        self._popup.setObjectName("CheckableComboBoxPopup")
        self._popup.setAttribute(QtCore.Qt.WA_WindowPropagation, True)
        self._popup.hide()

        popup_layout = QtWidgets.QVBoxLayout(self._popup)
        popup_layout.setContentsMargins(6, 6, 6, 0)
        popup_layout.setSpacing(4)

        self._search = QtWidgets.QLineEdit(self._popup)
        self._search.setObjectName("CheckableComboBoxSearch")
        self._search.setPlaceholderText("Search…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._apply_filter)
        popup_layout.addWidget(self._search)

        self._list = QtWidgets.QListWidget(self._popup)
        self._list.setObjectName("CheckableComboBoxList")
        self._list.setUniformItemSizes(False)
        self._list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self._list.setFocusPolicy(QtCore.Qt.NoFocus)
        self._list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self._list.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._list.setTextElideMode(QtCore.Qt.ElideRight)
        self._list.itemChanged.connect(self._on_item_changed)
        self._list.itemClicked.connect(self._on_item_clicked)
        popup_layout.addWidget(self._list, 1)

        self._footer = QtWidgets.QFrame(self._popup)
        self._footer.setObjectName("CheckableComboBoxFooter")
        footer_layout = QtWidgets.QHBoxLayout(self._footer)
        footer_layout.setContentsMargins(6, 5, 6, 5)
        footer_layout.setSpacing(6)

        self._btn_select_all = QtWidgets.QPushButton("Select all", self._footer)
        self._btn_select_all.setObjectName("CheckableComboBoxGhost")
        self._btn_select_all.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_select_all.clicked.connect(self._on_select_all_clicked)

        self._btn_clear = QtWidgets.QPushButton("Clear", self._footer)
        self._btn_clear.setObjectName("CheckableComboBoxGhost")
        self._btn_clear.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_clear.clicked.connect(self._on_clear_clicked)

        footer_layout.addWidget(self._btn_select_all)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self._btn_clear)

        # Manually re-parent the footer outside the main popup layout's
        # content margins so it sits flush with the popup edges.
        popup_layout.addWidget(self._footer)

        # -------- Debounce timer --------
        self._debounce_timer = QtCore.QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(self._DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._emit_selection_changed)

        # -------- Styling --------
        self.setStyleSheet(config_manager.CHECKABLE_COMBO_STYLE)

        # Default sizing & empty-state summary.
        self.setMinimumHeight(30)
        self.setMinimumWidth(self._MIN_POPUP_WIDTH)
        self._refresh_summary()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def set_placeholder(self, text: str) -> None:
        """Change the summary text shown when no items are checked."""
        self._placeholder = text or ""
        self._refresh_summary()

    def set_noun(self, singular: str, plural: str) -> None:
        """Set the noun used in the "N items selected" summary."""
        self._noun_singular = singular or "item"
        self._noun_plural = plural or self._noun_singular + "s"
        self._search.setPlaceholderText(f"Search {self._noun_plural}\u2026")
        self._refresh_summary()

    def set_items(
        self,
        items: Sequence[str],
        preserve_selection: bool = True,
    ) -> None:
        """Populate as a flat list of checkable rows.

        When ``preserve_selection`` is True, any currently-checked items that
        still exist in ``items`` remain checked.
        """
        prior_selected = set(self.selected_items()) if preserve_selection else set()

        self._mode = "flat"
        self._list.blockSignals(True)
        try:
            self._list.clear()
            for text in items:
                item = self._make_child_item(text, group=None)
                checked = preserve_selection and text in prior_selected
                item.setCheckState(
                    QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked,
                )
                self._list.addItem(item)
        finally:
            self._list.blockSignals(False)

        self._apply_filter(self._search.text())
        self._refresh_summary()
        self._schedule_emit()

    def set_grouped_items(
        self,
        groups: Sequence[Tuple[str, Sequence[str]]],
        preserve_selection: bool = True,
    ) -> None:
        """Populate as grouped, indented checkable rows.

        Each entry is ``(header, children)``. Headers render as disabled
        teal-dark rows; children render as indented checkable rows.
        """
        prior_selected = set(self.selected_items()) if preserve_selection else set()

        self._mode = "grouped"
        self._list.blockSignals(True)
        try:
            self._list.clear()
            first_header = True
            for header, children in groups:
                header_item = self._make_header_item(str(header), first=first_header)
                self._list.addItem(header_item)
                first_header = False
                for child in children:
                    item = self._make_child_item(str(child), group=str(header))
                    checked = preserve_selection and child in prior_selected
                    item.setCheckState(
                        QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked,
                    )
                    self._list.addItem(item)
        finally:
            self._list.blockSignals(False)

        self._apply_filter(self._search.text())
        self._refresh_summary()
        self._schedule_emit()

    def selected_items(self) -> List[str]:
        """Return the list of currently-checked child items (in list order)."""
        selected: List[str] = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if self._kind_of(item) != "child":
                continue
            if item.checkState() == QtCore.Qt.Checked:
                selected.append(self._value_of(item))
        return selected

    def selected_grouped_items(self) -> List[Tuple[Optional[str], str]]:
        """Return checked child items together with their group/header label."""
        selected: List[Tuple[Optional[str], str]] = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if self._kind_of(item) != "child":
                continue
            if item.checkState() == QtCore.Qt.Checked:
                selected.append((self._group_of(item), self._value_of(item)))
        return selected

    def set_selected_items(self, items: Iterable[str]) -> None:
        """Set which child items are checked (by value)."""
        target = set(items or ())
        self._list.blockSignals(True)
        try:
            for i in range(self._list.count()):
                item = self._list.item(i)
                if self._kind_of(item) != "child":
                    continue
                value = self._value_of(item)
                item.setCheckState(
                    QtCore.Qt.Checked if value in target else QtCore.Qt.Unchecked,
                )
        finally:
            self._list.blockSignals(False)

        self._refresh_summary()
        self._schedule_emit()

    def clear_selection(self) -> None:
        """Uncheck every child item."""
        self._list.blockSignals(True)
        try:
            for i in range(self._list.count()):
                item = self._list.item(i)
                if self._kind_of(item) != "child":
                    continue
                item.setCheckState(QtCore.Qt.Unchecked)
        finally:
            self._list.blockSignals(False)
        self._refresh_summary()
        self._schedule_emit()

    def select_all(self) -> None:
        """Check every child item (ignores search filter — programmatic)."""
        self._list.blockSignals(True)
        try:
            for i in range(self._list.count()):
                item = self._list.item(i)
                if self._kind_of(item) != "child":
                    continue
                item.setCheckState(QtCore.Qt.Checked)
        finally:
            self._list.blockSignals(False)
        self._refresh_summary()
        self._schedule_emit()

    def all_items(self) -> List[str]:
        """Return every child item (checked or not), in list order."""
        values: List[str] = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if self._kind_of(item) != "child":
                continue
            values.append(self._value_of(item))
        return values

    # ------------------------------------------------------------------ #
    # Internal helpers — item construction
    # ------------------------------------------------------------------ #

    def _make_header_item(self, text: str, first: bool) -> QtWidgets.QListWidgetItem:
        item = QtWidgets.QListWidgetItem(text)
        item.setFlags(QtCore.Qt.ItemFlags(QtCore.Qt.NoItemFlags))
        item.setData(_ROLE_KIND, "header")
        item.setData(_ROLE_VALUE, text)

        font = QtGui.QFont(self._list.font())
        font.setBold(True)
        font.setPointSizeF(max(font.pointSizeF() - 0.5, 8.0))
        item.setFont(font)
        item.setForeground(QtGui.QBrush(QtGui.QColor("#006064")))

        # The dashed upper border from the mockup is approximated by a little
        # extra top-padding on every header after the first. We use the
        # SizeHintRole to add vertical padding; the QSS itself handles the
        # rest of the visual weight.
        hint = item.sizeHint()
        if hint.isValid():
            extra_top = 0 if first else 6
            item.setSizeHint(QtCore.QSize(hint.width(), max(hint.height(), 0) + 6 + extra_top))
        else:
            item.setSizeHint(QtCore.QSize(0, 26))

        # Visual separator via a top margin glyph in the text: a thin dashed
        # line is not directly expressible as QSS on a single QListWidgetItem,
        # so we rely on the typography + colour to read as a section header.
        return item

    def _make_child_item(
        self,
        text: str,
        group: Optional[str],
    ) -> QtWidgets.QListWidgetItem:
        item = QtWidgets.QListWidgetItem(text)
        item.setFlags(
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsUserCheckable,
        )
        item.setData(_ROLE_KIND, "child")
        item.setData(_ROLE_VALUE, text)
        if group is not None:
            item.setData(_ROLE_GROUP, group)
        item.setCheckState(QtCore.Qt.Unchecked)
        # Indent grouped children so they read as belonging to the header.
        if group is not None:
            item.setData(QtCore.Qt.TextAlignmentRole, int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
            # A lightweight left pad via a leading space; combined with the
            # checkbox indicator width the row visually aligns past the header.
            item.setText("    " + text)
        return item

    def _make_empty_item(self, text: str) -> QtWidgets.QListWidgetItem:
        item = QtWidgets.QListWidgetItem(text)
        item.setFlags(QtCore.Qt.ItemFlags(QtCore.Qt.NoItemFlags))
        item.setData(_ROLE_KIND, "empty")
        font = QtGui.QFont(self._list.font())
        font.setItalic(True)
        item.setFont(font)
        item.setForeground(QtGui.QBrush(QtGui.QColor("#888888")))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        return item

    # ------------------------------------------------------------------ #
    # Role accessors
    # ------------------------------------------------------------------ #

    @staticmethod
    def _kind_of(item: QtWidgets.QListWidgetItem) -> str:
        if item is None:
            return ""
        kind = item.data(_ROLE_KIND)
        return kind if isinstance(kind, str) else ""

    @staticmethod
    def _value_of(item: QtWidgets.QListWidgetItem) -> str:
        if item is None:
            return ""
        value = item.data(_ROLE_VALUE)
        return value if isinstance(value, str) else (item.text() or "")

    @staticmethod
    def _group_of(item: QtWidgets.QListWidgetItem) -> Optional[str]:
        if item is None:
            return None
        g = item.data(_ROLE_GROUP)
        return g if isinstance(g, str) else None

    # ------------------------------------------------------------------ #
    # Search filtering
    # ------------------------------------------------------------------ #

    def _apply_filter(self, text: str) -> None:
        """Show only rows whose text matches ``text`` (case-insensitive).

        In grouped mode, a header row stays visible if any of its children
        still match. If the filter produces nothing visible, a disabled
        "No matches" row is appended (non-persistent).
        """
        # First, strip any previously-added transient "empty" markers.
        self._remove_empty_markers()

        needle = (text or "").strip().lower()

        # Pass 1: decide child visibility; track which groups still have a
        # visible child.
        groups_with_match: set = set()
        child_any_visible = False
        had_any_child = False
        for i in range(self._list.count()):
            item = self._list.item(i)
            if self._kind_of(item) != "child":
                continue
            had_any_child = True
            value = self._value_of(item)
            visible = True if not needle else needle in value.lower()
            self._list.setRowHidden(i, not visible)
            if visible:
                child_any_visible = True
                group = self._group_of(item)
                if group is not None:
                    groups_with_match.add(group)

        # Pass 2: decide header visibility based on whether their group has a
        # surviving child.
        had_any_header = False
        for i in range(self._list.count()):
            item = self._list.item(i)
            if self._kind_of(item) != "header":
                continue
            had_any_header = True
            header_text = self._value_of(item)
            # When no filter, always show headers. With a filter, only show
            # headers whose group has at least one visible child.
            visible = True if not needle else header_text in groups_with_match
            self._list.setRowHidden(i, not visible)

        # Empty-state rows.
        if not had_any_child:
            # The widget itself is empty — show a contextual placeholder.
            if self._mode == "grouped":
                placeholder_text = "Select at least one interface first."
            else:
                placeholder_text = "No items available."
            self._list.addItem(self._make_empty_item(placeholder_text))
        elif not child_any_visible:
            self._list.addItem(self._make_empty_item("No matches"))

    def _remove_empty_markers(self) -> None:
        # Walk backwards so removal doesn't shift indices.
        for i in range(self._list.count() - 1, -1, -1):
            item = self._list.item(i)
            if self._kind_of(item) == "empty":
                self._list.takeItem(i)

    # ------------------------------------------------------------------ #
    # Item interaction
    # ------------------------------------------------------------------ #

    def _on_item_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        """Toggle check state when the row is clicked (not just the indicator)."""
        if self._kind_of(item) != "child":
            return
        new_state = (
            QtCore.Qt.Unchecked
            if item.checkState() == QtCore.Qt.Checked
            else QtCore.Qt.Checked
        )
        # blockSignals so we don't fire itemChanged twice in a row.
        self._list.blockSignals(True)
        try:
            item.setCheckState(new_state)
        finally:
            self._list.blockSignals(False)
        self._refresh_summary()
        self._schedule_emit()

    def _on_item_changed(self, item: QtWidgets.QListWidgetItem) -> None:
        if self._kind_of(item) != "child":
            return
        self._refresh_summary()
        self._schedule_emit()

    def _on_select_all_clicked(self) -> None:
        """Check all currently-visible child rows (respects active filter)."""
        self._list.blockSignals(True)
        try:
            for i in range(self._list.count()):
                if self._list.isRowHidden(i):
                    continue
                item = self._list.item(i)
                if self._kind_of(item) != "child":
                    continue
                item.setCheckState(QtCore.Qt.Checked)
        finally:
            self._list.blockSignals(False)
        self._refresh_summary()
        self._schedule_emit()

    def _on_clear_clicked(self) -> None:
        """Clear all currently-visible child rows (respects active filter)."""
        self._list.blockSignals(True)
        try:
            for i in range(self._list.count()):
                if self._list.isRowHidden(i):
                    continue
                item = self._list.item(i)
                if self._kind_of(item) != "child":
                    continue
                item.setCheckState(QtCore.Qt.Unchecked)
        finally:
            self._list.blockSignals(False)
        self._refresh_summary()
        self._schedule_emit()

    # ------------------------------------------------------------------ #
    # Popup show / hide / outside-click
    # ------------------------------------------------------------------ #

    def _toggle_popup(self) -> None:
        if self._popup.isVisible():
            self._popup.hide()
        else:
            self._show_popup()

    def _show_popup(self) -> None:
        self._position_popup()
        self._popup.show()
        self._popup.raise_()
        # Install a click-outside filter while the popup is open.
        if not self._outside_filter_installed:
            app = QtWidgets.QApplication.instance()
            if app is not None:
                app.installEventFilter(self)
                self._outside_filter_installed = True
        # Give the search box focus so users can type immediately.
        self._search.setFocus(QtCore.Qt.PopupFocusReason)
        self._search.selectAll()

    def _position_popup(self) -> None:
        # Anchor: just below the trigger's bottom-left in global coords.
        anchor = self._trigger.mapToGlobal(QtCore.QPoint(0, self._trigger.height()))
        width = max(self._trigger.width(), self._MIN_POPUP_WIDTH)

        # Target height: prefer a sensible cap for the list.
        target_height = 320

        # Clamp to the screen that contains the anchor so the popup never
        # spills off-screen.
        screen = QtWidgets.QApplication.screenAt(anchor)
        if screen is None:
            screen = QtWidgets.QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else QtCore.QRect()

        x, y = anchor.x(), anchor.y() + 4
        if available.isValid():
            if x + width > available.right():
                x = max(available.left(), available.right() - width)
            if y + target_height > available.bottom():
                # Flip above the trigger if there isn't room below.
                above_y = self._trigger.mapToGlobal(QtCore.QPoint(0, 0)).y() - target_height - 4
                if above_y >= available.top():
                    y = above_y
                else:
                    target_height = max(120, available.bottom() - y - 4)

        self._popup.setFixedWidth(width)
        self._popup.setMaximumHeight(target_height)
        self._popup.move(x, y)

    def _hide_popup(self) -> None:
        if self._popup.isVisible():
            self._popup.hide()
        if self._outside_filter_installed:
            app = QtWidgets.QApplication.instance()
            if app is not None:
                app.removeEventFilter(self)
            self._outside_filter_installed = False

    # ------------------------------------------------------------------ #
    # Event handling
    # ------------------------------------------------------------------ #

    def eventFilter(self, obj, event):  # noqa: D401 — Qt override
        """Close the popup when a click lands outside it."""
        et = event.type()
        if et in (
            QtCore.QEvent.MouseButtonPress,
            QtCore.QEvent.MouseButtonDblClick,
            QtCore.QEvent.NonClientAreaMouseButtonPress,
        ):
            # Use global position so widget-local coords don't matter.
            try:
                global_pos = event.globalPos()
            except AttributeError:
                global_pos = QtGui.QCursor.pos()

            popup_rect = QtCore.QRect(
                self._popup.mapToGlobal(QtCore.QPoint(0, 0)),
                self._popup.size(),
            )
            trigger_rect = QtCore.QRect(
                self._trigger.mapToGlobal(QtCore.QPoint(0, 0)),
                self._trigger.size(),
            )
            if not popup_rect.contains(global_pos) and not trigger_rect.contains(global_pos):
                self._hide_popup()
                # Don't consume — let the click reach its intended target.
        elif et == QtCore.QEvent.KeyPress and self._popup.isVisible():
            if event.key() == QtCore.Qt.Key_Escape:
                self._hide_popup()
                return True
        return super().eventFilter(obj, event)

    def hideEvent(self, event: QtGui.QHideEvent) -> None:  # noqa: D401
        # If the whole widget is hidden (e.g. tab switch), also drop the popup.
        self._hide_popup()
        super().hideEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: D401
        self._hide_popup()
        super().closeEvent(event)

    # ------------------------------------------------------------------ #
    # Signal emission (debounced)
    # ------------------------------------------------------------------ #

    def _schedule_emit(self) -> None:
        # QTimer.singleShot-style pattern — restart the 100 ms window every time
        # the checked set might have changed, so rapid clicks collapse into one.
        self._debounce_timer.start(self._DEBOUNCE_MS)

    def _emit_selection_changed(self) -> None:
        current = tuple(self.selected_items())
        if current == self._last_emitted_selection:
            return
        self._last_emitted_selection = current
        self.selectionChanged.emit()

    # ------------------------------------------------------------------ #
    # Summary / trigger label
    # ------------------------------------------------------------------ #

    def _refresh_summary(self) -> None:
        count = len(self.selected_items())
        if count == 0:
            self._count_badge.hide()
            self._summary_label.setText(self._placeholder)
            self._summary_label.setProperty("placeholder", "true")
        else:
            self._count_badge.setText(str(count))
            self._count_badge.show()
            noun = self._noun_singular if count == 1 else self._noun_plural
            self._summary_label.setText("{0} selected".format(noun))
            self._summary_label.setProperty("placeholder", "false")
        # Re-polish so the dynamic QSS property takes effect.
        self._summary_label.style().unpolish(self._summary_label)
        self._summary_label.style().polish(self._summary_label)
