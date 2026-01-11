"""Run UI tests with real Anki installation

This script runs UI tests that interact with the actual Anki application
installed on the system.

Usage:
    python run_ui_tests.py                  # Run all UI tests
    python run_ui_tests.py --fast          # Skip slow tests
    python run_ui_tests.py --verbose       # Verbose output
    python run_ui_tests.py --no-anki       # Skip tests requiring Anki process
"""

import sys
import argparse
from pathlib import Path
import subprocess

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(description='Run UI tests with real Anki')
    parser.add_argument('--fast', action='store_true', 
                       help='Skip slow tests (marked with @pytest.mark.slow)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose test output')
    parser.add_argument('--no-anki', action='store_true',
                       help='Skip tests that require Anki process')
    parser.add_argument('--test', '-k', type=str,
                       help='Run specific test by name pattern')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML test report')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest', 'tests/ui']
    
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    if args.fast:
        cmd.extend(['-m', 'not slow'])
    
    if args.no_anki:
        # Skip tests that use anki_process fixture
        cmd.extend(['-k', 'not anki_process'])
    
    if args.test:
        cmd.extend(['-k', args.test])
    
    if args.coverage:
        cmd.extend(['--cov=.', '--cov-report=term-missing'])
        if args.html_report:
            cmd.append('--cov-report=html')
    
    # Add useful pytest options
    cmd.extend([
        '--tb=short',           # Shorter traceback format
        '--strict-markers',     # Ensure all markers are registered
        '--color=yes'           # Colored output
    ])
    
    print(f"\n{'='*70}")
    print("Running UI Tests with Real Anki")
    print(f"{'='*70}\n")
    print(f"Command: {' '.join(cmd)}\n")
    
    # Run tests
    result = subprocess.run(cmd, cwd=project_root)
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
