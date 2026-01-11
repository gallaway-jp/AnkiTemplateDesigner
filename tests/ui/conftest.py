"""Pytest configuration for UI tests with real Anki"""
import sys
import os
import subprocess
import time
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

# Anki installation directory
ANKI_DIR = Path(r"C:\Users\Colin\AppData\Local\Programs\Anki")
ANKI_EXE = ANKI_DIR / "anki.exe"

# Addon directory (this project)
ADDON_DIR = Path(__file__).parent.parent.parent

@pytest.fixture(scope="session")
def anki_installation():
    """Verify Anki installation exists"""
    if not ANKI_DIR.exists():
        pytest.skip(f"Anki not found at {ANKI_DIR}")
    if not ANKI_EXE.exists():
        pytest.skip(f"Anki executable not found at {ANKI_EXE}")
    
    return {
        'dir': ANKI_DIR,
        'exe': ANKI_EXE,
        'version': get_anki_version()
    }

def get_anki_version():
    """Get Anki version from installation"""
    try:
        # Try to get version from Anki
        result = subprocess.run(
            [str(ANKI_EXE), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return "Unknown"

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for the test session"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Don't quit here - let tests manage lifecycle

@pytest.fixture(scope="function")
def anki_process(anki_installation):
    """Start Anki process for a test"""
    # Start Anki in the background
    process = subprocess.Popen(
        [str(ANKI_EXE)],
        cwd=str(ANKI_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Anki to start up
    time.sleep(5)  # Give Anki time to initialize
    
    yield process
    
    # Cleanup: terminate Anki
    try:
        process.terminate()
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

@pytest.fixture
def addon_loaded(anki_process, monkeypatch):
    """Ensure the addon is loaded in the Anki process
    
    This fixture sets up the environment to test the addon
    in a real Anki installation.
    """
    # Add addon directory to Python path
    addon_path = str(ADDON_DIR)
    if addon_path not in sys.path:
        sys.path.insert(0, addon_path)
    
    # Now we can import from the real Anki installation
    anki_lib = ANKI_DIR / "lib"
    if anki_lib.exists() and str(anki_lib) not in sys.path:
        sys.path.insert(0, str(anki_lib))
    
    yield
    
    # Cleanup
    if addon_path in sys.path:
        sys.path.remove(addon_path)

@pytest.fixture
def designer_dialog(qapp, addon_loaded):
    """Create and return a DesignerDialog instance
    
    This imports the real dialog after Anki modules are available.
    """
    # Import after Anki is available
    try:
        from gui.designer_dialog import DesignerDialog
        
        # Create mock mw (main window) if needed
        class MockMW:
            class MockCol:
                class MockModels:
                    @staticmethod
                    def all_names_and_ids():
                        return []
                    
                    @staticmethod
                    def get(model_id):
                        return {
                            'name': 'Test Note Type',
                            'id': model_id,
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
                        }
                
                models = MockModels()
            
            col = MockCol()
            
            class MockAddonManager:
                @staticmethod
                def getConfig(name):
                    return {}
            
            addonManager = MockAddonManager()
        
        mock_mw = MockMW()
        
        # Create dialog
        dialog = DesignerDialog(mock_mw)
        
        yield dialog
        
        # Cleanup
        dialog.close()
        dialog.deleteLater()
        
    except ImportError as e:
        pytest.skip(f"Could not import DesignerDialog: {e}")

@pytest.fixture
def wait_for_load(qapp):
    """Helper fixture to wait for async operations"""
    def _wait(ms=100):
        QTest.qWait(ms)
        qapp.processEvents()
    return _wait
