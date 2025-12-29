"""
Build script for creating Anki add-on package
"""

import os
import zipfile
import json
from pathlib import Path


def get_addon_name():
    """Get add-on name from manifest"""
    with open('manifest.json', 'r') as f:
        manifest = json.load(f)
    return manifest['package']


def create_addon_package():
    """Create .ankiaddon package file"""
    addon_name = get_addon_name()
    output_file = f"{addon_name}.ankiaddon"
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        '.gitignore',
        'build.py',
        '*.ankiaddon',
        '.vscode',
        '.idea',
        'meta.json'
    ]
    
    def should_exclude(path):
        """Check if path should be excluded"""
        for pattern in exclude_patterns:
            if pattern in str(path):
                return True
        return False
    
    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if should_exclude(file_path):
                    continue
                
                # Add to zip with relative path
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")
    
    print(f"\nPackage created: {output_file}")
    print(f"Size: {os.path.getsize(output_file) / 1024:.2f} KB")


if __name__ == '__main__':
    create_addon_package()
