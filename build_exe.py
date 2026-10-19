import os
import sys
import subprocess
import shutil

def build_executable():
    print("=" * 60)
    print(">>> BUILDING STANDALONE EXECUTABLE: FileOrganizer.exe")
    print(">>> AESTHETIC: Industrial Brutalist & Tactical Streetwear")
    print("=" * 60)

    # Ensure icon exists
    if not os.path.exists("assets/icon.ico"):
        print("[!] Generating missing icon...")
        import build_assets
        build_assets.create_tactical_icon()

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=FileOrganizer",
        "--icon=assets/icon.ico",
        "--add-data=assets;assets",
        "--collect-all=customtkinter",
        "--clean",
        "-y",
        "main.py"
    ]

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    print("-" * 60)

    res = subprocess.run(cmd)

    if res.returncode == 0:
        exe_path = os.path.abspath("dist/FileOrganizer.exe")
        print("\n" + "=" * 60)
        print("[OK] BUILD SUCCESSFUL!")
        print(f"[OK] Standalone Executable: {exe_path}")
        print(f"[OK] Size: {os.path.getsize(exe_path) / (1024 * 1024):.2f} MB")
        print("=" * 60)
    else:
        print("\n" + "!" * 60)
        print(f"[!] Build failed with exit code: {res.returncode}")
        print("!" * 60)
        sys.exit(res.returncode)

if __name__ == "__main__":
    build_executable()
