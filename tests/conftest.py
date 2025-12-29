"""Pytest configuration for all tests"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

# Mock Anki modules BEFORE any project imports
def setup_anki_mocks():
    """Set up mock Anki modules to prevent import errors"""
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    
    # Create mock modules
    mock_anki = MagicMock()
    mock_anki._backend = MagicMock()
    mock_anki._rsbridge = MagicMock()
    mock_anki.lang = MagicMock()
    mock_anki.backend_pb2 = MagicMock()
    mock_anki.i18n_pb2 = MagicMock()
    
    mock_aqt = MagicMock()
    mock_aqt.mw = MagicMock()
    mock_aqt.mw.addonManager = MagicMock()
    mock_aqt.mw.addonManager.getConfig = MagicMock(return_value={})
    mock_aqt.mw.col = MagicMock()
    mock_aqt.mw.col.models = MagicMock()
    mock_aqt.mw.col.models.all_names_and_ids = MagicMock(return_value=[
        type('NoteType', (), {'name': 'Test Note Type', 'id': 1234567890})()
    ])
    mock_aqt.mw.col.models.get = MagicMock(return_value={
        'name': 'Test Note Type',
        'id': 1234567890,
        'css': '.card { font-family: arial; }',
        'tmpls': [
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
                'ord': 0
            }
        ],
        'flds': [
            {'name': 'Front', 'ord': 0},
            {'name': 'Back', 'ord': 1}
        ]
    })
    mock_aqt.gui_hooks = MagicMock()
    mock_aqt.utils = MagicMock()
    
    # Mock aqt.qt to use real PyQt6
    mock_aqt_qt = MagicMock()
    # Map PyQt6 classes so imports work
    mock_aqt_qt.QWidget = QtWidgets.QWidget
    mock_aqt_qt.QDialog = QtWidgets.QDialog
    mock_aqt_qt.QVBoxLayout = QtWidgets.QVBoxLayout
    mock_aqt_qt.QHBoxLayout = QtWidgets.QHBoxLayout
    mock_aqt_qt.QPushButton = QtWidgets.QPushButton
    mock_aqt_qt.QLabel = QtWidgets.QLabel
    mock_aqt_qt.QTextEdit = QtWidgets.QTextEdit
    mock_aqt_qt.QPlainTextEdit = QtWidgets.QPlainTextEdit
    mock_aqt_qt.QComboBox = QtWidgets.QComboBox
    mock_aqt_qt.QTreeWidget = QtWidgets.QTreeWidget
    mock_aqt_qt.QTreeWidgetItem = QtWidgets.QTreeWidgetItem
    mock_aqt_qt.QSplitter = QtWidgets.QSplitter
    mock_aqt_qt.QTabWidget = QtWidgets.QTabWidget
    mock_aqt_qt.QScrollArea = QtWidgets.QScrollArea
    mock_aqt_qt.QCheckBox = QtWidgets.QCheckBox
    mock_aqt_qt.QLineEdit = QtWidgets.QLineEdit
    mock_aqt_qt.QSpinBox = QtWidgets.QSpinBox
    mock_aqt_qt.QSlider = QtWidgets.QSlider
    mock_aqt_qt.QFrame = QtWidgets.QFrame
    mock_aqt_qt.QGroupBox = QtWidgets.QGroupBox
    mock_aqt_qt.QToolBar = QtWidgets.QToolBar
    mock_aqt_qt.QListWidget = QtWidgets.QListWidget
    mock_aqt_qt.QListWidgetItem = QtWidgets.QListWidgetItem
    mock_aqt_qt.QAction = QtGui.QAction
    mock_aqt_qt.Qt = QtCore.Qt
    mock_aqt_qt.QColor = QtGui.QColor
    mock_aqt_qt.QPainter = QtGui.QPainter
    mock_aqt_qt.QBrush = QtGui.QBrush
    mock_aqt_qt.QPen = QtGui.QPen
    mock_aqt_qt.QFont = QtGui.QFont
    mock_aqt_qt.QRect = QtCore.QRect
    mock_aqt_qt.QPoint = QtCore.QPoint
    mock_aqt_qt.QSize = QtCore.QSize
    mock_aqt_qt.pyqtSignal = QtCore.pyqtSignal
    mock_aqt_qt.QWebEngineView = QWebEngineView
    mock_aqt_qt.QWebEngineSettings = QWebEngineSettings
    
    # Install mocks
    sys.modules['anki'] = mock_anki
    sys.modules['anki._backend'] = mock_anki._backend
    sys.modules['anki._rsbridge'] = mock_anki._rsbridge
    sys.modules['anki.lang'] = mock_anki.lang
    sys.modules['aqt'] = mock_aqt
    sys.modules['aqt.utils'] = mock_aqt.utils
    sys.modules['aqt.qt'] = mock_aqt_qt
    sys.modules['aqt.theme'] = MagicMock()
    sys.modules['aqt.webview'] = MagicMock()
    sys.modules['aqt.editor'] = MagicMock()

# Set up mocks first
setup_anki_mocks()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
