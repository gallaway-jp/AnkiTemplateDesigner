"""Auto-downloader for GrapeJS assets.

This module handles automatic downloading of GrapeJS library files from unpkg.com
if they are not already present in the web/grapesjs/ directory.
"""

import urllib.request
import ssl
from pathlib import Path
from typing import Optional, Callable


class GrapeJSDownloader:
    """Download GrapeJS assets if not present.
    
    Downloads GrapeJS library files from unpkg.com CDN to local web/grapesjs/ folder.
    Files are gitignored to avoid bloating the repository.
    """
    
    # Assets to download from unpkg.com
    ASSETS = [
        {
            "url": "https://unpkg.com/grapesjs@0.21.10/dist/grapes.min.js",
            "filename": "grapes.min.js",
            "description": "GrapeJS core library"
        },
        {
            "url": "https://unpkg.com/grapesjs@0.21.10/dist/css/grapes.min.css",
            "filename": "grapes.min.css",
            "description": "GrapeJS default styles"
        }
    ]
    
    def __init__(self):
        """Initialize downloader with paths to addon web assets."""
        self.addon_path = Path(__file__).parent.parent
        self.assets_dir = self.addon_path / "web" / "grapesjs"
    
    def assets_exist(self) -> bool:
        """Check if all required assets exist.
        
        Returns:
            True if all assets are present, False otherwise
        """
        for asset in self.ASSETS:
            filepath = self.assets_dir / asset["filename"]
            if not filepath.exists():
                return False
        return True
    
    def download_assets(self, progress_callback: Optional[Callable[[int, int, str], None]] = None):
        """Download all required assets from unpkg.com.
        
        Args:
            progress_callback: Optional callback(current, total, filename) for progress updates
            
        Raises:
            RuntimeError: If download fails
        """
        # Ensure directory exists
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SSL context for HTTPS
        ssl_context = ssl.create_default_context()
        
        for i, asset in enumerate(self.ASSETS):
            filepath = self.assets_dir / asset["filename"]
            
            # Report progress
            if progress_callback:
                progress_callback(i, len(self.ASSETS), asset["filename"])
            
            # Download if not present
            if not filepath.exists():
                self._download_file(asset["url"], filepath, ssl_context)
        
        # Final progress update
        if progress_callback:
            progress_callback(len(self.ASSETS), len(self.ASSETS), "Complete")
    
    def _download_file(self, url: str, filepath: Path, ssl_context):
        """Download a single file.
        
        Args:
            url: URL to download from
            filepath: Local path to save to
            ssl_context: SSL context for HTTPS
            
        Raises:
            RuntimeError: If download fails
        """
        try:
            with urllib.request.urlopen(url, context=ssl_context, timeout=30) as response:
                content = response.read()
                filepath.write_bytes(content)
        except Exception as e:
            raise RuntimeError(f"Failed to download {url}: {e}")
    
    def get_js_path(self) -> Path:
        """Get path to GrapeJS JavaScript file.
        
        Returns:
            Path to grapes.min.js
        """
        return self.assets_dir / "grapes.min.js"
    
    def get_css_path(self) -> Path:
        """Get path to GrapeJS CSS file.
        
        Returns:
            Path to grapes.min.css
        """
        return self.assets_dir / "grapes.min.css"
    
    def ensure_assets(self) -> bool:
        """Ensure assets exist, download if necessary.
        
        Returns:
            True if assets are ready, False if download failed
        """
        if not self.assets_exist():
            try:
                self.download_assets()
                return True
            except RuntimeError as e:
                print(f"Failed to download GrapeJS assets: {e}")
                return False
        return True
