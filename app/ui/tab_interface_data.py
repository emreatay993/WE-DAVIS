# File: app/ui/tab_interface_data.py

import re
from natsort import natsorted
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSplitter, QComboBox, QLabel, QSizePolicy
from ..plotting.plotter import load_fig_to_webview

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
            self._set_combo_items(self.interface_selector, [], "")
            self._set_combo_items(self.side_selector, [], "")
            return

        previous_interface = self.interface_selector.currentText() if preserve_selection else ""
        previous_side = self.side_selector.currentText() if preserve_selection else ""

        interfaces = self._extract_interfaces()
        selected_interface = self._set_combo_items(
            self.interface_selector,
            interfaces,
            previous_interface,
        )

        sides = self._get_sides_for_interface(selected_interface)
        self._set_combo_items(self.side_selector, sides, previous_side)

    def _setup_ui(self):
        # Widgets
        self.interface_selector = QComboBox()
        self.interface_selector.setEditable(True)
        self.side_selector = QComboBox()
        self.side_selector.setEditable(True)
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
        self.interface_selector.currentIndexChanged.connect(self._on_interface_changed)
        self.side_selector.currentIndexChanged.connect(self.plot_parameters_changed)

    # Private slots for internal logic
    def _on_interface_changed(self):
        self._populate_side_selector()
        self.plot_parameters_changed.emit()

    # Helper methods to call
    def _populate_side_selector(self):
        current_interface = self.interface_selector.currentText()
        current_side = self.side_selector.currentText()
        sides = self._get_sides_for_interface(current_interface)
        self._set_combo_items(self.side_selector, sides, current_side)

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

    @staticmethod
    def _set_combo_items(combo_box, items, selected_text):
        combo_box.blockSignals(True)
        combo_box.clear()
        combo_box.addItems(items)

        if items:
            target_text = selected_text if selected_text in items else items[0]
            combo_box.setCurrentIndex(combo_box.findText(target_text))

        combo_box.blockSignals(False)
        return combo_box.currentText()

    def display_t_series_plot(self, fig):
        load_fig_to_webview(fig, self.t_series_plot)

    def display_r_series_plot(self, fig):

        load_fig_to_webview(fig, self.r_series_plot)
