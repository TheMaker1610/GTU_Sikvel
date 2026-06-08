import subprocess
import sys
import os

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd=root,
    )
