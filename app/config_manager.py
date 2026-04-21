# File: app/config_manager.py
# This file contains all the Qt Style Sheet (QSS) strings for the application.

TREEVIEW_STYLE = """
    QTreeView {
        background-color: #f7f7f7;
        border: none;
    }
    QTreeView::item {
        padding: 5px;
    }
    QTreeView::item:selected {
        background-color: #00838f;
        color: white;
    }
"""

TABWIDGET_STYLE = """
    QTabBar::tab {
        background: #00838f;
        color: white;
        min-width: 120px;
        padding: 5px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        margin-right: 5px;
    }
    QTabBar::tab:selected {
        background: #00acc1;
        font-weight: normal;
    }
    QTabBar::tab:disabled {
        background: #cccccc;
        color: #777777;
    }
    QTabWidget::pane {
        border-top: 2px solid #ccc;
        border-left: 1px solid #ccc;
        border-right: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
        border-radius: 10px;
        padding: 5px;
    }
"""

GROUPBOX_STYLE = """
    QGroupBox {
        color: #00838f;
        background-color: #f0f0f0;
        border: 1px solid lightgray;
        border-radius: 5px;
        margin-top: 1ex;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 3px;
    }
"""

COMPARE_BUTTON_STYLE = """
    QPushButton {
        background-color: #00838f;
        color: white;
        border: 2px solid #006064;
        border-radius: 5px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #00acc1;
        border-color: #006064;
    }
    QPushButton:pressed {
        background-color: #006064;
        border-color: #004d40;
    }
"""

# QSS for the reusable CheckableComboBox widget (see app/ui/widgets/checkable_combo_box.py).
# Matches mockups/multiselect_variations.html Variation 1 — teal #00838f / cyan #00acc1
# palette, white trigger, rounded 4 px corners, 1 px #dcdde0 border, and teal check marks.
CHECKABLE_COMBO_STYLE = """
    QWidget#CheckableComboBox {
        background: transparent;
    }
    QPushButton#CheckableComboBoxTrigger {
        background-color: white;
        color: #333333;
        border: 1px solid #dcdde0;
        border-radius: 4px;
        padding: 4px 10px;
        text-align: left;
        font-size: 12px;
        min-height: 22px;
    }
    QPushButton#CheckableComboBoxTrigger:hover {
        border-color: #00acc1;
    }
    QPushButton#CheckableComboBoxTrigger:focus {
        border-color: #00838f;
        outline: none;
    }
    QPushButton#CheckableComboBoxTrigger:disabled {
        background-color: #f7f7f7;
        color: #888888;
    }
    QLabel#CheckableComboBoxCountBadge {
        background-color: #00838f;
        color: white;
        border-radius: 9px;
        padding: 1px 8px;
        font-size: 11px;
        font-weight: 600;
        min-width: 16px;
    }
    QLabel#CheckableComboBoxCaret {
        color: #888888;
        font-size: 11px;
        padding-left: 6px;
    }
    QLabel#CheckableComboBoxSummary {
        color: #333333;
        font-size: 12px;
    }
    QLabel#CheckableComboBoxSummary[placeholder="true"] {
        color: #b0b3b8;
    }
    QFrame#CheckableComboBoxPopup {
        background-color: white;
        border: 1px solid #dcdde0;
        border-radius: 6px;
    }
    QLineEdit#CheckableComboBoxSearch {
        background-color: white;
        border: 1px solid #dcdde0;
        border-radius: 3px;
        padding: 3px 6px;
        font-size: 12px;
    }
    QLineEdit#CheckableComboBoxSearch:focus {
        border-color: #00acc1;
        outline: none;
    }
    QListWidget#CheckableComboBoxList {
        background-color: white;
        border: none;
        outline: 0;
        font-size: 12px;
    }
    QListWidget#CheckableComboBoxList::item {
        padding: 4px 6px;
        border-radius: 3px;
        color: #333333;
    }
    QListWidget#CheckableComboBoxList::item:hover {
        background-color: #f0f9fa;
    }
    QListWidget#CheckableComboBoxList::item:selected {
        background-color: #e0f3f5;
        color: #333333;
    }
    QListWidget#CheckableComboBoxList::item:disabled {
        color: #006064;
        background-color: transparent;
    }
    QListWidget#CheckableComboBoxList::indicator {
        width: 14px;
        height: 14px;
        border: 1.5px solid #b0b3b8;
        border-radius: 3px;
        background-color: white;
    }
    QListWidget#CheckableComboBoxList::indicator:hover {
        border-color: #00acc1;
    }
    QListWidget#CheckableComboBoxList::indicator:checked {
        background-color: #00838f;
        border-color: #00838f;
        image: none;
    }
    QListWidget#CheckableComboBoxList::indicator:unchecked {
        background-color: white;
    }
    QFrame#CheckableComboBoxFooter {
        background-color: #fafbfc;
        border: none;
        border-top: 1px solid #dcdde0;
    }
    QPushButton#CheckableComboBoxGhost {
        background-color: transparent;
        color: #006064;
        border: 1px solid transparent;
        border-radius: 3px;
        padding: 3px 10px;
        font-size: 11.5px;
    }
    QPushButton#CheckableComboBoxGhost:hover {
        background-color: white;
        border-color: #dcdde0;
        color: #00838f;
    }
    QPushButton#CheckableComboBoxGhost:pressed {
        background-color: #e0f3f5;
        color: #006064;
    }
"""
