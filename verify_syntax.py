"""
Verify all Python files compile without syntax errors
"""
import py_compile
import os
import sys

print("Checking for syntax errors...")
print("=" * 60)

errors = []
checked = 0

for root, dirs, files in os.walk('.'):
    # Skip test directories and venv
    if '.venv' in root or '__pycache__' in root or '.pytest_cache' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                py_compile.compile(filepath, doraise=True)
                checked += 1
            except SyntaxError as e:
                errors.append((filepath, str(e)))
                print(f"❌ {filepath}: {e}")

print("=" * 60)
if errors:
    print(f"\n❌ Found {len(errors)} syntax error(s)")
    for path, error in errors:
        print(f"  - {path}: {error}")
else:
    print(f"\n✅ All {checked} Python files are syntactically correct!")
    print("\nThe addon is ready to use.")
    print("Copy to: C:\\Users\\Colin\\AppData\\Roaming\\Anki2\\addons21\\AnkiTemplateDesigner\\")
    print("Then restart Anki.")
