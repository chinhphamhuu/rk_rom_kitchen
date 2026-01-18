"""
QSS Stylesheet - Dark theme giống CRB Android Kitchen
"""

# Color palette
COLORS = {
    "bg_dark": "#1e1e1e",
    "bg_medium": "#252526",
    "bg_light": "#2d2d30",
    "bg_hover": "#3e3e42",
    "bg_selected": "#094771",
    "fg_primary": "#cccccc",
    "fg_secondary": "#969696",
    "fg_disabled": "#5a5a5a",
    "accent": "#0e639c",
    "accent_hover": "#1177bb",
    "border": "#3c3c3c",
    "border_light": "#4a4a4a",
    "success": "#4ec9b0",
    "warning": "#dcdcaa",
    "error": "#f14c4c",
    "info": "#3794ff",
}

# Main stylesheet
STYLESHEET = f"""
/* ===== Global ===== */
QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['fg_primary']};
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}}

/* ===== Main Window ===== */
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

/* ===== Scroll Bars ===== */
QScrollBar:vertical {{
    background: {COLORS['bg_dark']};
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border_light']};
    min-height: 30px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['fg_secondary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {COLORS['bg_dark']};
    height: 12px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['border_light']};
    min-width: 30px;
    border-radius: 6px;
    margin: 2px;
}}

/* ===== Labels ===== */
QLabel {{
    background: transparent;
    color: {COLORS['fg_primary']};
}}

QLabel[heading="true"] {{
    font-size: 16px;
    font-weight: bold;
    color: {COLORS['fg_primary']};
    padding: 8px 0;
}}

/* ===== Buttons ===== */
QPushButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_selected']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['fg_disabled']};
}}

QPushButton[secondary="true"] {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
}}

QPushButton[secondary="true"]:hover {{
    background-color: {COLORS['bg_hover']};
}}

QPushButton[danger="true"] {{
    background-color: {COLORS['error']};
}}

QPushButton[danger="true"]:hover {{
    background-color: #ff6b6b;
}}

/* ===== Line Edit ===== */
QLineEdit {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px 10px;
    color: {COLORS['fg_primary']};
    selection-background-color: {COLORS['accent']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['fg_disabled']};
}}

/* ===== Combo Box ===== */
QComboBox {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px 10px;
    color: {COLORS['fg_primary']};
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {COLORS['border_light']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['fg_secondary']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['bg_selected']};
    outline: none;
}}

/* ===== Check Box ===== */
QCheckBox {{
    spacing: 8px;
    color: {COLORS['fg_primary']};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    background-color: {COLORS['bg_light']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent']};
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    background-color: {COLORS['bg_light']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 4px;
}}

/* ===== Text Edit / Plain Text Edit ===== */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_medium']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    color: {COLORS['fg_primary']};
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: {COLORS['accent']};
}}

/* ===== Table ===== */
QTableWidget, QTableView {{
    background-color: {COLORS['bg_medium']};
    border: 1px solid {COLORS['border']};
    gridline-color: {COLORS['border']};
    color: {COLORS['fg_primary']};
}}

QTableWidget::item, QTableView::item {{
    padding: 6px;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {COLORS['bg_selected']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['fg_primary']};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {COLORS['border']};
    font-weight: bold;
}}

/* ===== Group Box ===== */
QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: {COLORS['fg_primary']};
}}

/* ===== Tab Widget ===== */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_medium']};
    border-bottom: 2px solid {COLORS['accent']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['bg_hover']};
}}

/* ===== Splitter ===== */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* ===== Menu ===== */
QMenu {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border']};
    margin: 4px 8px;
}}

/* ===== Tool Tip ===== */
QToolTip {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['fg_primary']};
    padding: 4px 8px;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {COLORS['bg_medium']};
    border-top: 1px solid {COLORS['border']};
}}

/* ===== Custom Classes ===== */
/* Icon Sidebar */
QWidget#IconSidebar {{
    background-color: {COLORS['bg_medium']};
    border-right: 1px solid {COLORS['border']};
}}

QWidget#IconSidebar QPushButton {{
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 12px;
    min-width: 56px;
    min-height: 48px;
}}

QWidget#IconSidebar QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
}}

QWidget#IconSidebar QPushButton:checked {{
    background-color: {COLORS['bg_selected']};
    border-left: 3px solid {COLORS['accent']};
}}

/* Project Sidebar */
QWidget#ProjectSidebar {{
    background-color: {COLORS['bg_medium']};
    border-right: 1px solid {COLORS['border']};
}}

/* Log Panel */
QWidget#LogPanel {{
    background-color: {COLORS['bg_medium']};
    border-top: 1px solid {COLORS['border']};
}}

/* Info Box */
QFrame#InfoBox {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px;
}}
"""


def get_stylesheet() -> str:
    """Trả về QSS stylesheet"""
    return STYLESHEET


def get_color(name: str) -> str:
    """Lấy màu theo tên"""
    return COLORS.get(name, "#ffffff")
