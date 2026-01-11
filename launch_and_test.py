"""
Launch Anki and test the Template Designer addon

This script:
1. Starts Anki
2. Waits for it to initialize
3. Provides instructions for testing
"""

import subprocess
import time
import sys
from pathlib import Path

ANKI_EXE = Path(r"C:\Users\Colin\AppData\Local\Programs\Anki\anki.exe")

def launch_anki():
    """Launch Anki and provide testing instructions"""
    
    print("\n" + "="*70)
    print("Launching Anki for Template Designer Testing")
    print("="*70 + "\n")
    
    # Check if Anki exists
    if not ANKI_EXE.exists():
        print(f"❌ Error: Anki not found at:")
        print(f"   {ANKI_EXE}")
        return False
    
    print(f"✓ Anki found: {ANKI_EXE}")
    print(f"\n🚀 Starting Anki...")
    
    try:
        # Start Anki
        process = subprocess.Popen(
            [str(ANKI_EXE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✓ Anki process started (PID: {process.pid})")
        
        # Wait a bit for Anki to start
        print(f"\n⏳ Waiting for Anki to initialize...")
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✓ Anki is running")
        else:
            print(f"⚠ Anki process exited early")
            return False
        
        # Show testing instructions
        print("\n" + "="*70)
        print("TESTING INSTRUCTIONS")
        print("="*70 + "\n")
        
        print("📋 STEP 1: Verify Addon is Loaded")
        print("   1. In Anki, go to: Tools > Add-ons")
        print("   2. Look for 'Anki Template Designer' in the list")
        print("   3. Check that it's enabled (checkbox checked)")
        print("   4. If not visible, restart Anki\n")
        
        print("📋 STEP 2: Open Template Designer")
        print("   1. Go to: Tools > Anki Template Designer")
        print("   2. Designer dialog should open")
        print("   3. Verify dialog size is reasonable (800x600+)\n")
        
        print("📋 STEP 3: Verify Editor Loads")
        print("   1. Check that GrapeJS editor appears (not blank)")
        print("   2. Look for toolbar at top")
        print("   3. Look for blocks panel on left")
        print("   4. Check browser console for errors (if available)\n")
        
        print("📋 STEP 4: Test Component Blocks")
        print("   1. Expand block categories in left panel:")
        print("      - Layout (25 blocks)")
        print("      - Study Action Bar (1 block)")
        print("      - Inputs (13 blocks)")
        print("      - Buttons (5 blocks)")
        print("      - Data (18 blocks)")
        print("      - Feedback (14 blocks)")
        print("      - Overlays (6 blocks)")
        print("      - Animations (3 blocks)")
        print("      - Accessibility (5 blocks)")
        print("      - Anki Special (3 blocks)")
        print("   2. Verify all categories are visible\n")
        
        print("📋 STEP 5: Test Drag & Drop")
        print("   1. Drag a 'Frame' block to canvas")
        print("   2. Verify it appears in the canvas")
        print("   3. Drag a 'Heading' block into the frame")
        print("   4. Click on blocks to select them")
        print("   5. Check properties panel on right\n")
        
        print("📋 STEP 6: Test Component Properties")
        print("   1. Select a block in canvas")
        print("   2. Properties panel should show traits")
        print("   3. Try modifying properties")
        print("   4. Verify changes appear in canvas\n")
        
        print("📋 STEP 7: Run Tests from Anki Console")
        print("   1. In Anki, press Shift+F1 (or Tools > Debug Console)")
        print("   2. Run these commands:")
        print("      ```python")
        print("      import sys")
        print("      from pathlib import Path")
        print("      addon_dir = Path.home() / 'AppData/Roaming/Anki2/addons21/AnkiTemplateDesigner'")
        print("      sys.path.insert(0, str(addon_dir))")
        print("      exec(open(addon_dir / 'test_in_anki.py').read())")
        print("      test_component_library()")
        print("      ```")
        print("   3. Check test results\n")
        
        print("="*70)
        print("TROUBLESHOOTING")
        print("="*70 + "\n")
        
        print("If addon doesn't appear:")
        print("  - Restart Anki")
        print("  - Check Tools > Add-ons > Check for Updates")
        print("  - Reinstall with: python install_addon.py install\n")
        
        print("If dialog doesn't open:")
        print("  - Check Anki console for errors")
        print("  - Verify all files copied correctly")
        print("  - Check addon directory exists\n")
        
        print("If editor is blank:")
        print("  - Check web/ directory exists in addon")
        print("  - Verify index.html is present")
        print("  - Check browser console for JS errors\n")
        
        print("="*70 + "\n")
        
        print("Press Ctrl+C to stop monitoring...\n")
        
        # Keep script running
        try:
            while process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped")
            print("  (Anki is still running)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching Anki: {e}")
        return False

if __name__ == "__main__":
    success = launch_anki()
    sys.exit(0 if success else 1)
