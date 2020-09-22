import os

LOG_FILE = r'C:\ProgramData\NetSync\netsync.log'
LOG_PATH = os.path.dirname(LOG_FILE)

if __name__ == "__main__":
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
        print("path created")
