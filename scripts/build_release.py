"""Complete build and release script for Moria MOD Creator.

This script:
1. Builds the executable with PyInstaller
2. Signs the executable
3. Creates installer zip bundles
4. Builds the Inno Setup installer (if available)
5. Signs the installer

Usage:
    python scripts/build_release.py [--no-sign] [--no-installer]
"""

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path
import os
import shutil


def run_command(cmd, description, timeout=120):
    """Run a command and print status.

    Args:
        cmd: Command to run (list or string).
        description: Description of what the command does.
        timeout: Timeout in seconds.

    Returns:
        True if successful, False otherwise.
    """
    print(f"\n{'='*60}")
    print(f"{description}...")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=isinstance(cmd, str),
            check=False
        )
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True

        print(f"[ERROR] {description} failed!")
        print(result.stderr)
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {description} timed out!")
        return False
    except (OSError, ValueError) as e:
        print(f"[ERROR] {description} failed: {e}")
        return False


def build_executable(project_root):
    """Build the executable with PyInstaller."""
    spec_file = project_root / "MoriaMODCreator.spec"
    return run_command(
        ["pyinstaller", str(spec_file), "--noconfirm"],
        "Building executable with PyInstaller",
        timeout=180
    )


def sign_file(file_path):
    """Sign a file using the signing script."""
    # Import signing function from sign_executable module
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from scripts.sign_executable import sign_file as sign_func  # pylint: disable=import-outside-toplevel
        return sign_func(file_path)
    except ImportError:
        print("Warning: Could not import signing module")
        return False


def copy_to_release(project_root):
    """Copy executable from dist/ to release/."""
    dist_exe = project_root / "dist" / "MoriaMODCreator.exe"
    release_dir = project_root / "release"
    release_exe = release_dir / "MoriaMODCreator.exe"

    release_dir.mkdir(exist_ok=True)

    if not dist_exe.exists():
        print(f"[ERROR] Executable not found: {dist_exe}")
        return False

    shutil.copy2(dist_exe, release_exe)
    print("[OK] Copied executable to release/")
    return True


def create_installer_zips(project_root):
    """Create zip bundles for the installer."""
    appdata = Path(os.environ['APPDATA']) / 'MoriaMODCreator'
    installer_dir = project_root / 'installer'

    print("\nCreating installer zip bundles...")

    # Definitions.zip
    print("  - Definitions.zip...")
    with zipfile.ZipFile(installer_dir / 'Definitions.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        defs_dir = appdata / 'Definitions'
        if defs_dir.exists():
            for root, _, files in os.walk(defs_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(defs_dir)
                    zf.write(file_path, arcname)
            print(f"    Added {len(zf.namelist())} files")

    # mymodfiles.zip (excluding large directories)
    print("  - mymodfiles.zip...")
    with zipfile.ZipFile(installer_dir / 'mymodfiles.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        mods_dir = appdata / 'mymodfiles'
        if mods_dir.exists():
            for root, _, files in os.walk(mods_dir):
                root_path = Path(root)
                # Skip large directories
                if any(part in ['finalmod', 'jsonfiles'] for part in root_path.parts):
                    continue
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(mods_dir)
                    zf.write(file_path, arcname)
            size = sum(zf.getinfo(f).file_size for f in zf.namelist()) / 1024 / 1024
            print(f"    Added {len(zf.namelist())} files ({size:.2f} MB)")

    # utilities.zip
    print("  - utilities.zip...")
    with zipfile.ZipFile(installer_dir / 'utilities.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        utils_dir = appdata / 'utilities'
        if utils_dir.exists():
            for root, _, files in os.walk(utils_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(utils_dir)
                    zf.write(file_path, arcname)
            print(f"    Added {len(zf.namelist())} files")

    print("[OK] Installer zips created")
    return True


def build_installer(project_root):
    """Build the Inno Setup installer."""
    iss_file = project_root / "installer" / "MoriaMODCreator.iss"

    # Try to find Inno Setup compiler
    iscc_paths = [
        "C:/Program Files (x86)/Inno Setup 6/ISCC.exe",
        "C:/Program Files/Inno Setup 6/ISCC.exe",
    ]

    iscc = None
    for path in iscc_paths:
        if Path(path).exists():
            iscc = path
            break

    if not iscc:
        # Try to find in PATH
        result = subprocess.run(
            ["where", "iscc"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            iscc = result.stdout.strip().split('\n')[0]

    if not iscc:
        print("Warning: Inno Setup compiler not found. Skipping installer build.")
        print("Install Inno Setup from https://jrsoftware.org/isdl.php")
        return False

    return run_command(
        [iscc, str(iss_file)],
        "Building Inno Setup installer",
        timeout=120
    )


def main():
    """Main build process: build executable, sign, create installer zips, build & sign installer."""
    parser = argparse.ArgumentParser(description="Build release for Moria MOD Creator")
    parser.add_argument("--no-sign", action="store_true", help="Skip code signing")
    parser.add_argument("--no-installer", action="store_true", help="Skip installer build")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    print("="*60)
    print("Moria MOD Creator - Release Build Script")
    print("="*60)

    # Step 1: Build executable
    if not build_executable(project_root):
        print("\n[ERROR] Build failed!")
        return 1

    # Step 2: Copy to release/
    if not copy_to_release(project_root):
        print("\n[ERROR] Copy to release failed!")
        return 1

    # Step 3: Sign executable
    if not args.no_sign:
        release_exe = project_root / "release" / "MoriaMODCreator.exe"
        if not sign_file(release_exe):
            print("\nWarning: Executable signing failed. Continuing without signature.")

    # Step 4: Create installer zips
    if not create_installer_zips(project_root):
        print("\n[ERROR] Zip creation failed!")
        return 1

    # Step 5: Build installer
    if not args.no_installer:
        if build_installer(project_root):
            # Step 6: Sign installer
            if not args.no_sign:
                installer = project_root / "release" / "MoriaMODCreator_Setup_v0.8.exe"
                if installer.exists():
                    if not sign_file(installer):
                        print("\nWarning: Installer signing failed.")
        else:
            print("\nWarning: Installer build skipped or failed.")

    print("\n" + "="*60)
    print("[OK] Build process complete!")
    print("="*60)
    print("\nRelease files:")
    print("  - release/MoriaMODCreator.exe")
    if (project_root / "release").glob("*.exe"):
        for f in (project_root / "release").glob("*.exe"):
            if f.name.startswith("MoriaMODCreator_Setup"):
                print(f"  - release/{f.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
