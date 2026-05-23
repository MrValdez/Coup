from src.pycoup.console import console
from src.pycoup.server import main as server


if __name__ == "__main__":
    choice = input("""1. Console
2. Server (Default)

>>> """)

    if choice == "1":
        console.main()
    else:
        server.start()
