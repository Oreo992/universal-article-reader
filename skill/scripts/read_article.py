#!/usr/bin/env python3
"""
Wrapper script for the universal article reader.

Usage:
    python read_article.py <URL> [--no-browser] [--force-browser] [--no-images]
"""

import sys
import os

# Ensure the project src is on sys.path
PROJECT_ROOT = r"C:\Users\Administrator\Desktop\wechat-article-reader-main"
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from mcp_server_my_mcp_server.cli import main_universal

if __name__ == "__main__":
    main_universal()
