"""
Test runner for Anki environment

This script is meant to be run from within Anki's addon environment.
Place this in the addon directory and run from Anki's debug console.
"""

def test_component_library():
    """Test component library in Anki environment"""
    import sys
    from pathlib import Path
    
    print("\n" + "="*70)
    print("Testing Anki Template Designer - Component Library")
    print("="*70 + "\n")
    
    results = {
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Test 1: Check web directory exists
    print("TEST 1: Web directory structure")
    try:
        addon_dir = Path(__file__).parent
        web_dir = addon_dir / "web"
        
        if web_dir.exists():
            print(f"  ✓ Web directory exists: {web_dir}")
            results['passed'] += 1
        else:
            print(f"  ✗ Web directory not found: {web_dir}")
            results['failed'] += 1
            results['errors'].append("Web directory missing")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results['failed'] += 1
        results['errors'].append(str(e))
    
    # Test 2: Check key files exist
    print("\nTEST 2: Key web files")
    try:
        required_files = [
            "web/index.html",
            "web/designer.js",
            "web/designer.css",
            "web/bridge.js",
            "web/components/index.js",
            "web/blocks/index.js"
        ]
        
        missing = []
        for file_path in required_files:
            full_path = addon_dir / file_path
            if full_path.exists():
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path}")
                missing.append(file_path)
        
        if not missing:
            results['passed'] += 1
        else:
            results['failed'] += 1
            results['errors'].append(f"Missing files: {', '.join(missing)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results['failed'] += 1
        results['errors'].append(str(e))
    
    # Test 3: Import addon modules
    print("\nTEST 3: Import addon modules")
    try:
        from gui.designer_dialog import DesignerDialog
        print(f"  ✓ DesignerDialog imported")
        
        from gui.webview_bridge import WebViewBridge
        print(f"  ✓ WebViewBridge imported")
        
        from core.models import Template
        print(f"  ✓ Template model imported")
        
        results['passed'] += 1
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        results['failed'] += 1
        results['errors'].append(f"Import error: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results['failed'] += 1
        results['errors'].append(str(e))
    
    # Test 4: Check menu hook
    print("\nTEST 4: Menu hook registration")
    try:
        from hooks.menu import setup_menu
        print(f"  ✓ Menu setup function exists")
        results['passed'] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results['failed'] += 1
        results['errors'].append(str(e))
    
    # Test 5: Try to create dialog instance
    print("\nTEST 5: Create DesignerDialog instance")
    try:
        from aqt import mw
        from gui.designer_dialog import DesignerDialog
        
        if mw is not None:
            dialog = DesignerDialog(mw)
            print(f"  ✓ DesignerDialog instance created")
            print(f"  ✓ Dialog type: {type(dialog).__name__}")
            
            # Check dialog has webview
            if hasattr(dialog, 'webview') or hasattr(dialog, 'web'):
                print(f"  ✓ Dialog has webview component")
            
            dialog.close()
            dialog.deleteLater()
            results['passed'] += 1
        else:
            print(f"  ⚠ Anki main window not available (mw is None)")
            results['failed'] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results['failed'] += 1
        results['errors'].append(str(e))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['errors']:
        print(f"\nErrors:")
        for i, error in enumerate(results['errors'], 1):
            print(f"  {i}. {error}")
    
    if results['failed'] == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {results['failed']} test(s) failed")
    
    print("="*70 + "\n")
    
    return results['failed'] == 0


# For running from Anki debug console:
# exec(open('test_in_anki.py').read())
# test_component_library()

if __name__ == "__main__":
    test_component_library()
