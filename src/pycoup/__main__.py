import os.path
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from src.pycoup.console import main

if __name__ == "__main__":
    main()
