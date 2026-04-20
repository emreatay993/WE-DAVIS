# File: app/ui/tab_interface_data.py

import re
from natsort import natsorted
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QSizePolicy
from ..plotting.plotter import load_fig_to_webview
from .widgets.checkable_combo_box import CheckableComboBox


class InterfaceDataTab(QtWidgets.QWidget):
    plot_parameters_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.df = None  # Holding a reference to the main frame
        self._setup_ui()

    def set_dataframe(self, df):
        """MainWindow provides the dataframe to this tab."""
        self.df = df

    def refresh_selectors(self, preserve_selection=True):
        """Rebuild interface and side selectors from the current dataframe."""
        if self.df is None:
            self.interface_selector.set_items([], preserve_selection=False)
            self.side_selector.set_grouped_items([], preserve_selection=False)
            return

        interfaces = self._extract_interfaces()
        self.interface_selector.set_items(
            interfaces,
            preserve_selection=preserve_selection,
        )
        self._rebuild_side_selector_from_checked_interfaces()

    def selected_interfaces(self):
        """Return the list of currently-checked interface IDs."""
        return self.interface_selector.selected_items()

    def selected_sides(self):
        """Return the list of currently-checked part sides."""
        return self.side_selector.selected_items()

    def selected_interface_side_pairs(self):
        """Return the checked ``(interface, side)`` pairs from the grouped selector."""
        return [
            (interface_name, side_name)
            for interface_name, side_name in self.side_selector.selected_grouped_items()
            if interface_name
        ]

    def _setup_ui(self):
        # Widgets
        self.interface_selector = CheckableComboBox()
        self.interface_selector.set_noun("interface", "interfaces")
        self.interface_selector.set_placeholder("Select interfaces…")

        self.side_selector = CheckableComboBox()
        self.side_selector.set_noun("part side", "part sides")
        self.side_selector.set_placeholder("Select part sides…")

        self.t_series_plot = QtWebEngineWidgets.QWebEngineView()
        self.t_series_plot.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.r_series_plot = QtWebEngineWidgets.QWebEngineView()
        self.r_series_plot.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        splitter = QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.t_series_plot)
        splitter.addWidget(self.r_series_plot)

        # Layouts
        side_layout = QHBoxLayout()
        side_selection_label = QLabel("Part Side Filter")
        side_selection_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        side_layout.addWidget(side_selection_label)
        side_layout.addWidget(self.side_selector)

        main_layout = QVBoxLayout(self)
        interface_selection_label = QLabel("Interface")
        main_layout.addWidget(interface_selection_label)
        main_layout.addWidget(self.interface_selector)
        main_layout.addLayout(side_layout)
        main_layout.addWidget(splitter)

        # Connections
        self.interface_selector.selectionChanged.connect(self._on_interfaces_changed)
        self.side_selector.selectionChanged.connect(self.plot_parameters_changed)

    # Private slots for internal logic
    def _on_interfaces_changed(self):
        self._rebuild_side_selector_from_checked_interfaces()
        self.plot_parameters_changed.emit()

    def _rebuild_side_selector_from_checked_interfaces(self):
        """Rebuild the grouped side selector from the checked interfaces.

        Each checked interface becomes a group header followed by its sides;
        any previously-checked sides that still exist under a still-checked
        interface stay checked (preserve_selection=True).
        """
        checked_interfaces = self.interface_selector.selected_items()
        groups = [
            (iface, self._get_sides_for_interface(iface))
            for iface in checked_interfaces
        ]
        self.side_selector.set_grouped_items(groups, preserve_selection=True)

    # Helper methods
    def _extract_interfaces(self):
        return natsorted(
            list(
                {
                    match.group(0)
                    for col in self.df.columns
                    if (match := re.match(r'I\d+[A-Za-z]?', col.split(' ')[0]))
                }
            )
        )

    def _get_sides_for_interface(self, interface_name):
        if self.df is None or not interface_name:
            return []

        pattern = re.compile(r'I\d+[a-zA-Z]?\s*-\s*(.*?)(?=\s*\()')
        relevant_cols = [
            col for col in self.df.columns
            if re.match(rf"^{re.escape(interface_name)}(?=\D)", col)
        ]
        return sorted(
            {
                match.group(1).strip()
                for col in relevant_cols
                if (match := pattern.search(col))
            }
        )

    def display_t_series_plot(self, fig):
        load_fig_to_webview(fig, self.t_series_plot)

    def display_r_series_plot(self, fig):
        load_fig_to_webview(fig, self.r_series_plot)
