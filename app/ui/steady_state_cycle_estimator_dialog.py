import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
)

from .. import config_manager
from ..analysis.steady_state_estimator import (
    build_estimate_table,
    estimate_cycles_to_steady_state,
)


HELP_HTML = """
<html>
<head>
<style>
body {
    font-family: "Segoe UI", Arial, sans-serif;
    line-height: 1.45;
}
h1, h2 {
    color: #1f1f1f;
}
.eq {
    margin: 10px 0 14px 0;
    padding: 10px 14px;
    background: #f7f7f7;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 15px;
}
.small-eq {
    font-size: 14px;
}
.defs {
    margin: 6px 0 14px 18px;
}
.defs li {
    margin: 3px 0;
}
table {
    border-collapse: collapse;
    margin: 10px 0 14px 0;
}
th, td {
    border: 1px solid #d9d9d9;
    padding: 6px 10px;
    text-align: left;
}
th {
    background: #f2f2f2;
}
</style>
</head>
<body>
<h1>Transient Steady-State Cycle Estimator</h1>

<h2>Short answer</h2>
<ul>
  <li>A mode-superposition harmonic analysis returns the <b>steady-state</b> response at the driving frequency.</li>
  <li>A mode-superposition transient analysis with the <b>same linear model</b>, <b>same modal basis</b>, <b>same damping</b>, and the <b>same continuous sinusoidal load</b> converges to the same steady-state sinusoid after the startup transient decays.</li>
  <li>The <b>absolute maximum over the full transient history</b> is not guaranteed to equal the harmonic peak because startup transients, phase effects, and slight detuning can temporarily shift the time-history maximum.</li>
</ul>

<h2>Dominant-Mode Model Used Here</h2>
<p>For one dominant mode, the modal coordinate is modeled as:</p>
<div class="eq">
  q&#776; + 2&zeta;&omega;<sub>n</sub>q&#775; + &omega;<sub>n</sub><sup>2</sup>q = p<sub>0</sub> cos(&omega;t)
</div>
<ul class="defs">
  <li><i>q</i> = modal coordinate or modal response for the dominant mode</li>
  <li>q&#775; = first time derivative of <i>q</i></li>
  <li>q&#776; = second time derivative of <i>q</i></li>
  <li>&zeta; = damping ratio</li>
  <li>&omega;<sub>n</sub> = dominant natural circular frequency in rad/s</li>
  <li><i>p</i><sub>0</sub> = modal forcing amplitude</li>
  <li>&omega; = excitation circular frequency in rad/s</li>
  <li><i>t</i> = time</li>
</ul>

<p>The total response is the sum of a steady-state term and a decaying transient term:</p>
<div class="eq">
  q(t) = q<sub>ss</sub>(t) + q<sub>tr</sub>(t)<br>
  q<sub>tr</sub>(t) &sim; exp(-&zeta;&omega;<sub>n</sub>t)
</div>
<ul class="defs">
  <li>q<sub>ss</sub>(t) = steady-state part of the response</li>
  <li>q<sub>tr</sub>(t) = startup transient part of the response</li>
</ul>

<p>That exponential envelope is the basis of this estimator.</p>

<h2>Estimator</h2>
<p>Choose a residual transient fraction <i>r</i>.</p>
<ul>
  <li><code>r = 0.01</code> means <b>1% of the startup transient envelope remains</b></li>
  <li>equivalently, the response is about <b>99% settled</b> to the steady-state limit</li>
</ul>

<p>The required run time is estimated from:</p>
<div class="eq">
  t<sub>required</sub> = ln(1 / r) / (&zeta;&omega;<sub>n</sub>)
</div>
<ul class="defs">
  <li>t<sub>required</sub> = estimated run time needed to reduce the startup transient to the chosen residual level</li>
  <li><i>r</i> = residual transient fraction still allowed at the end of the run</li>
  <li>&zeta; = damping ratio</li>
  <li>&omega;<sub>n</sub> = dominant natural circular frequency in rad/s</li>
</ul>

<p>The corresponding number of excitation cycles is:</p>
<div class="eq">
  N<sub>cycles</sub> = f<sub>exc</sub> t<sub>required</sub><br>
  N<sub>cycles</sub> = [&omega; / (2&pi;&zeta;&omega;<sub>n</sub>)] ln(1 / r)
</div>
<ul class="defs">
  <li>N<sub>cycles</sub> = estimated number of forcing cycles required to reach the chosen settling level</li>
  <li>f<sub>exc</sub> = excitation frequency in Hz</li>
  <li>t<sub>required</sub> = estimated run time</li>
  <li>&omega; = excitation circular frequency in rad/s</li>
  <li>&zeta; = damping ratio</li>
  <li>&omega;<sub>n</sub> = dominant natural circular frequency in rad/s</li>
  <li><i>r</i> = residual transient fraction</li>
</ul>

<p>If you run the transient at the same dominant resonant frequency identified from harmonic analysis:</p>
<div class="eq">
  &omega; &asymp; &omega;<sub>n</sub><br>
  N<sub>cycles</sub> &asymp; ln(1 / r) / (2&pi;&zeta;)
</div>

<p>At exact resonance, the cycle count therefore depends mainly on damping. The selected frequency changes the required <b>time</b>, not much the required <b>cycle count</b>.</p>

<h2>Practical Reference Values at Exact Resonance</h2>
<ul>
  <li>5% residual transient: <code>N &asymp; 0.477 / &zeta;</code></li>
  <li>1% residual transient: <code>N &asymp; 0.733 / &zeta;</code></li>
  <li>0.1% residual transient: <code>N &asymp; 1.099 / &zeta;</code></li>
</ul>

<h2>Several Nearby Resonant Modes</h2>
<p>If several modes contribute near the excitation frequency, a conservative estimate is based on the slowest modal decay rate:</p>
<div class="eq small-eq">
  t<sub>required</sub> &asymp; max<sub>i</sub> [ln(1 / r) / (&zeta;<sub>i</sub>&omega;<sub>n,i</sub>)]
</div>
<ul class="defs">
  <li><i>i</i> = mode index</li>
  <li>&zeta;<sub>i</sub> = damping ratio of mode <i>i</i></li>
  <li>&omega;<sub>n,i</sub> = natural circular frequency of mode <i>i</i></li>
  <li>max<sub>i</sub> means use the slowest-decaying contributing mode as the conservative settling estimate</li>
</ul>

<p>This dialog is intended for the common case you described: a transient run driven at a known dominant resonant frequency from the harmonic study.</p>

<h2>Interpretation</h2>
<ul>
  <li><b>Harmonic result</b>: steady-state amplitude at the selected frequency</li>
  <li><b>Transient result after settling</b>: should match the harmonic amplitude within numerical tolerance</li>
  <li><b>Transient maximum over all time</b>: can be slightly lower or higher before settling</li>
</ul>

<h2>References</h2>
<ol>
  <li><a href="https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/wb2_help/wb2h_harmrespAN.html">ANSYS Help: Harmonic Response</a></li>
  <li><a href="https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_str/Hlp_G_STR5_10.html">ANSYS Help: Mode-Superposition Transient Dynamic Analysis</a></li>
  <li><a href="https://eng.libretexts.org/Bookshelves/Mechanical_Engineering/Introductory_Dynamics%3A_2D_Kinematics_and_Kinetics_of_Point_Masses_and_Rigid_Bodies_%28Steeneken%29/04%3A_Vibrations_and_Strategy/13%3A_Vibrations/13.04%3A_Forced_vibrations">Engineering LibreTexts: Forced Vibrations</a></li>
  <li><a href="https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/782069da3820fc514c10c26ae0c15b01_MIT8_03SCF16_Text_Ch2.pdf">MIT OpenCourseWare: Forced Oscillation and Resonance</a></li>
</ol>
</body>
</html>
"""

INTRO_TOOLTIP = (
    "This tool estimates how many sinusoidal transient cycles you should run before the "
    "startup transient becomes small enough that the response is effectively in steady state."
)
ZETA_TOOLTIP = (
    "Modal damping ratio used for the estimate. Example: 0.02 means 2% damping. "
    "Higher damping reaches steady state in fewer cycles."
)
EXCITATION_FREQUENCY_TOOLTIP = (
    "Driving frequency of the transient load in Hz. This sets the physical run time. "
    "If you are running at resonance, this is usually the dominant resonant frequency."
)
ASSUME_RESONANCE_TOOLTIP = (
    "Turn this on when the transient is run at the same dominant resonant frequency found from "
    "harmonic analysis. Then the excitation frequency and mode frequency are treated as the same."
)
MODE_FREQUENCY_TOOLTIP = (
    "Dominant participating mode frequency in Hz. Only edit this when the transient excitation "
    "frequency is not exactly the same as the dominant mode frequency."
)
RESIDUAL_PERCENT_TOOLTIP = (
    "How much of the startup transient you are willing to leave at the end of the run. "
    "1% is a common starting point. Smaller values require more cycles."
)
SUMMARY_TOOLTIP = (
    "Quick interpretation of the estimate. Focus on the recommended whole-cycle count and run time. "
    "For comparison with harmonic analysis, use the final settled cycle rather than the maximum over the full startup history."
)
THRESHOLD_TABLE_TOOLTIP = (
    "Reference settling levels for the same inputs. Each row shows the estimated cycles and run time "
    "needed to reduce the startup transient to that remaining percentage."
)
DOCS_TOOLTIP = (
    "Background notes, assumptions, formulas, caveats, and source references for the estimator."
)


class SteadyStateCycleEstimatorDialog(QDialog):
    def __init__(
        self,
        parent=None,
        initial_excitation_frequency_hz: float = 1.0,
        initial_mode_frequency_hz: float | None = None,
    ):
        super().__init__(parent)
        self._initial_excitation_frequency_hz = max(float(initial_excitation_frequency_hz), 1e-6)
        if initial_mode_frequency_hz is None:
            initial_mode_frequency_hz = self._initial_excitation_frequency_hz
        self._initial_mode_frequency_hz = max(float(initial_mode_frequency_hz), 1e-6)
        self._setup_ui()
        self._update_results()

    def _setup_ui(self):
        self.setWindowTitle("Transient Steady-State Cycle Estimator")
        self.resize(920, 700)

        tabs = QTabWidget(self)
        tabs.addTab(self._build_estimator_tab(), "Estimator")
        tabs.addTab(self._build_help_tab(), "Docs / Help")
        tabs.setToolTip("Switch between the calculator and the background notes.")

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setToolTip("Close this estimator window.")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tabs)
        main_layout.addLayout(button_layout)

    def _build_estimator_tab(self):
        page = QtWidgets.QWidget(self)
        layout = QVBoxLayout(page)

        intro_label = QLabel(
            "Estimate how many sinusoidal transient cycles are needed for the startup transient "
            "envelope to decay below a chosen residual level."
        )
        intro_label.setWordWrap(True)
        intro_label.setToolTip(INTRO_TOOLTIP)
        layout.addWidget(intro_label)

        input_group = QGroupBox("Inputs")
        input_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        input_layout = QFormLayout(input_group)

        self.damping_ratio_spin = QDoubleSpinBox()
        self.damping_ratio_spin.setDecimals(5)
        self.damping_ratio_spin.setRange(0.00001, 0.99999)
        self.damping_ratio_spin.setSingleStep(0.001)
        self.damping_ratio_spin.setValue(0.02)
        self.damping_ratio_spin.setToolTip(ZETA_TOOLTIP)
        input_layout.addRow("Damping ratio, zeta", self.damping_ratio_spin)

        self.excitation_frequency_spin = QDoubleSpinBox()
        self.excitation_frequency_spin.setDecimals(5)
        self.excitation_frequency_spin.setRange(0.00001, 1_000_000.0)
        self.excitation_frequency_spin.setSingleStep(1.0)
        self.excitation_frequency_spin.setValue(self._initial_excitation_frequency_hz)
        self.excitation_frequency_spin.setToolTip(EXCITATION_FREQUENCY_TOOLTIP)
        input_layout.addRow("Excitation frequency [Hz]", self.excitation_frequency_spin)

        self.assume_resonance_checkbox = QCheckBox("Assume excitation is applied at the dominant resonance")
        self.assume_resonance_checkbox.setChecked(True)
        self.assume_resonance_checkbox.setToolTip(ASSUME_RESONANCE_TOOLTIP)
        input_layout.addRow("", self.assume_resonance_checkbox)

        self.mode_frequency_spin = QDoubleSpinBox()
        self.mode_frequency_spin.setDecimals(5)
        self.mode_frequency_spin.setRange(0.00001, 1_000_000.0)
        self.mode_frequency_spin.setSingleStep(1.0)
        self.mode_frequency_spin.setValue(self._initial_mode_frequency_hz)
        self.mode_frequency_spin.setToolTip(MODE_FREQUENCY_TOOLTIP)
        input_layout.addRow("Dominant mode frequency [Hz]", self.mode_frequency_spin)

        self.residual_percent_spin = QDoubleSpinBox()
        self.residual_percent_spin.setDecimals(3)
        self.residual_percent_spin.setRange(0.001, 50.0)
        self.residual_percent_spin.setSingleStep(0.1)
        self.residual_percent_spin.setValue(1.0)
        self.residual_percent_spin.setToolTip(RESIDUAL_PERCENT_TOOLTIP)
        input_layout.addRow("Residual transient allowed [%]", self.residual_percent_spin)

        residual_note = QLabel(
            "Example: 1.0% residual transient means the startup transient envelope has decayed "
            "to 1% of its initial level."
        )
        residual_note.setWordWrap(True)
        residual_note.setToolTip(RESIDUAL_PERCENT_TOOLTIP)
        input_layout.addRow("", residual_note)

        result_group = QGroupBox("Results")
        result_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        result_layout = QVBoxLayout(result_group)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.summary_label.setToolTip(SUMMARY_TOOLTIP)
        result_layout.addWidget(self.summary_label)

        self.threshold_table = QTableWidget(0, 4)
        self.threshold_table.setHorizontalHeaderLabels(
            ["Residual transient", "Approx. settled", "Cycles", "Time [s]"]
        )
        self.threshold_table.setToolTip(THRESHOLD_TABLE_TOOLTIP)
        self.threshold_table.verticalHeader().setVisible(False)
        self.threshold_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.threshold_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.threshold_table.horizontalHeader().setStretchLastSection(True)
        self.threshold_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.threshold_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.threshold_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.threshold_table.horizontalHeaderItem(0).setToolTip("Remaining startup transient at the end of the run.")
        self.threshold_table.horizontalHeaderItem(1).setToolTip("Approximate settled fraction of the response.")
        self.threshold_table.horizontalHeaderItem(2).setToolTip("Estimated forcing cycles needed for that settling level.")
        self.threshold_table.horizontalHeaderItem(3).setToolTip("Estimated physical run time for that settling level.")
        result_layout.addWidget(self.threshold_table)

        layout.addWidget(input_group)
        layout.addWidget(result_group)
        layout.addStretch()

        self.assume_resonance_checkbox.toggled.connect(self._on_assume_resonance_toggled)
        self.excitation_frequency_spin.valueChanged.connect(self._sync_mode_frequency_to_excitation)
        self.damping_ratio_spin.valueChanged.connect(self._update_results)
        self.excitation_frequency_spin.valueChanged.connect(self._update_results)
        self.mode_frequency_spin.valueChanged.connect(self._update_results)
        self.residual_percent_spin.valueChanged.connect(self._update_results)
        self.assume_resonance_checkbox.toggled.connect(self._update_results)

        self._on_assume_resonance_toggled(self.assume_resonance_checkbox.isChecked())
        return page

    def _build_help_tab(self):
        page = QtWidgets.QWidget(self)
        layout = QVBoxLayout(page)

        help_browser = QTextBrowser()
        help_browser.setOpenExternalLinks(True)
        help_browser.setToolTip(DOCS_TOOLTIP)
        help_browser.setHtml(HELP_HTML)

        layout.addWidget(help_browser)
        return page

    @QtCore.pyqtSlot(bool)
    def _on_assume_resonance_toggled(self, checked: bool):
        self.mode_frequency_spin.setEnabled(not checked)
        if checked:
            self._sync_mode_frequency_to_excitation()

    @QtCore.pyqtSlot()
    def _sync_mode_frequency_to_excitation(self):
        if not self.assume_resonance_checkbox.isChecked():
            return
        self.mode_frequency_spin.blockSignals(True)
        self.mode_frequency_spin.setValue(self.excitation_frequency_spin.value())
        self.mode_frequency_spin.blockSignals(False)

    @QtCore.pyqtSlot()
    def _update_results(self):
        try:
            excitation_frequency_hz = self.excitation_frequency_spin.value()
            mode_frequency_hz = (
                excitation_frequency_hz
                if self.assume_resonance_checkbox.isChecked()
                else self.mode_frequency_spin.value()
            )
            estimate = estimate_cycles_to_steady_state(
                damping_ratio=self.damping_ratio_spin.value(),
                excitation_frequency_hz=excitation_frequency_hz,
                mode_frequency_hz=mode_frequency_hz,
                residual_fraction=self.residual_percent_spin.value() / 100.0,
            )
        except ValueError as exc:
            self.summary_label.setText(f"Input error: {exc}")
            self.threshold_table.setRowCount(0)
            return

        exact_resonance = np.isclose(excitation_frequency_hz, mode_frequency_hz, rtol=1e-6, atol=1e-12)
        resonance_note = (
            "Using the exact-resonance simplification."
            if exact_resonance
            else "Using the general cycle estimate with separate excitation and mode frequencies."
        )
        self.summary_label.setText(
            "<b>Steady-state limit:</b> for the same linear MSUP model and sinusoidal load, the harmonic "
            "result is the steady-state limit of the transient response.<br><br>"
            f"<b>Requested settling:</b> {estimate.settled_fraction * 100.0:.3f}% settled "
            f"({estimate.residual_fraction * 100.0:.3f}% residual transient).<br>"
            f"<b>Estimated cycles:</b> {estimate.estimated_cycles:.3f}<br>"
            f"<b>Recommended minimum whole cycles:</b> {estimate.rounded_cycle_count}<br>"
            f"<b>Estimated run time:</b> {estimate.estimated_time_s:.6g} s<br>"
            f"<b>Transient envelope time constant:</b> {estimate.time_constant_s:.6g} s<br>"
            f"<b>Mode decay rate:</b> {estimate.decay_rate_per_s:.6g} 1/s<br><br>"
            f"{resonance_note}"
        )

        table_estimates = build_estimate_table(
            damping_ratio=self.damping_ratio_spin.value(),
            excitation_frequency_hz=excitation_frequency_hz,
            mode_frequency_hz=mode_frequency_hz,
        )
        self.threshold_table.setRowCount(len(table_estimates))
        for row, row_estimate in enumerate(table_estimates):
            values = [
                f"{row_estimate.residual_fraction * 100.0:.3f}%",
                f"{row_estimate.settled_fraction * 100.0:.3f}%",
                f"{row_estimate.estimated_cycles:.3f}",
                f"{row_estimate.estimated_time_s:.6g}",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.threshold_table.setItem(row, column, item)

        self.threshold_table.resizeRowsToContents()
