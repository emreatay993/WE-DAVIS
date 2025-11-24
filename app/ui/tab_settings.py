# File: app/ui/tab_settings.py

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QCheckBox, QGroupBox, QLineEdit)
from .. import config_manager
from .. import tooltips

class SettingsTab(QtWidgets.QWidget):
    settings_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Data Processing Group
        data_processing_group = QGroupBox("Data Processing Tools For Time Domain Data (Beta)")
        data_processing_layout = QVBoxLayout()
        self.rolling_min_max_checkbox = QCheckBox("Show Plots as Rolling Min-Max Envelope")
        self.rolling_min_max_checkbox.setToolTip(tooltips.ROLLING_MIN_MAX_ENVELOPE)
        self.plot_as_bars_checkbox = QCheckBox("Plot as Bars")
        self.desired_num_points_input = QLineEdit("50000")
        self.num_points_label = QLabel("Number of Points Shown:")

        # Set dependent widgets to be invisible initially
        self.plot_as_bars_checkbox.setVisible(False)
        self.num_points_label.setVisible(False)
        self.desired_num_points_input.setVisible(False)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.rolling_min_max_checkbox)
        control_layout.addWidget(self.plot_as_bars_checkbox)
        control_layout.addWidget(self.num_points_label)
        control_layout.addWidget(self.desired_num_points_input)
        control_layout.addStretch()
        data_processing_layout.addLayout(control_layout)
        data_processing_group.setLayout(data_processing_layout)

        # Graphical Settings Group
        graphical_settings_group = QGroupBox("Graphical Settings")
        graphical_settings_layout = QVBoxLayout()

        self.legend_font_size_selector = self._create_selector([str(s) for s in range(4, 30)], "10")
        graphical_settings_layout.addLayout(
            self._create_setting_row("Legend Font Size", self.legend_font_size_selector))

        self.default_font_size_selector = self._create_selector([str(s) for s in range(8, 30)], "12")
        graphical_settings_layout.addLayout(
            self._create_setting_row("Default Font Size", self.default_font_size_selector))

        self.hover_font_size_selector = self._create_selector([str(s) for s in range(4, 21)], "15")
        graphical_settings_layout.addLayout(self._create_setting_row("Hover Font Size", self.hover_font_size_selector))

        self.hover_mode_selector = self._create_selector(['closest', 'x', 'y', 'x unified', 'y unified'], 'closest')
        graphical_settings_layout.addLayout(self._create_setting_row("Hover Mode", self.hover_mode_selector))

        # Opacity control for all traces
        self.opacity_spin = QtWidgets.QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.05)
        self.opacity_spin.setDecimals(2)
        self.opacity_spin.setValue(0.75)
        self.opacity_spin.setToolTip("Controls opacity of all traces in all plots. 0.0 = transparent, 1.0 = opaque.")
        graphical_settings_layout.addLayout(self._create_setting_row("Trace Opacity", self.opacity_spin))

        graphical_settings_group.setLayout(graphical_settings_layout)

        # Contact Label
        contact_label = QLabel("Please reach K. Emre Atay for bug reports or feature requests.")

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(data_processing_group)
        main_layout.addWidget(graphical_settings_group)
        main_layout.addStretch()
        main_layout.addWidget(contact_label, alignment=QtCore.Qt.AlignBottom)

        # Styles
        data_processing_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        graphical_settings_group.setStyleSheet(config_manager.GROUPBOX_STYLE)

        # Connections
        self.rolling_min_max_checkbox.stateChanged.connect(self.settings_changed)
        self.rolling_min_max_checkbox.stateChanged.connect(self._on_rolling_min_max_toggled)
        self.plot_as_bars_checkbox.stateChanged.connect(self.settings_changed)
        self.desired_num_points_input.textChanged.connect(self.settings_changed)
        self.legend_font_size_selector.currentIndexChanged.connect(self.settings_changed)
        self.default_font_size_selector.currentIndexChanged.connect(self.settings_changed)
        self.hover_font_size_selector.currentIndexChanged.connect(self.settings_changed)
        self.hover_mode_selector.currentIndexChanged.connect(self.settings_changed)
        self.opacity_spin.valueChanged.connect(self.settings_changed)

    def _create_selector(self, items, default):
        selector = QComboBox()
        selector.addItems(items)
        selector.setCurrentText(default)
        return selector

    def _create_setting_row(self, label_text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        return layout

    # Slot to control visibility of dependent widgets
    @QtCore.pyqtSlot(int)
    def _on_rolling_min_max_toggled(self, state):
        is_checked = (state == QtCore.Qt.Checked)
        self.plot_as_bars_checkbox.setVisible(is_checked)
        self.num_points_label.setVisible(is_checked)
        self.desired_num_points_input.setVisible(is_checked)