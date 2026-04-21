#!/usr/bin/env python3
"""
Resonance Steady-State Cycle Estimator for MSUP transient analyses.

Use when the transient excitation frequency is the dominant resonant
frequency found from a harmonic/MSUP harmonic analysis.

Requirements:
    pip install PyQt5 numpy

Run:
    python resonance_steady_state_cycles_gui.py
"""

from __future__ import annotations

import html
import math
import sys
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets


APP_TITLE = "Resonant MSUP Transient Cycle Estimator"


DOCS_HTML = """
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
.defs {
    margin: 6px 0 14px 18px;
}
.defs li {
    margin: 3px 0;
}
</style>
</head>
<body>
<h1>Resonant MSUP Transient Cycle Estimator</h1>

<p>Use this tool when the transient analysis is run at a <b>dominant resonant frequency</b> identified from a harmonic/MSUP harmonic analysis.</p>

<h2>What Changes in the Resonance Case?</h2>
<p>The general settling estimate is:</p>
<div class="eq">
  N<sub>ss</sub> = (f<sub>exc</sub> / f<sub>n</sub>) [-ln(&epsilon;)] / (2&pi;&zeta;)
</div>
<ul class="defs">
  <li><i>N</i><sub>ss</sub> = forcing cycles required for the homogeneous transient to decay to the tolerance</li>
  <li><i>f</i><sub>exc</sub> = transient excitation frequency</li>
  <li><i>f</i><sub>n</sub> = dominant participating natural or resonant frequency</li>
  <li>&zeta; = damping ratio</li>
  <li>&epsilon; = acceptable remaining transient fraction</li>
</ul>

<p>If you run the transient <b>at the dominant resonance</b>, then:</p>
<div class="eq">
  f<sub>exc</sub> = f<sub>n</sub>
</div>

<p>so the estimate simplifies to:</p>
<div class="eq">
  N<sub>ss</sub> &asymp; [-ln(&epsilon;)] / (2&pi;&zeta;)
</div>
<ul class="defs">
  <li>N<sub>ss</sub> = estimated settling cycles at resonance before any safety factor is applied</li>
  <li>&epsilon; = acceptable remaining transient fraction</li>
  <li>&zeta; = damping ratio</li>
</ul>

<p>The required <b>number of cycles</b> is therefore controlled mainly by damping ratio and tolerance. The resonant frequency still matters for the <b>physical time duration</b>:</p>
<div class="eq">
  t<sub>run</sub> = N<sub>run</sub> / f<sub>res</sub>
</div>
<ul class="defs">
  <li>t<sub>run</sub> = physical transient duration in seconds</li>
  <li>N<sub>run</sub> = total cycles you decide to run, including any safety margin and extra post-settling cycles</li>
  <li>f<sub>res</sub> = resonant frequency in Hz used for the transient run</li>
</ul>

<h2>Why This Works</h2>
<p>For a modal coordinate in an underdamped linear MSUP model:</p>
<div class="eq">
  q&#776; + 2&zeta;&omega;<sub>n</sub>q&#775; + &omega;<sub>n</sub><sup>2</sup>q = p(t)
</div>
<ul class="defs">
  <li><i>q</i> = modal coordinate or modal response</li>
  <li>q&#775; = first time derivative of <i>q</i></li>
  <li>q&#776; = second time derivative of <i>q</i></li>
  <li>&zeta; = damping ratio</li>
  <li>&omega;<sub>n</sub> = natural circular frequency in rad/s</li>
  <li><i>p</i>(t) = applied modal forcing as a function of time</li>
</ul>

<p>The transient response under a harmonic load can be written as:</p>
<div class="eq">
  q(t) = q<sub>ss</sub>(t) + q<sub>tr</sub>(t)
</div>
<ul class="defs">
  <li>q<sub>ss</sub>(t) = steady-state part of the response</li>
  <li>q<sub>tr</sub>(t) = decaying transient part of the response</li>
</ul>

<p>with the homogeneous transient envelope decaying as:</p>
<div class="eq">
  q<sub>tr</sub>(t) &sim; e<sup>-&zeta;&omega;<sub>n</sub>t</sup>
</div>
<ul class="defs">
  <li><i>t</i> = time</li>
  <li>&zeta;&omega;<sub>n</sub> = exponential decay rate of the modal transient envelope</li>
</ul>

<p>At resonance, one forcing period is approximately one modal period, so after <i>N</i> forcing cycles:</p>
<div class="eq">
  |q<sub>tr</sub>(N)| / |q<sub>tr</sub>(0)| &asymp; e<sup>-2&pi;&zeta;N</sup>
</div>
<ul class="defs">
  <li><i>N</i> = number of forcing cycles elapsed</li>
  <li>|q<sub>tr</sub>(N)| / |q<sub>tr</sub>(0)| = remaining fraction of the transient envelope after <i>N</i> cycles</li>
  <li>&zeta; = damping ratio</li>
</ul>

<p>Setting this equal to &epsilon; gives the resonance formula above.</p>

<h2>Examples</h2>
<p>At resonance:</p>
<table>
  <tr><th>Damping ratio</th><th>5% remaining</th><th>1% remaining</th><th>0.1% remaining</th></tr>
  <tr><td>0.5%</td><td>95.4 cycles</td><td>146.6 cycles</td><td>219.9 cycles</td></tr>
  <tr><td>1%</td><td>47.7 cycles</td><td>73.3 cycles</td><td>109.9 cycles</td></tr>
  <tr><td>2%</td><td>23.8 cycles</td><td>36.6 cycles</td><td>55.0 cycles</td></tr>
  <tr><td>5%</td><td>9.5 cycles</td><td>14.7 cycles</td><td>22.0 cycles</td></tr>
</table>

<p>A safety factor is recommended because real FE post-processing quantities may combine several modes, phases, and recovered stresses.</p>

<h2>How to Compare with Harmonic Response</h2>
<p>For a linear model with the same modal basis, load amplitude, phase convention, damping model, and boundary conditions, the final steady-state transient cycle should match the harmonic response at the same frequency.</p>

<p>Do <b>not</b> compare the harmonic amplitude with the maximum over the entire transient history. The early transient part may add to or subtract from the periodic steady-state response. Compare against the peak from the final complete cycle, or several final complete cycles.</p>

<p>For vector or stress results, compare the same definition used in harmonic post-processing. A harmonic component amplitude is not always the same as an instantaneous vector magnitude or a von Mises stress maximum unless the postprocessor performs the equivalent phase sweep.</p>

<h2>Practical Recommendations</h2>
<ol>
  <li>Use the harmonic peak frequency or the actual mode frequency as <i>f</i><sub>res</sub>.</li>
  <li>Use &epsilon; = 1% as a reasonable starting point.</li>
  <li>Use a safety factor between 1.1 and 1.5.</li>
  <li>Add at least one complete post-settling cycle for peak extraction.</li>
  <li>Verify by plotting peak-per-cycle convergence in the transient result.</li>
  <li>Use enough time points per cycle. This tool suggests a forcing-cycle-based interval, but your solver may require a smaller step to resolve high retained modes, contact status output, stress recovery, or integration accuracy.</li>
</ol>

<h2>Limitations</h2>
<p>This estimate assumes:</p>
<ul>
  <li>linear dynamics</li>
  <li>underdamped modal damping</li>
  <li>a single-frequency sinusoidal load</li>
  <li>no nonlinear contacts, plasticity, or frictional status changes</li>
  <li>no load ramp unless the settling cycles are counted after the ramp</li>
  <li>consistent damping definition between harmonic and transient analyses</li>
</ul>

<h2>References</h2>
<ul>
  <li>Ansys Innovation Courses, <i>Performing Mode Superposition Harmonic Analysis</i></li>
  <li>Ansys Innovation Courses, <i>Summary</i></li>
  <li>Bentley STAAD.Pro Help, <i>Steady State and Harmonic Response</i></li>
  <li>University of Alberta Engineering, <i>Steady State Harmonic Response</i></li>
</ul>
</body>
</html>
"""

INFO_TOOLTIP = (
    "This version assumes each transient run is performed at a dominant resonant frequency from harmonic analysis, "
    "so the settling estimate is expressed mainly in cycles versus damping."
)
DEFAULT_ZETA_TOOLTIP = (
    "Default damping ratio used for any row that does not have its own override. "
    "Example: 0.02 means 2% damping."
)
EPSILON_TOOLTIP = (
    "Allowed remaining startup transient after the run. "
    "1% is a common starting point. Smaller values mean longer runs."
)
SAFETY_FACTOR_TOOLTIP = (
    "Extra margin applied to the theoretical settling cycle count. "
    "Use this to be conservative when several modes or recovered stresses may slow visible convergence."
)
EXTRA_CYCLES_TOOLTIP = (
    "Additional full cycles added after settling so you still have complete steady-state cycles available for peak extraction."
)
STEPS_PER_CYCLE_TOOLTIP = (
    "Suggested number of time points per forcing cycle. "
    "This helps translate cycle count into a rough time-step suggestion."
)
FREQUENCY_TABLE_TOOLTIP = (
    "Enter one resonant frequency per row. The second column lets you override damping for that specific row."
)
FREQ_COLUMN_TOOLTIP = (
    "Dominant resonant frequency for that transient run. This affects run time and suggested time step."
)
ZETA_OVERRIDE_TOOLTIP = (
    "Optional damping ratio just for this row. Leave blank to use the default damping ratio above."
)
RESULTS_TOOLTIP = (
    "Calculated settling cycles, run time, suggested time step, and remaining transient after the chosen run length."
)
NOTE_TOOLTIP = (
    "Plain-language reminder for how to compare transient and harmonic results."
)


@dataclass
class RowResult:
    row: int
    frequency_hz: float
    zeta: float
    base_cycles: float
    safe_cycles: float
    rounded_settling_cycles: int
    run_cycles: int
    run_time_s: float
    dt_s: float
    n_points: int
    residual_after_run: float


def parse_ratio(text: str, field_name: str) -> float:
    raw = text.strip().lower()
    if not raw:
        raise ValueError(f"{field_name} is blank.")
    percent = raw.endswith("%") or "percent" in raw or "pct" in raw
    raw = raw.replace("%", "").replace("percent", "").replace("pct", "").strip()
    if "," in raw and "." not in raw:
        raw = raw.replace(",", ".")
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be numeric; examples: 0.02 or 2%.") from exc
    if percent:
        value /= 100.0
    return value


def parse_float(text: str, field_name: str) -> float:
    raw = text.strip()
    if not raw:
        raise ValueError(f"{field_name} is blank.")
    if "," in raw and "." not in raw:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be numeric.") from exc


def estimate_row(
    row: int,
    frequency_hz: float,
    zeta: float,
    eps_fraction: float,
    safety_factor: float,
    extra_cycles: int,
    steps_per_cycle: int,
) -> RowResult:
    if frequency_hz <= 0.0:
        raise ValueError(f"Row {row}: resonant frequency must be greater than zero.")
    if not (0.0 < zeta < 1.0):
        raise ValueError(f"Row {row}: damping ratio ζ must satisfy 0 < ζ < 1 for this estimator.")
    if not (0.0 < eps_fraction < 1.0):
        raise ValueError("Tolerance must be between 0 and 100 percent.")
    if safety_factor < 1.0:
        raise ValueError("Safety factor must be at least 1.0.")
    if extra_cycles < 0:
        raise ValueError("Extra post-settling cycles cannot be negative.")
    if steps_per_cycle < 4:
        raise ValueError("Steps per cycle should be at least 4.")

    base_cycles = -math.log(eps_fraction) / (2.0 * math.pi * zeta)
    safe_cycles = safety_factor * base_cycles
    rounded_settling_cycles = int(math.ceil(safe_cycles))
    run_cycles = max(1, rounded_settling_cycles + extra_cycles)
    run_time_s = run_cycles / frequency_hz
    dt_s = 1.0 / (steps_per_cycle * frequency_hz)
    n_points = run_cycles * steps_per_cycle + 1
    residual_after_run = math.exp(-2.0 * math.pi * zeta * run_cycles)

    return RowResult(
        row=row,
        frequency_hz=frequency_hz,
        zeta=zeta,
        base_cycles=base_cycles,
        safe_cycles=safe_cycles,
        rounded_settling_cycles=rounded_settling_cycles,
        run_cycles=run_cycles,
        run_time_s=run_time_s,
        dt_s=dt_s,
        n_points=n_points,
        residual_after_run=residual_after_run,
    )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1050, 740)

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.estimator_tab = QtWidgets.QWidget()
        self.docs_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.estimator_tab, "Estimator")
        self.tabs.addTab(self.docs_tab, "Docs / Help")

        self._build_estimator_tab()
        self._build_docs_tab()
        self._connect_signals()
        self.calculate()

    def _build_estimator_tab(self) -> None:
        root = QtWidgets.QVBoxLayout(self.estimator_tab)

        info = QtWidgets.QLabel(
            "Use this resonance-specific version when each transient run is performed at a dominant resonant frequency found from harmonic analysis."
        )
        info.setWordWrap(True)
        info.setToolTip(INFO_TOOLTIP)
        root.addWidget(info)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        root.addWidget(splitter, stretch=1)

        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        splitter.addWidget(left)

        input_group = QtWidgets.QGroupBox("Global inputs")
        form = QtWidgets.QFormLayout(input_group)
        left_layout.addWidget(input_group)

        self.zeta_edit = QtWidgets.QLineEdit("0.02")
        self.zeta_edit.setToolTip(DEFAULT_ZETA_TOOLTIP)
        form.addRow("Default damping ratio, ζ", self.zeta_edit)

        self.eps_percent = QtWidgets.QDoubleSpinBox()
        self.eps_percent.setRange(1e-9, 99.999999)
        self.eps_percent.setDecimals(6)
        self.eps_percent.setValue(1.0)
        self.eps_percent.setSuffix(" %")
        self.eps_percent.setToolTip(EPSILON_TOOLTIP)
        form.addRow("Target remaining transient, ε", self.eps_percent)

        self.safety_factor = QtWidgets.QDoubleSpinBox()
        self.safety_factor.setRange(1.0, 20.0)
        self.safety_factor.setDecimals(3)
        self.safety_factor.setSingleStep(0.05)
        self.safety_factor.setValue(1.20)
        self.safety_factor.setToolTip(SAFETY_FACTOR_TOOLTIP)
        form.addRow("Safety factor", self.safety_factor)

        self.extra_cycles = QtWidgets.QSpinBox()
        self.extra_cycles.setRange(0, 10000)
        self.extra_cycles.setValue(1)
        self.extra_cycles.setToolTip(EXTRA_CYCLES_TOOLTIP)
        form.addRow("Extra post-settling cycles", self.extra_cycles)

        self.steps_per_cycle = QtWidgets.QSpinBox()
        self.steps_per_cycle.setRange(4, 100000)
        self.steps_per_cycle.setValue(50)
        self.steps_per_cycle.setToolTip(STEPS_PER_CYCLE_TOOLTIP)
        form.addRow("Suggested points per cycle", self.steps_per_cycle)

        freq_group = QtWidgets.QGroupBox("Dominant resonant frequencies")
        freq_layout = QtWidgets.QVBoxLayout(freq_group)
        left_layout.addWidget(freq_group, stretch=1)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Resonant frequency f_res [Hz]", "ζ override (optional)"])
        self.table.setToolTip(FREQUENCY_TABLE_TOOLTIP)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeaderItem(0).setToolTip(FREQ_COLUMN_TOOLTIP)
        self.table.horizontalHeaderItem(1).setToolTip(ZETA_OVERRIDE_TOOLTIP)
        freq_layout.addWidget(self.table)

        buttons = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton("Add frequency")
        self.remove_button = QtWidgets.QPushButton("Remove selected")
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.add_button.setToolTip("Add another resonant frequency row to estimate.")
        self.remove_button.setToolTip("Remove the currently selected frequency rows.")
        self.reset_button.setToolTip("Reset the table to one default example row.")
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.remove_button)
        buttons.addWidget(self.reset_button)
        buttons.addStretch(1)
        freq_layout.addLayout(buttons)

        self.calculate_button = QtWidgets.QPushButton("Calculate")
        self.calculate_button.setDefault(True)
        self.calculate_button.setToolTip("Recalculate the recommended run length using the current inputs.")
        left_layout.addWidget(self.calculate_button, alignment=QtCore.Qt.AlignRight)

        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        splitter.addWidget(right)
        splitter.setSizes([420, 630])

        result_group = QtWidgets.QGroupBox("Results")
        result_layout = QtWidgets.QVBoxLayout(result_group)
        right_layout.addWidget(result_group, stretch=1)

        self.results_browser = QtWidgets.QTextBrowser()
        self.results_browser.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.results_browser.setToolTip(RESULTS_TOOLTIP)
        result_layout.addWidget(self.results_browser)

        note = QtWidgets.QTextBrowser()
        note.setMaximumHeight(155)
        note.setToolTip(NOTE_TOOLTIP)
        note.setHtml(
            "<p><b>Interpretation:</b> At exact resonance, required cycles depend on damping ratio and tolerance, not on the actual frequency value. "
            "The frequency still controls physical run time and time-step size.</p>"
            "<p>Compare harmonic amplitude to the final steady-state cycle, not to the maximum over the entire transient history.</p>"
        )
        right_layout.addWidget(note)

        self._reset_rows()

    def _build_docs_tab(self) -> None:
        layout = QtWidgets.QVBoxLayout(self.docs_tab)
        browser = QtWidgets.QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setToolTip("Background notes, formulas, assumptions, and references for the resonance-only estimator.")
        browser.setHtml(DOCS_HTML)
        layout.addWidget(browser)

    def _connect_signals(self) -> None:
        self.calculate_button.clicked.connect(self.calculate)
        self.zeta_edit.editingFinished.connect(self.calculate)
        self.eps_percent.valueChanged.connect(self.calculate)
        self.safety_factor.valueChanged.connect(self.calculate)
        self.extra_cycles.valueChanged.connect(self.calculate)
        self.steps_per_cycle.valueChanged.connect(self.calculate)
        self.add_button.clicked.connect(self._add_row)
        self.remove_button.clicked.connect(self._remove_selected_rows)
        self.reset_button.clicked.connect(self._reset_rows)
        self.table.itemChanged.connect(self.calculate)

    def _make_item(self, text: str) -> QtWidgets.QTableWidgetItem:
        item = QtWidgets.QTableWidgetItem(text)
        item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        return item

    def _add_row(self, frequency: Optional[float] = None, zeta_override: str = "") -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        f_value = 100.0 if frequency is None else frequency
        self.table.setItem(row, 0, self._make_item(f"{f_value:.9g}"))
        self.table.setItem(row, 1, self._make_item(zeta_override))
        self.calculate()

    def _remove_selected_rows(self) -> None:
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)
        self.calculate()

    def _reset_rows(self) -> None:
        blocked = self.table.blockSignals(True)
        self.table.setRowCount(0)
        self._add_row(100.0, "")
        self.table.blockSignals(blocked)
        if hasattr(self, "results_browser"):
            self.calculate()

    def _read_rows(self) -> List[RowResult]:
        default_zeta = parse_ratio(self.zeta_edit.text(), "Default damping ratio ζ")
        eps = self.eps_percent.value() / 100.0
        safety = self.safety_factor.value()
        extra = self.extra_cycles.value()
        steps = self.steps_per_cycle.value()

        rows: List[RowResult] = []
        for row in range(self.table.rowCount()):
            f_item = self.table.item(row, 0)
            z_item = self.table.item(row, 1)
            if f_item is None:
                continue
            f_text = f_item.text().strip()
            if not f_text:
                continue
            frequency = parse_float(f_text, f"Row {row + 1} frequency")
            z_text = z_item.text().strip() if z_item is not None else ""
            zeta = default_zeta if not z_text else parse_ratio(z_text, f"Row {row + 1} ζ override")
            rows.append(estimate_row(row + 1, frequency, zeta, eps, safety, extra, steps))

        if not rows:
            raise ValueError("Enter at least one resonant frequency.")
        return rows

    def calculate(self) -> None:
        if not hasattr(self, "results_browser"):
            return
        try:
            rows = self._read_rows()
            self.results_browser.setHtml(self._format_results(rows))
        except Exception as exc:
            self.results_browser.setHtml(f"<h3>Input error</h3><p>{html.escape(str(exc))}</p>")

    def _format_results(self, rows: List[RowResult]) -> str:
        worst = max(rows, key=lambda r: r.run_cycles)
        eps = self.eps_percent.value() / 100.0
        html_lines: List[str] = ["<html><body>"]
        html_lines.append("<h2>Resonance settling estimate</h2>")
        html_lines.append(
            "<p>At resonance: N<sub>ss</sub> = -ln(ε)/(2πζ). "
            "Rounded cycles include the safety factor. Total cycles also include the extra post-settling cycles.</p>"
        )
        html_lines.append('<table border="1" cellspacing="0" cellpadding="5">')
        html_lines.append(f"<tr><td>Target remaining transient ε</td><td>{100.0 * eps:.9g}%</td></tr>")
        html_lines.append(f"<tr><td>Safety factor</td><td>{self.safety_factor.value():.6g}</td></tr>")
        html_lines.append(f"<tr><td>Extra post-settling cycles</td><td>{self.extra_cycles.value()}</td></tr>")
        html_lines.append(f"<tr><td>Most conservative total cycle count</td><td><b>{worst.run_cycles}</b> cycles</td></tr>")
        html_lines.append("</table>")

        html_lines.append("<h3>Per-frequency run settings</h3>")
        html_lines.append('<table border="1" cellspacing="0" cellpadding="4">')
        html_lines.append(
            "<tr>"
            "<th>Row</th><th>f_res [Hz]</th><th>ζ</th><th>base N_ss</th><th>safety × N_ss</th>"
            "<th>rounded settling cycles</th><th>recommended total cycles</th><th>run time [s]</th>"
            "<th>suggested Δt [s]</th><th>points</th><th>residual after run</th>"
            "</tr>"
        )
        for r in rows:
            html_lines.append(
                f"<tr><td>{r.row}</td>"
                f"<td>{r.frequency_hz:.9g}</td>"
                f"<td>{r.zeta:.9g}</td>"
                f"<td>{r.base_cycles:.9g}</td>"
                f"<td>{r.safe_cycles:.9g}</td>"
                f"<td>{r.rounded_settling_cycles}</td>"
                f"<td><b>{r.run_cycles}</b></td>"
                f"<td>{r.run_time_s:.9g}</td>"
                f"<td>{r.dt_s:.9g}</td>"
                f"<td>{r.n_points}</td>"
                f"<td>{r.residual_after_run:.6g}</td></tr>"
            )
        html_lines.append("</table>")

        html_lines.append("<h3>Residual envelope at selected cycles</h3>")
        sample_cycles = np.array([0, 5, 10, 20, 50, 100, worst.run_cycles], dtype=float)
        sample_cycles = np.unique(sample_cycles[sample_cycles >= 0])
        html_lines.append('<table border="1" cellspacing="0" cellpadding="4">')
        html_lines.append("<tr><th>N cycles</th>")
        for r in rows:
            html_lines.append(f"<th>row {r.row}, ζ={r.zeta:.4g}</th>")
        html_lines.append("</tr>")
        for n in sample_cycles:
            html_lines.append(f"<tr><td>{int(n)}</td>")
            for r in rows:
                residual = math.exp(-2.0 * math.pi * r.zeta * n)
                html_lines.append(f"<td>{residual:.6g}</td>")
            html_lines.append("</tr>")
        html_lines.append("</table>")

        html_lines.append(
            "<p><b>Peak comparison:</b> Extract the peak from the final complete cycle(s). "
            "The maximum over the full transient can differ from harmonic response because it includes the decaying transient.</p>"
        )
        html_lines.append("</body></html>")
        return "\n".join(html_lines)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
