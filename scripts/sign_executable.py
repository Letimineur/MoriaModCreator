"""Code signing script for Moria MOD Creator executable.

This script signs the executable using SSL.com eSigner cloud service.
Credentials are stored in sign_config.py (not committed to git).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def sign_file(file_path: Path) -> bool:
    """Sign a file using SSL.com eSigner.

    Args:
        file_path: Path to the file to sign.

    Returns:
        True if signing succeeded, False otherwise.
    """
    # Import local signing configuration from project root
    proj_root = Path(__file__).parent.parent
    sys.path.insert(0, str(proj_root))

    try:
        import sign_config
    except ImportError:
        print("ERROR: sign_config.py not found!")
        print("Your signing credentials should be in sign_config.py")
        print("This file is in .gitignore and will not be committed.")
        return False

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False

    # Check if CodeSignTool directory exists
    codesigntool_dir = Path(sign_config.CODESIGNTOOL_PATH)
    java_exe = codesigntool_dir / "jdk-11.0.2" / "bin" / "java.exe"
    jar_file = codesigntool_dir / "jar" / "code_sign_tool-1.3.2.jar"

    if not codesigntool_dir.exists():
        print(f"ERROR: CodeSignTool directory not found: {codesigntool_dir}")
        print("Download from: https://www.ssl.com/how-to/esigner-codesigntool-command-guide/")
        print("Or update CODESIGNTOOL_PATH in sign_config.py")
        return False

    if not java_exe.exists():
        print(f"ERROR: Java not found: {java_exe}")
        return False

    if not jar_file.exists():
        print(f"ERROR: CodeSignTool jar not found: {jar_file}")
        return False

    # Use a temp directory for signed output to avoid source==destination error
    tmp_dir = tempfile.mkdtemp(prefix="codesign_")

    try:
        # Build Java command to run CodeSignTool for SSL.com eSigner
        cmd = [
            str(java_exe),
            "-jar",
            str(jar_file),
            "sign",
            "-username=" + sign_config.USERNAME,
            "-password=" + sign_config.PASSWORD,
            "-credential_id=" + sign_config.CREDENTIAL_ID,
            "-totp_secret=" + sign_config.TOTP_SECRET,
            "-input_file_path=" + str(file_path.absolute()),
            "-output_dir_path=" + tmp_dir
        ]

        print(f"Signing {file_path.name} with SSL.com eSigner...")
        print("This may take a moment as it connects to the cloud signing service...")

        # Run from CodeSignTool directory so it can find conf/code_sign_tool.properties
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=120,
            check=False,
            cwd=str(codesigntool_dir)
        )

        # Check stderr for errors - CodeSignTool may return 0 even on failure
        has_error = (result.stderr and
                     ("Exception" in result.stderr or
                      "FileNotFoundException" in result.stderr))

        if result.returncode == 0 and not has_error:
            # Copy the signed file back over the original
            signed_file = Path(tmp_dir) / file_path.name
            if signed_file.exists():
                shutil.copy2(signed_file, file_path)
                print(f"[OK] Successfully signed: {file_path.name}")
                if result.stdout:
                    print(result.stdout)
                return True

            print(f"ERROR: Signed file not found in temp dir: {signed_file}")
            return False

        print("ERROR: Signing failed!")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: Signing timed out (>120 seconds)")
        return False
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}")
        return False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Get project root
    project_root = Path(__file__).parent.parent

    # Sign the executable in release/
    exe_path = project_root / "release" / "MoriaMODCreator.exe"

    if sign_file(exe_path):
        print("\n[OK] Code signing complete!")
        sys.exit(0)
    else:
        print("\n[ERROR] Code signing failed!")
        sys.exit(1)
