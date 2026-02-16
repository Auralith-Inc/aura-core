#!/usr/bin/env python3
"""Aura Compile Script for OpenClaw Integration.

Compiles a directory of files into an .aura knowledge base.
Used as an OpenClaw skill action.

Usage:
    python compile.py <input_dir> <output_file>
"""

import sys
import subprocess


def main():
    if len(sys.argv) < 3:
        print("Usage: python compile.py <input_dir> <output.aura>")
        print("  Options:")
        print("    --pii-mask         Mask PII before compilation")
        print("    --min-quality 0.3  Filter low-quality content")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    # Pass through any additional flags
    extra_args = sys.argv[3:] if len(sys.argv) > 3 else []
    
    cmd = ["aura", "compile", input_dir, "--output", output_file] + extra_args
    
    print(f"🔥 Compiling: {input_dir} → {output_file}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed (exit code {e.returncode})")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ 'aura' command not found. Install with: pip install auralith-aura")
        sys.exit(1)


if __name__ == "__main__":
    main()
