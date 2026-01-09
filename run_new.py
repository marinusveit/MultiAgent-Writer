#!/usr/bin/env python3
"""
Test launcher for the new structure
"""

import sys
from pathlib import Path

# Add src/ to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the application
from multiagent_writer.main import main

if __name__ == "__main__":
    main()
