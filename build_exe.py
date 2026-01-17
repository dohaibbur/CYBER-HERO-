"""
Build script for CyberHero executable
Run: python build_exe.py
"""

import subprocess
import sys
import os

def install_package(package):
    print(f"[*] Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_icon():
    """Ensures assets/icon.ico exists, converting from png if needed"""
    ico_path = "assets/icon.ico"
    png_path = "assets/icon.png"

    if os.path.exists(ico_path):
        return True
    
    if not os.path.exists(png_path):
        return False

    print("[*] Found icon.png, converting to icon.ico...")
    try:
        from PIL import Image
    except ImportError:
        install_package("Pillow")
        from PIL import Image

    try:
        img = Image.open(png_path)
        # Save as ICO with multiple sizes for best Windows compatibility
        img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("[OK] Icon converted successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to convert icon: {e}")
        return False

def main():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("[OK] PyInstaller found")
    except ImportError:
        install_package("pyinstaller")

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "CyberHero",
        "--add-data", "assets;assets",
        "--add-data", "profiles;profiles",
        "--paths", "src",
        "--collect-all", "scapy",
        "--hidden-import", "cv2",
        "--clean",
        "main.py"
    ]

    # Add icon if it exists
    if ensure_icon():
        cmd.insert(3, "--icon=assets/icon.ico")
    else:
        print("[WARNING] assets/icon.ico not found. Building with default icon.")

    print("\n[*] Building CyberHero.exe...")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "="*50)
        print("[OK] Build successful!")
        print("Your executable is at: dist/CyberHero.exe")
        print("="*50)
    else:
        print("\n[X] Build failed. Check errors above.")

if __name__ == "__main__":
    main()
