"""Build script to download GrapeJS assets for development and releases."""

import urllib.request
import urllib.error
import ssl
import hashlib
import argparse
import sys
import time
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
        """Initialize downloader with addon path.
        
        Args:
            addon_path: Root path of the addon (defaults to parent of scripts dir)
        """
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
    ) -> list:
        """Download all required assets.
        
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
        """Verify all assets exist and are valid.
        
        Args:
            include_plugins: Whether to check optional plugins
            
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
        """Download a single file with retry logic.
        
        Args:
            url: URL to download from
            filepath: Local path to save to
            ssl_context: SSL context for HTTPS
            timeout: Timeout in seconds
            
        Raises:
            urllib.error.URLError: If download fails after retries
        """
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
                time.sleep(1 * (attempt + 1))
    
    def _verify_hash(self, filepath: Path, expected_hash: str) -> bool:
        """Verify file SHA256 hash.
        
        Args:
            filepath: Path to file to verify
            expected_hash: Expected SHA256 hash
            
        Returns:
            True if hash matches
        """
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_hash
    
    def get_asset_info(self) -> dict:
        """Get information about downloaded assets.
        
        Returns:
            Dictionary with version, assets list, missing list, total size
        """
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
