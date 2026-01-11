# 03a - GrapeJS Setup: Auto-Downloader and Asset Management

> **Purpose**: Detail the auto-downloader implementation and asset management for GrapeJS.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

GrapeJS files are downloaded at runtime to avoid committing large vendor files to git. The downloader checks for required assets on addon initialization and downloads them from unpkg CDN if missing.

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
├── .gitignore              # Ignore downloaded files
├── grapesjs/
│   ├── .gitkeep            # Keep folder in git
│   ├── grapes.min.js       # Downloaded (gitignored)
│   ├── grapes.min.css      # Downloaded (gitignored)
│   └── plugins/            # Optional plugins
│       └── .gitkeep
└── index.html              # Main editor HTML
```

### `.gitignore` Content

```gitignore
# GrapeJS downloaded assets - do not commit
grapesjs/*.js
grapesjs/*.css
grapesjs/plugins/*.js
!grapesjs/.gitkeep
!grapesjs/plugins/.gitkeep
```

---

## Downloader Implementation

### `services/downloader.py`

```python
"""Auto-downloader for GrapeJS assets."""
import urllib.request
import urllib.error
import ssl
import hashlib
from pathlib import Path
from typing import Optional, Callable
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
    Download GrapeJS assets if not present.
    
    Usage:
        downloader = GrapeJSDownloader()
        if not downloader.assets_exist():
            downloader.download_assets(progress_callback=my_callback)
    """
    
    # Version pinned for stability
    GRAPESJS_VERSION = "0.21.10"
    BASE_URL = f"https://unpkg.com/grapesjs@{GRAPESJS_VERSION}"
    
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
            url="https://unpkg.com/grapesjs-blocks-basic@1.0.2",
            filename="plugins/gjs-blocks-basic.min.js",
            required=False
        ),
        Asset(
            url="https://unpkg.com/grapesjs-plugin-forms@2.0.6",
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
    
    def assets_exist(self, include_plugins: bool = False) -> bool:
        """Check if all required assets exist."""
        assets = self.CORE_ASSETS.copy()
        if include_plugins:
            assets.extend(self.PLUGIN_ASSETS)
        
        for asset in assets:
            if not asset.required:
                continue
            filepath = self.assets_dir / asset.filename
            if not filepath.exists():
                return False
        return True
    
    def download_assets(
        self, 
        include_plugins: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        timeout: int = 30
    ) -> list[str]:
        """
        Download all required assets.
        
        Args:
            include_plugins: Whether to download optional plugins
            progress_callback: Called with (current, total, filename)
            timeout: Download timeout in seconds
            
        Returns:
            List of downloaded filenames
            
        Raises:
            RuntimeError: If required download fails
        """
        # Ensure directories exist
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep files
        (self.assets_dir / ".gitkeep").touch()
        (self.plugins_dir / ".gitkeep").touch()
        
        # Collect assets to download
        assets = self.CORE_ASSETS.copy()
        if include_plugins:
            assets.extend(self.PLUGIN_ASSETS)
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        downloaded = []
        for i, asset in enumerate(assets):
            filepath = self.assets_dir / asset.filename
            
            if progress_callback:
                progress_callback(i + 1, len(assets), asset.filename)
            
            if filepath.exists():
                downloaded.append(asset.filename)
                continue
            
            try:
                self._download_file(asset.url, filepath, ssl_context, timeout)
                
                # Verify integrity if hash provided
                if asset.sha256:
                    if not self._verify_hash(filepath, asset.sha256):
                        filepath.unlink()
                        raise RuntimeError(f"Integrity check failed: {asset.filename}")
                
                downloaded.append(asset.filename)
                
            except Exception as e:
                if asset.required:
                    raise RuntimeError(f"Failed to download {asset.filename}: {e}")
                # Log warning for optional assets
                print(f"Warning: Could not download optional {asset.filename}: {e}")
        
        return downloaded
    
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
                    headers={"User-Agent": "AnkiTemplateDesigner/2.0"}
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
    
    def get_js_path(self) -> Path:
        """Get path to GrapeJS JavaScript file."""
        return self.assets_dir / "grapes.min.js"
    
    def get_css_path(self) -> Path:
        """Get path to GrapeJS CSS file."""
        return self.assets_dir / "grapes.min.css"
    
    def clear_cache(self):
        """Remove all downloaded assets."""
        import shutil
        if self.assets_dir.exists():
            for f in self.assets_dir.glob("*.js"):
                f.unlink()
            for f in self.assets_dir.glob("*.css"):
                f.unlink()
            if self.plugins_dir.exists():
                shutil.rmtree(self.plugins_dir)
                self.plugins_dir.mkdir()
                (self.plugins_dir / ".gitkeep").touch()
```

---

## Progress Dialog Integration

### Show Download Progress in Qt

```python
"""Download progress dialog for GrapeJS assets."""
from aqt.qt import QDialog, QVBoxLayout, QLabel, QProgressBar
from aqt import mw

class DownloadProgressDialog(QDialog):
    """Show download progress for GrapeJS assets."""
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Downloading GrapeJS...")
        self.setModal(True)
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Initializing...")
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        layout.addWidget(self.progress)
    
    def update_progress(self, current: int, total: int, filename: str):
        """Update progress display."""
        percent = int((current / total) * 100)
        self.progress.setValue(percent)
        self.label.setText(f"Downloading: {filename}")
        # Process events to update UI
        from aqt.qt import QApplication
        QApplication.processEvents()


def ensure_grapejs_assets() -> bool:
    """
    Ensure GrapeJS assets are downloaded.
    Shows progress dialog if download needed.
    
    Returns:
        True if assets are available, False on failure
    """
    from ..services.downloader import GrapeJSDownloader
    
    downloader = GrapeJSDownloader()
    
    if downloader.assets_exist():
        return True
    
    # Show progress dialog
    dialog = DownloadProgressDialog()
    dialog.show()
    
    try:
        downloader.download_assets(
            progress_callback=dialog.update_progress
        )
        dialog.close()
        return True
        
    except RuntimeError as e:
        dialog.close()
        from aqt.utils import showWarning
        showWarning(
            f"Failed to download GrapeJS assets:\n\n{e}\n\n"
            "Please check your internet connection and try again.",
            title="Download Error"
        )
        return False
```

---

## Initialization Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADDON INITIALIZATION                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ profile_did_open  │
                    │      hook         │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   setup_menu()    │
                    └─────────┬─────────┘
                              │
                              ▼
            User clicks "Template Designer" menu
                              │
                              ▼
                    ┌───────────────────┐
                    │ assets_exist()?   │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
        ┌───────────┐                 ┌───────────────┐
        │    Yes    │                 │      No       │
        └─────┬─────┘                 └───────┬───────┘
              │                               │
              │                               ▼
              │                     ┌───────────────────┐
              │                     │ Show Progress     │
              │                     │ Dialog            │
              │                     └─────────┬─────────┘
              │                               │
              │                               ▼
              │                     ┌───────────────────┐
              │                     │ download_assets() │
              │                     └─────────┬─────────┘
              │                               │
              │                    ┌──────────┴──────────┐
              │                    │                     │
              │                    ▼                     ▼
              │              ┌──────────┐         ┌──────────┐
              │              │ Success  │         │ Failure  │
              │              └────┬─────┘         └────┬─────┘
              │                   │                    │
              │◀──────────────────┘                    ▼
              │                              ┌───────────────┐
              │                              │ Show Error    │
              │                              │ Return        │
              │                              └───────────────┘
              ▼
    ┌───────────────────┐
    │ Open Designer     │
    │ Dialog            │
    └───────────────────┘
```

---

## Offline Mode Considerations

### Cached Assets Check

```python
def can_run_offline(self) -> bool:
    """Check if addon can run without internet."""
    return self.assets_exist()

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
```

---

## Error Handling

### Network Errors

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

### User-Friendly Messages

| Error Type | User Message |
|------------|--------------|
| NetworkError | "Cannot connect to download server. Please check your internet connection." |
| TimeoutError | "Download timed out. The server may be slow or unavailable." |
| IntegrityError | "Downloaded file appears corrupted. Please try again." |
| PermissionError | "Cannot write to addon folder. Please check folder permissions." |

---

## Testing the Downloader

### Unit Test

```python
"""Tests for GrapeJS downloader."""
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from services.downloader import GrapeJSDownloader

class TestGrapeJSDownloader:
    
    def test_assets_exist_false_when_empty(self):
        with TemporaryDirectory() as tmpdir:
            downloader = GrapeJSDownloader(Path(tmpdir))
            assert downloader.assets_exist() is False
    
    def test_download_creates_files(self):
        with TemporaryDirectory() as tmpdir:
            downloader = GrapeJSDownloader(Path(tmpdir))
            downloaded = downloader.download_assets()
            
            assert len(downloaded) >= 2
            assert downloader.assets_exist() is True
            assert downloader.get_js_path().exists()
            assert downloader.get_css_path().exists()
    
    def test_clear_cache(self):
        with TemporaryDirectory() as tmpdir:
            downloader = GrapeJSDownloader(Path(tmpdir))
            downloader.download_assets()
            
            assert downloader.assets_exist() is True
            
            downloader.clear_cache()
            
            assert downloader.assets_exist() is False
```

---

## Next Document

See [03b-GRAPEJS-EDITOR.md](03b-GRAPEJS-EDITOR.md) for GrapeJS editor initialization and configuration.
