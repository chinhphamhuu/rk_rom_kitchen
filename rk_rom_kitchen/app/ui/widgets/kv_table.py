"""
Key-Value Table - Hiển thị thông tin dạng bảng
"""
from typing import List, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt


class KVTable(QWidget):
    """
    Table hiển thị key-value pairs
    Dùng cho tools status, project info, etc.
    """
    
    def __init__(self, 
                 headers: Tuple[str, str] = ("Key", "Value"),
                 parent=None):
        super().__init__(parent)
        self._headers = headers
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(list(self._headers))
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        
        layout.addWidget(self._table)
    
    def set_data(self, data: List[Tuple[str, str]]):
        """Set table data từ list of tuples"""
        self._table.setRowCount(len(data))
        
        for row, (key, value) in enumerate(data):
            key_item = QTableWidgetItem(str(key))
            value_item = QTableWidgetItem(str(value))
            
            self._table.setItem(row, 0, key_item)
            self._table.setItem(row, 1, value_item)
    
    def set_headers(self, headers: Tuple[str, str]):
        """Update headers"""
        self._headers = headers
        self._table.setHorizontalHeaderLabels(list(headers))
    
    def add_row(self, key: str, value: str):
        """Add một row mới"""
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(key))
        self._table.setItem(row, 1, QTableWidgetItem(value))
    
    def clear(self):
        """Clear table"""
        self._table.setRowCount(0)


class ToolsStatusTable(QWidget):
    """
    Table đặc biệt cho hiển thị tools status
    3 columns: Tool, Path, Status
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Tool", "Path", "Status"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self._table)
    
    def set_tools(self, tools: list):
        """
        Set tools data
        
        Args:
            tools: List of ToolInfo objects hoặc dicts với keys: name, path, available
        """
        self._table.setRowCount(len(tools))
        
        for row, tool in enumerate(tools):
            if hasattr(tool, 'name'):
                # ToolInfo object
                name = tool.name
                path = str(tool.path) if tool.path else ""
                available = tool.available
            else:
                # Dict
                name = tool.get('name', '')
                path = tool.get('path', '')
                available = tool.get('available', False)
            
            name_item = QTableWidgetItem(name)
            path_item = QTableWidgetItem(path)
            
            status = "✓" if available else "✗"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Color based on status
            if available:
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            
            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, path_item)
            self._table.setItem(row, 2, status_item)
    
    def clear(self):
        """Clear table"""
        self._table.setRowCount(0)
