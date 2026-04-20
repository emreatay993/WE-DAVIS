import html
import re

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


HELP_MARKDOWN = """
# Transient Steady-State Cycle Estimator

## Short answer

- A mode-superposition harmonic analysis returns the **steady-state** response at the driving frequency.
- A mode-superposition transient analysis with the **same linear model**, **same modal basis**, **same damping**, and the **same continuous sinusoidal load** converges to the same steady-state sinusoid after the startup transient decays.
- The **absolute maximum over the full transient history** is not guaranteed to equal the harmonic peak because startup transients, phase effects, and slight detuning can temporarily shift the time-history maximum.

## Dominant-mode model used here

For one dominant mode, the modal coordinate is modeled as:

```text
q_ddot + 2*zeta*omega_n*q_dot + omega_n^2*q = p0*cos(omega*t)
```

The total response is the sum of a steady-state term and a decaying transient term:

```text
q(t) = q_ss(t) + q_tr(t)
q_tr(t) ~ exp(-zeta*omega_n*t)
```

That exponential envelope is the basis of this estimator.

## Estimator

Choose a residual transient fraction `r`.

- `r = 0.01` means **1% of the startup transient envelope remains**
- equivalently, the response is about **99% settled** to the steady-state limit

The required run time is estimated from:

```text
t_required = ln(1/r) / (zeta*omega_n)
```

The corresponding number of excitation cycles is:

```text
N_cycles = f_exc * t_required
         = (omega / (2*pi*zeta*omega_n)) * ln(1/r)
```

If you run the transient at the same dominant resonant frequency identified from harmonic analysis:

```text
omega ~= omega_n
N_cycles ~= ln(1/r) / (2*pi*zeta)
```

At exact resonance, the cycle count therefore depends mainly on damping. The selected frequency changes the required **time**, not much the required **cycle count**.

## Practical reference values at exact resonance

- 5% residual transient: `N ~= 0.477 / zeta`
- 1% residual transient: `N ~= 0.733 / zeta`
- 0.1% residual transient: `N ~= 1.099 / zeta`

## Several nearby resonant modes

If several modes contribute near the excitation frequency, a conservative estimate is based on the slowest modal decay rate:

```text
t_required ~= max_i [ ln(1/r) / (zeta_i*omega_n_i) ]
```

This dialog is intended for the common case you described: a transient run driven at a known dominant resonant frequency from the harmonic study.

## Interpretation

- **Harmonic result**: steady-state amplitude at the selected frequency
- **Transient result after settling**: should match the harmonic amplitude within numerical tolerance
- **Transient maximum over all time**: can be slightly lower or higher before settling

## References

1. [ANSYS Help: Harmonic Response](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/wb2_help/wb2h_harmrespAN.html)
2. [ANSYS Help: Mode-Superposition Transient Dynamic Analysis](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_str/Hlp_G_STR5_10.html)
3. [Engineering LibreTexts: Forced Vibrations](https://eng.libretexts.org/Bookshelves/Mechanical_Engineering/Introductory_Dynamics%3A_2D_Kinematics_and_Kinetics_of_Point_Masses_and_Rigid_Bodies_%28Steeneken%29/04%3A_Vibrations_and_Strategy/13%3A_Vibrations/13.04%3A_Forced_vibrations)
4. [MIT OpenCourseWare: Forced Oscillation and Resonance](https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/782069da3820fc514c10c26ae0c15b01_MIT8_03SCF16_Text_Ch2.pdf)
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
        if hasattr(help_browser, "setMarkdown"):
            help_browser.setMarkdown(HELP_MARKDOWN)
        else:
            help_browser.setHtml(self._markdown_to_html(HELP_MARKDOWN))

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

    @staticmethod
    def _format_inline_markdown(text: str) -> str:
        link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
        result_parts = []
        last_index = 0

        for match in link_pattern.finditer(text):
            result_parts.append(html.escape(text[last_index:match.start()]))
            label = html.escape(match.group(1))
            url = html.escape(match.group(2), quote=True)
            result_parts.append(f'<a href="{url}">{label}</a>')
            last_index = match.end()

        result_parts.append(html.escape(text[last_index:]))
        formatted = "".join(result_parts)
        formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", formatted)
        formatted = re.sub(r"`([^`]+)`", r"<code>\1</code>", formatted)
        return formatted

    @classmethod
    def _markdown_to_html(cls, markdown_text: str) -> str:
        html_parts = ["<html><body>"]
        paragraph_lines = []
        in_unordered_list = False
        in_ordered_list = False
        in_code_block = False
        code_lines = []

        def flush_paragraph():
            nonlocal paragraph_lines
            if not paragraph_lines:
                return
            combined = " ".join(line.strip() for line in paragraph_lines)
            html_parts.append(f"<p>{cls._format_inline_markdown(combined)}</p>")
            paragraph_lines = []

        def close_lists():
            nonlocal in_unordered_list, in_ordered_list
            if in_unordered_list:
                html_parts.append("</ul>")
                in_unordered_list = False
            if in_ordered_list:
                html_parts.append("</ol>")
                in_ordered_list = False

        for raw_line in markdown_text.strip().splitlines():
            line = raw_line.rstrip()

            if line.startswith("```"):
                flush_paragraph()
                close_lists()
                if in_code_block:
                    html_parts.append("<pre><code>{}</code></pre>".format("\n".join(code_lines)))
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(html.escape(line))
                continue

            stripped = line.strip()
            if not stripped:
                flush_paragraph()
                close_lists()
                continue

            heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_match:
                flush_paragraph()
                close_lists()
                level = len(heading_match.group(1))
                text = cls._format_inline_markdown(heading_match.group(2))
                html_parts.append(f"<h{level}>{text}</h{level}>")
                continue

            unordered_match = re.match(r"^-\s+(.*)$", stripped)
            if unordered_match:
                flush_paragraph()
                if in_ordered_list:
                    html_parts.append("</ol>")
                    in_ordered_list = False
                if not in_unordered_list:
                    html_parts.append("<ul>")
                    in_unordered_list = True
                html_parts.append(f"<li>{cls._format_inline_markdown(unordered_match.group(1))}</li>")
                continue

            ordered_match = re.match(r"^\d+\.\s+(.*)$", stripped)
            if ordered_match:
                flush_paragraph()
                if in_unordered_list:
                    html_parts.append("</ul>")
                    in_unordered_list = False
                if not in_ordered_list:
                    html_parts.append("<ol>")
                    in_ordered_list = True
                html_parts.append(f"<li>{cls._format_inline_markdown(ordered_match.group(1))}</li>")
                continue

            paragraph_lines.append(stripped)

        if in_code_block:
            html_parts.append("<pre><code>{}</code></pre>".format("\n".join(code_lines)))

        flush_paragraph()
        close_lists()
        html_parts.append("</body></html>")
        return "\n".join(html_parts)
