"""Build script for creating PyPI releases with the Memory OS module.

This script handles the build process for auralith-aura:
1. Copies the real Memory OS source from .private/
2. Builds the wheel and sdist
3. Cleans up the source after build

Usage:
    python build_release.py        # Build wheel + sdist
    python build_release.py upload  # Build and upload to PyPI
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PRIVATE_SRC = ROOT / ".private" / "memory.py"
TARGET = ROOT / "aura" / "_memory.py"
DIST = ROOT / "dist"


def build():
    """Build wheel and sdist with the real Memory OS included."""

    if not PRIVATE_SRC.exists():
        print("[!] Private source not found: {}".format(PRIVATE_SRC))
        print("   Place the real memory.py in .private/memory.py")
        sys.exit(1)

    # Copy real source into package as _memory.py
    print("[*] Copying Memory OS source...")
    shutil.copy2(PRIVATE_SRC, TARGET)

    try:
        # Clean previous builds
        if DIST.exists():
            shutil.rmtree(DIST)
        for d in ROOT.glob("*.egg-info"):
            shutil.rmtree(d)

        # Build
        print("[*] Building wheel and sdist...")
        subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=str(ROOT),
            check=True,
        )
        print("[OK] Build complete. Artifacts in dist/")

    finally:
        # Always clean up — never leave real source exposed
        if TARGET.exists():
            TARGET.unlink()
            print("[*] Cleaned up _memory.py")


def upload():
    """Upload to PyPI using twine."""
    build()
    print("[*] Uploading to PyPI...")
    subprocess.run(
        [sys.executable, "-m", "twine", "upload", "dist/*"],
        cwd=str(ROOT),
        check=True,
    )
    print("[OK] Uploaded to PyPI")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "upload":
        upload()
    else:
        build()
