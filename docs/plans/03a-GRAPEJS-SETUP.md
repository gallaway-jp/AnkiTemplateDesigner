# 03a - GrapeJS Setup: Build Script and Asset Management

> **Purpose**: Detail the build script implementation and asset management for GrapeJS.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

GrapeJS files are included in the addon release but downloaded via a build script for source code maintenance. The build script downloads assets from unpkg CDN and commits them to git for distribution. This approach ensures:

- Clean separation between development and runtime
- Reliable asset availability in releases
- Easy version updates during development
- No runtime network dependencies

---

## Asset URLs and Versions

### Required Files

| File | URL | Size (approx) |
|------|-----|---------------|
| grapes.min.js | https://unpkg.com/grapesjs@0.21.10/dist/grapes.min.js | ~450KB |
| grapes.min.css | https://unpkg.com/grapesjs@0.21.10/dist/css/grapes.min.css | ~50KB |

### Optional Plugins

| Plugin | URL | Purpose |
|--------|-----|---------|
| gjs-blocks-basic | https://unpkg.com/grapesjs-blocks-basic | Basic HTML blocks |
| gjs-preset-webpage | https://unpkg.com/grapesjs-preset-webpage | Webpage editing preset |
| gjs-plugin-forms | https://unpkg.com/grapesjs-plugin-forms | Form components |

---

## Folder Structure

```
web/
├── grapesjs/
│   ├── grapes.min.js       # Committed to git
│   ├── grapes.min.css      # Committed to git
│   └── plugins/            # Optional plugins
│       ├── gjs-blocks-basic.min.js
│       └── gjs-plugin-forms.min.js
└── index.html              # Main editor HTML
```

### `.gitignore` Content

```gitignore
# No GrapeJS files ignored - they are committed to git
# Build artifacts can be ignored if needed
build/
dist/
*.pyc
__pycache__/
```

---

## Build Script Implementation

### `scripts/download_grapejs.py`

```python
"""Build script to download GrapeJS assets for development and releases."""
import urllib.request
import urllib.error
import ssl
import hashlib
import argparse
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class Asset:
    """Represents a downloadable asset."""
    url: str
    filename: str
    sha256: Optional[str] = None  # Optional integrity check
    required: bool = True

class GrapeJSDownloader:
    """
    Download GrapeJS assets for build process.
    
    Usage:
        python scripts/download_grapejs.py
        python scripts/download_grapejs.py --plugins
        python scripts/download_grapejs.py --verify-only
    """
    
    # Version pinned for stability
    GRAPESJS_VERSION = "0.21.10"
    
    CORE_ASSETS = [
        Asset(
            url=f"https://unpkg.com/grapesjs@{GRAPESJS_VERSION}/dist/grapes.min.js",
            filename="grapes.min.js",
            required=True
        ),
        Asset(
            url=f"https://unpkg.com/grapesjs@{GRAPESJS_VERSION}/dist/css/grapes.min.css",
            filename="grapes.min.css", 
            required=True
        ),
    ]
    
    PLUGIN_ASSETS = [
        Asset(
            url="https://unpkg.com/grapesjs-blocks-basic@1.0.2/dist/grapesjs-blocks-basic.min.js",
            filename="plugins/gjs-blocks-basic.min.js",
            required=False
        ),
        Asset(
            url="https://unpkg.com/grapesjs-plugin-forms@2.0.6/dist/grapesjs-plugin-forms.min.js",
            filename="plugins/gjs-plugin-forms.min.js",
            required=False
        ),
    ]
    
    def __init__(self, addon_path: Optional[Path] = None):
        if addon_path is None:
            addon_path = Path(__file__).parent.parent
        self.addon_path = addon_path
        self.assets_dir = addon_path / "web" / "grapesjs"
        self.plugins_dir = self.assets_dir / "plugins"
    
    def download_assets(
        self, 
        include_plugins: bool = False,
        force: bool = False,
        timeout: int = 30
    ) -> list[str]:
        """
        Download all required assets.
        
        Args:
            include_plugins: Whether to download optional plugins
            force: Force re-download even if files exist
            timeout: Download timeout in seconds
            
        Returns:
            List of downloaded filenames
            
        Raises:
            RuntimeError: If required download fails
        """
        # Ensure directories exist
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect assets to download
        assets = self.CORE_ASSETS.copy()
        if include_plugins:
            assets.extend(self.PLUGIN_ASSETS)
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        downloaded = []
        for asset in assets:
            filepath = self.assets_dir / asset.filename
            
            if filepath.exists() and not force:
                print(f"✓ {asset.filename} already exists")
                downloaded.append(asset.filename)
                continue
            
            print(f"Downloading {asset.filename}...")
            try:
                self._download_file(asset.url, filepath, ssl_context, timeout)
                
                # Verify integrity if hash provided
                if asset.sha256:
                    if not self._verify_hash(filepath, asset.sha256):
                        filepath.unlink()
                        raise RuntimeError(f"Integrity check failed: {asset.filename}")
                
                downloaded.append(asset.filename)
                print(f"✓ Downloaded {asset.filename}")
                
            except Exception as e:
                if asset.required:
                    raise RuntimeError(f"Failed to download {asset.filename}: {e}")
                # Log warning for optional assets
                print(f"⚠ Could not download optional {asset.filename}: {e}")
        
        return downloaded
    
    def verify_assets(self, include_plugins: bool = False) -> bool:
        """
        Verify all assets exist and are valid.
        
        Returns:
            True if all required assets exist
        """
        assets = self.CORE_ASSETS.copy()
        if include_plugins:
            assets.extend(self.PLUGIN_ASSETS)
        
        missing = []
        for asset in assets:
            if not asset.required:
                continue
            filepath = self.assets_dir / asset.filename
            if not filepath.exists():
                missing.append(asset.filename)
        
        if missing:
            print(f"Missing required assets: {', '.join(missing)}")
            return False
        
        print("✓ All required assets present")
        return True
    
    def _download_file(
        self, 
        url: str, 
        filepath: Path, 
        ssl_context: ssl.SSLContext,
        timeout: int
    ):
        """Download a single file with retry logic."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "AnkiTemplateDesigner-Build/2.0"}
                )
                
                with urllib.request.urlopen(
                    request, 
                    context=ssl_context, 
                    timeout=timeout
                ) as response:
                    content = response.read()
                    
                    # Ensure parent directory exists
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    filepath.write_bytes(content)
                    return
                    
            except urllib.error.URLError as e:
                if attempt == max_retries - 1:
                    raise
                # Wait before retry
                import time
                time.sleep(1 * (attempt + 1))
    
    def _verify_hash(self, filepath: Path, expected_hash: str) -> bool:
        """Verify file SHA256 hash."""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_hash
    
    def get_asset_info(self) -> dict:
        """Get information about downloaded assets."""
        info = {
            "version": self.GRAPESJS_VERSION,
            "assets": [],
            "missing": [],
            "total_size": 0
        }
        
        for asset in self.CORE_ASSETS + self.PLUGIN_ASSETS:
            filepath = self.assets_dir / asset.filename
            if filepath.exists():
                size = filepath.stat().st_size
                info["assets"].append({
                    "filename": asset.filename,
                    "size": size,
                    "required": asset.required
                })
                info["total_size"] += size
            elif asset.required:
                info["missing"].append(asset.filename)
        
        return info


def main():
    """Command line interface for the build script."""
    parser = argparse.ArgumentParser(
        description="Download GrapeJS assets for Anki Template Designer"
    )
    parser.add_argument(
        "--plugins", 
        action="store_true",
        help="Include optional plugins"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force re-download even if files exist"
    )
    parser.add_argument(
        "--verify-only", 
        action="store_true",
        help="Only verify assets exist, don't download"
    )
    parser.add_argument(
        "--info", 
        action="store_true",
        help="Show asset information"
    )
    
    args = parser.parse_args()
    
    downloader = GrapeJSDownloader()
    
    try:
        if args.info:
            info = downloader.get_asset_info()
            print(f"GrapeJS Version: {info['version']}")
            print(f"Total Size: {info['total_size'] / 1024:.1f} KB")
            print(f"Assets: {len(info['assets'])}")
            if info['missing']:
                print(f"Missing: {', '.join(info['missing'])}")
            return
        
        if args.verify_only:
            success = downloader.verify_assets(args.plugins)
            sys.exit(0 if success else 1)
        
        downloaded = downloader.download_assets(
            include_plugins=args.plugins,
            force=args.force
        )
        
        print(f"\n✓ Downloaded {len(downloaded)} assets successfully")
        
        # Show asset info
        info = downloader.get_asset_info()
        print(f"Total size: {info['total_size'] / 1024:.1f} KB")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Usage Instructions

### Development Setup

```bash
# Download core GrapeJS files
python scripts/download_grapejs.py

# Download with optional plugins
python scripts/download_grapejs.py --plugins

# Force re-download all files
python scripts/download_grapejs.py --force

# Verify assets exist
python scripts/download_grapejs.py --verify-only

# Show asset information
python scripts/download_grapejs.py --info
```

### Release Process

```bash
# Ensure all assets are downloaded and committed
python scripts/download_grapejs.py --plugins
git add web/grapesjs/
git commit -m "Update GrapeJS assets to v0.21.10"
```

### CI/CD Integration

```yaml
# .github/workflows/release.yml
- name: Download GrapeJS assets
  run: python scripts/download_grapejs.py --plugins

- name: Verify assets
  run: python scripts/download_grapejs.py --verify-only
```

---

## Build Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     BUILD PROCESS                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Run Build Script  │
                    │ download_grapejs.py│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Download Assets   │
                    │ from unpkg CDN    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Verify Integrity  │
                    │ (optional hashes) │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
        ┌───────────┐                 ┌───────────────┐
        │ Success   │                 │   Failure    │
        └─────┬─────┘                 └───────┬───────┘
              │                               │
              ▼                               ▼
    ┌───────────────────┐           ┌───────────────────┐
    │ Commit to Git     │           │ Show Error        │
    │ web/grapesjs/     │           │ Exit with error   │
    └───────────────────┘           └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Create Release    │
                    │ Package           │
                    └───────────────────┘
```

---

## Asset Management

### Version Control Strategy

- **Core files** (`grapes.min.js`, `grapes.min.css`) are committed to git
- **Plugins** are optional and committed when included
- **Version pinning** ensures reproducible builds
- **Integrity verification** optional for security-critical deployments

### Updating GrapeJS Versions

```bash
# Update version in download_grapejs.py
GRAPESJS_VERSION = "0.21.11"  # New version

# Download new assets
python scripts/download_grapejs.py --force

# Test the new version
# ... run tests ...

# Commit the update
git add web/grapesjs/ scripts/download_grapejs.py
git commit -m "Update GrapeJS to v0.21.11"
```

### Asset Verification

```python
def verify_runtime_assets() -> bool:
    """
    Verify assets exist at runtime (no downloads).
    Called during addon initialization.
    """
    addon_path = Path(__file__).parent.parent
    assets_dir = addon_path / "web" / "grapesjs"
    
    required_files = [
        "grapes.min.js",
        "grapes.min.css"
    ]
    
    for filename in required_files:
        if not (assets_dir / filename).exists():
            return False
    
    return True
```

---

## Error Handling

### Build Script Errors

```python
class DownloadError(Exception):
    """Base exception for download errors."""
    pass

class NetworkError(DownloadError):
    """Network connectivity error."""
    pass

class IntegrityError(DownloadError):
    """File integrity check failed."""
    pass

class TimeoutError(DownloadError):
    """Download timed out."""
    pass
```

### Build Failure Scenarios

| Error Type | Cause | Resolution |
|------------|-------|------------|
| NetworkError | No internet or CDN down | Retry later, check connection |
| TimeoutError | Slow connection | Increase timeout, retry |
| IntegrityError | Corrupted download | Re-download with --force |
| PermissionError | Cannot write files | Check folder permissions |

### CI/CD Error Handling

```yaml
# .github/workflows/build.yml
- name: Download GrapeJS assets
  run: python scripts/download_grapejs.py --plugins
  continue-on-error: false  # Fail build if download fails

- name: Verify assets
  run: python scripts/download_grapejs.py --verify-only
```

---

## Testing the Build Script

### Unit Tests

```python
"""Tests for GrapeJS build script."""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from scripts.download_grapejs import GrapeJSDownloader, Asset

class TestGrapeJSDownloader:
    
    def test_verify_assets_missing_files(self, tmp_path):
        downloader = GrapeJSDownloader(tmp_path)
        assert downloader.verify_assets() is False
    
    @patch('urllib.request.urlopen')
    def test_download_assets_success(self, mock_urlopen, tmp_path):
        # Mock successful download
        mock_response = mock_open(read_data=b'fake content')
        mock_urlopen.return_value.__enter__.return_value = mock_response()
        
        downloader = GrapeJSDownloader(tmp_path)
        downloaded = downloader.download_assets()
        
        assert len(downloaded) >= 2
        assert (tmp_path / "web" / "grapesjs" / "grapes.min.js").exists()
    
    def test_get_asset_info(self, tmp_path):
        downloader = GrapeJSDownloader(tmp_path)
        
        # Create fake files
        js_file = tmp_path / "web" / "grapesjs" / "grapes.min.js"
        js_file.parent.mkdir(parents=True)
        js_file.write_text("fake js content")
        
        info = downloader.get_asset_info()
        assert info["version"] == "0.21.10"
        assert len(info["assets"]) == 1
        assert info["assets"][0]["filename"] == "grapes.min.js"
```

### Integration Tests

```bash
# Test script functionality
python scripts/download_grapejs.py --verify-only  # Should fail initially
python scripts/download_grapejs.py               # Download assets
python scripts/download_grapejs.py --verify-only  # Should pass
python scripts/download_grapejs.py --info         # Show asset info
```

### CI/CD Testing

```yaml
# .github/workflows/test.yml
- name: Test build script
  run: |
    python scripts/download_grapejs.py --verify-only && exit 1 || echo "Expected failure"
    python scripts/download_grapejs.py
    python scripts/download_grapejs.py --verify-only
    python scripts/download_grapejs.py --info
```

---

## Next Document

See [03b-GRAPEJS-EDITOR.md](03b-GRAPEJS-EDITOR.md) for GrapeJS editor initialization and configuration.
