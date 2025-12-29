#!/usr/bin/env python
"""
Test runner script for Anki Template Designer

Usage:
    python run_tests.py                 # Run all tests
    python run_tests.py --unit          # Run only unit tests
    python run_tests.py --integration   # Run only integration tests
    python run_tests.py --coverage      # Run with coverage report
    python run_tests.py --verbose       # Verbose output
    python run_tests.py --quick         # Run quick tests only (skip slow)
"""
import sys
import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Run tests for Anki Template Designer')
    
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--e2e', action='store_true', help='Run only end-to-end tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--html-cov', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quick', action='store_true', help='Skip slow tests')
    parser.add_argument('--parallel', '-n', type=int, help='Run tests in parallel (specify number of workers)')
    parser.add_argument('--failed', action='store_true', help='Run only previously failed tests')
    parser.add_argument('--pdb', action='store_true', help='Drop into debugger on failure')
    parser.add_argument('--markers', '-m', type=str, help='Run tests matching markers (e.g., "unit and not slow")')
    parser.add_argument('tests', nargs='*', help='Specific test files or patterns to run')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['pytest']
    
    # Add test path based on category
    if args.unit:
        cmd.append('tests/unit/')
    elif args.integration:
        cmd.append('tests/integration/')
    elif args.e2e:
        cmd.append('tests/integration/test_e2e_workflows.py')
    elif args.tests:
        cmd.extend(args.tests)
    else:
        cmd.append('tests/')
    
    # Add coverage options
    if args.coverage or args.html_cov:
        cmd.extend(['--cov=ui', '--cov=utils'])
        
        if args.html_cov:
            cmd.append('--cov-report=html')
        else:
            cmd.append('--cov-report=term-missing')
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # Add quick mode (skip slow tests)
    if args.quick:
        cmd.extend(['-m', 'not slow'])
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(['-n', str(args.parallel)])
    
    # Run only failed tests
    if args.failed:
        cmd.append('--lf')
    
    # Debugger on failure
    if args.pdb:
        cmd.append('--pdb')
    
    # Custom markers
    if args.markers:
        cmd.extend(['-m', args.markers])
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run pytest
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        
        # Open HTML coverage report if generated
        if args.html_cov and result.returncode == 0:
            cov_report = Path(__file__).parent.parent / 'htmlcov' / 'index.html'
            if cov_report.exists():
                print(f"\nCoverage report generated: {cov_report}")
                print("Opening in browser...")
                
                if sys.platform == 'win32':
                    subprocess.run(['start', str(cov_report)], shell=True)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', str(cov_report)])
                else:
                    subprocess.run(['xdg-open', str(cov_report)])
        
        return result.returncode
    
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user")
        return 130


if __name__ == '__main__':
    sys.exit(main())
