from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QMessageBox
except ModuleNotFoundError:
    def _install_pyqt5_stub() -> None:
        pyqt5_module = ModuleType("PyQt5")
        qtcore_module = ModuleType("PyQt5.QtCore")
        qtwidgets_module = ModuleType("PyQt5.QtWidgets")

        class _BoundSignal:
            def __init__(self) -> None:
                self._slots = []

            def connect(self, slot) -> None:
                self._slots.append(slot)

            def emit(self, *args, **kwargs) -> None:
                for slot in list(self._slots):
                    slot(*args, **kwargs)

        class _SignalDescriptor:
            def __init__(self) -> None:
                self._name = None

            def __set_name__(self, owner, name) -> None:
                self._name = f"__signal_{name}"

            def __get__(self, instance, owner):
                if instance is None:
                    return self
                if not hasattr(instance, self._name):
                    setattr(instance, self._name, _BoundSignal())
                return getattr(instance, self._name)

        class QObject:
            def __init__(self, parent=None) -> None:
                self.parent = parent

        class QCoreApplication:
            _instance = None

            def __init__(self, args=None) -> None:
                QCoreApplication._instance = self

            @classmethod
            def instance(cls):
                return cls._instance

        def pyqtSignal(*args, **kwargs):
            return _SignalDescriptor()

        def pyqtSlot(*args, **kwargs):
            def decorator(function):
                return function
            return decorator

        class QFileDialog:
            @staticmethod
            def getExistingDirectory(*args, **kwargs):
                return ""

        class QMessageBox:
            @staticmethod
            def warning(*args, **kwargs):
                return None

            @staticmethod
            def critical(*args, **kwargs):
                return None

            @staticmethod
            def information(*args, **kwargs):
                return None

        qtcore_module.QObject = QObject
        qtcore_module.QCoreApplication = QCoreApplication
        qtcore_module.pyqtSignal = pyqtSignal
        qtcore_module.pyqtSlot = pyqtSlot
        qtwidgets_module.QFileDialog = QFileDialog
        qtwidgets_module.QMessageBox = QMessageBox

        pyqt5_module.QtCore = qtcore_module
        pyqt5_module.QtWidgets = qtwidgets_module
        sys.modules["PyQt5"] = pyqt5_module
        sys.modules["PyQt5.QtCore"] = qtcore_module
        sys.modules["PyQt5.QtWidgets"] = qtwidgets_module

    _install_pyqt5_stub()
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QMessageBox

from app.data_manager import DataManager


class DataManagerUnitMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.qt_app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication([])
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.frequency_sample = cls.repo_root / "resources" / "sample_data" / "frequency_sample"
        cls.time_sample = cls.repo_root / "resources" / "sample_data" / "time_transient_sample"

    def setUp(self) -> None:
        self.data_manager = DataManager()
        self.warning_patcher = patch.object(QMessageBox, "warning", return_value=None)
        self.critical_patcher = patch.object(QMessageBox, "critical", return_value=None)
        self.information_patcher = patch.object(QMessageBox, "information", return_value=None)
        self.warning_patcher.start()
        self.critical_patcher.start()
        self.information_patcher.start()
        self.addCleanup(self.warning_patcher.stop)
        self.addCleanup(self.critical_patcher.stop)
        self.addCleanup(self.information_patcher.stop)

    def test_frequency_sample_primary_load_emits_aligned_unit_context(self) -> None:
        data, data_domain, folder_path, unit_context = self._load_primary_folder(self.frequency_sample)

        self.assertEqual(data_domain, "FREQ")
        self.assertEqual(Path(folder_path), self.frequency_sample)
        self.assertEqual(list(unit_context), list(data.columns))
        self.assertEqual(
            list(data.columns[:6]),
            [
                "NO",
                "FREQ",
                "I1 - STBD REAR MOUNT (CS-8012) T1",
                "Phase_I1 - STBD REAR MOUNT (CS-8012) T1",
                "I2 - PORT REAR MOUNT (CS-8013) T1",
                "Phase_I2 - PORT REAR MOUNT (CS-8013) T1",
            ],
        )
        self.assertEqual(unit_context["FREQ"].normalized_unit, "Hz")
        self.assertEqual(unit_context["FREQ"].quantity_family, "frequency")
        self.assertEqual(unit_context["I1 - STBD REAR MOUNT (CS-8012) T1"].normalized_unit, "kN")
        self.assertEqual(
            unit_context["Phase_I1 - STBD REAR MOUNT (CS-8012) T1"].quantity_family,
            "phase",
        )
        self.assertIsNone(unit_context["DataFolder"].normalized_unit)
        self.assertEqual(data["DataFolder"].nunique(), 1)

    def test_time_sample_primary_load_keeps_time_domain_and_context_alignment(self) -> None:
        data, data_domain, _, unit_context = self._load_primary_folder(self.time_sample)

        self.assertEqual(data_domain, "TIME")
        self.assertEqual(list(unit_context), list(data.columns))
        self.assertEqual(list(data.columns[:5]), ["NO", "TIME", "I1 - STBD REAR MOUNT (CS-8012) T1", "I1 - PORT REAR MOUNT (CS-8013) R1", "I3-TT/FBS/IPS - TT Side (CS-8001) T1"])
        self.assertEqual(unit_context["TIME"].normalized_unit, "s")
        self.assertEqual(unit_context["TIME"].quantity_family, "time")
        self.assertEqual(data["DataFolder"].iloc[0], self.time_sample.name)

    def test_comparison_load_emits_unit_context(self) -> None:
        emitted = []
        self.data_manager.comparisonDataLoaded.connect(
            lambda df_compare, unit_context_compare: emitted.append((df_compare, unit_context_compare))
        )

        with patch.object(self.data_manager, "_select_directory", return_value=str(self.frequency_sample)):
            self.data_manager.load_comparison_data()

        self.assertEqual(len(emitted), 1)
        df_compare, unit_context_compare = emitted[0]
        self.assertEqual(list(unit_context_compare), list(df_compare.columns))
        self.assertNotIn("DataFolder", unit_context_compare)
        self.assertEqual(unit_context_compare["FREQ"].normalized_unit, "Hz")
        self.assertEqual(
            unit_context_compare["Phase_I1 - STBD REAR MOUNT (CS-8012) T1"].display_unit,
            "deg",
        )

    def test_extra_column_fallback_receives_native_only_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._write_pld_files(
                temp_path,
                full_text="""
                | NO | FREQ | Y1 | Y2 | Y3 | Y4 | Y5 |
                ______________________________________
                | 1 | 5.0 | 10.0 | 15.0 | 20.0 | 25.0 | 30.0 |
                | 2 | 6.0 | 11.0 | 16.0 | 21.0 | 26.0 | 31.0 |
                """,
                max_text="""
                | Interface Label | UNIT | MAGNITUDE | PHASE(deg) | FREQ(Hz) |
                _______________________________________________________________
                | Channel Force | kN | 10.0 | 15.0 | 5.0 |
                | Channel Moment | kN*m | 20.0 | 25.0 | 6.0 |
                """,
            )

            data, data_domain, _, unit_context = self._load_primary_folder(temp_path)

        self.assertEqual(data_domain, "FREQ")
        self.assertIn("Extra_Column_1", data.columns)
        self.assertEqual(unit_context["Channel Force"].quantity_family, "force")
        self.assertEqual(unit_context["Channel Moment"].quantity_family, "moment")
        self.assertTrue(unit_context["Extra_Column_1"].native_only)
        self.assertIsNone(unit_context["Extra_Column_1"].normalized_unit)

    def test_loader_detects_units_from_max_pld_without_using_component_suffixes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._write_pld_files(
                temp_path,
                full_text="""
                | NO | FREQ | Y1 | Y2 | Y3 | Y4 |
                __________________________________
                | 1 | 1.0 | 0.25 | 0.00 | 5.0 | 0.50 |
                | 2 | 2.0 | 0.50 | 0.25 | 6.0 | 0.75 |
                """,
                max_text="""
                | Interface Label | UNIT | MAGNITUDE | PHASE(rad) | FREQ(kHz) |
                ________________________________________________________________
                | Custom Channel T1 | m | 0.25 | 0.00 | 1.0 |
                | Custom Channel R1 | N | 5.0 | 0.50 | 1.0 |
                """,
            )

            data, data_domain, _, unit_context = self._load_primary_folder(temp_path)

        self.assertEqual(data_domain, "FREQ")
        self.assertEqual(list(unit_context), list(data.columns))
        self.assertEqual(unit_context["FREQ"].normalized_unit, "kHz")
        self.assertEqual(unit_context["Phase_Custom Channel T1"].normalized_unit, "rad")
        self.assertEqual(unit_context["Custom Channel T1"].quantity_family, "displacement")
        self.assertEqual(unit_context["Custom Channel R1"].quantity_family, "force")

    def _load_primary_folder(self, folder: Path):
        emitted = []
        failures = []
        self.data_manager.dataLoaded.connect(
            lambda data, data_domain, folder_path, unit_context: emitted.append(
                (data, data_domain, folder_path, unit_context)
            )
        )
        self.data_manager.dataLoadFailed.connect(failures.append)

        self.data_manager.load_data_from_paths([str(folder)])

        self.assertFalse(failures, failures[0] if failures else None)
        self.assertEqual(len(emitted), 1)
        return emitted[0]

    def _write_pld_files(self, folder: Path, full_text: str, max_text: str) -> None:
        (folder / "PLD_DATA_0_full.pld").write_text(
            textwrap.dedent(full_text).strip() + "\n",
            encoding="utf-8",
        )
        (folder / "PLD_HEADER_DATA_max.pld").write_text(
            textwrap.dedent(max_text).strip() + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
