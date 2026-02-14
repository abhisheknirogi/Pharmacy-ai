import os
import shutil

def add_to_startup():
    startup = os.path.join(os.getenv("APPDATA"),
        "Microsoft\\Windows\\Start Menu\\Programs\\Startup")

    exe_path = os.path.abspath("PharmarecAI.exe")
    shutil.copy(exe_path, startup)
    print("Added to startup")

if __name__ == "__main__":
    add_to_startup()
