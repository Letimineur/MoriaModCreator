# Code Signing Setup Guide

This guide explains how to set up automatic code signing for Moria MOD Creator builds without exposing your credentials to the internet.

## Prerequisites

1. **Code Signing Certificate**: You need a valid code signing certificate (`.pfx` or `.p12` file)
2. **Windows SDK**: Install Windows SDK for the `signtool.exe` utility
3. **Inno Setup** (optional): For building the installer

## Setup Steps

### 1. Create Your Signing Configuration

Copy the example configuration file:

```bash
cp sign_config.example.py sign_config.py
```

Edit `sign_config.py` with your actual values:

```python
# Path to your certificate file
CERT_PATH = "C:/Users/YourName/Certificates/mycert.pfx"

# Certificate password
CERT_PASSWORD = "your_password_here"

# SignTool path (adjust version number as needed)
SIGNTOOL_PATH = "C:/Program Files (x86)/Windows Kits/10/bin/10.0.22621.0/x64/signtool.exe"

# Timestamp server
TIMESTAMP_URL = "http://timestamp.digicert.com"

# App info
APP_NAME = "Moria MOD Creator"
APP_URL = "https://github.com/jbowensii/MoriaModCreator"
```

**Important**: `sign_config.py` is in `.gitignore` and will NEVER be committed to Git.

### 2. Find Your SignTool Path

Run this command to find where Windows SDK installed SignTool:

```bash
dir /s /b "C:\Program Files (x86)\Windows Kits\*\signtool.exe"
```

Copy the path to the x64 version (not x86 or arm64) and update `SIGNTOOL_PATH` in `sign_config.py`.

### 3. Verify Certificate

Test that your certificate works:

```bash
signtool sign /f "path\to\cert.pfx" /p "password" /fd sha256 /tr http://timestamp.digicert.com /td sha256 "path\to\test.exe"
```

### 4. Configure Inno Setup Signing (Optional)

If you want the installer to be signed automatically:

1. Open Inno Setup
2. Go to **Tools** → **Configure Sign Tools**
3. Add a new sign tool named `ssl`
4. Use this command (adjust paths):

```
"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign /f "C:\path\to\cert.pfx" /p "YOUR_PASSWORD" /tr http://timestamp.digicert.com /td sha256 /fd sha256 /d $p /du $w $f
```

5. In `installer/MoriaMODCreator.iss`, uncomment the `SignTool` line:

```ini
SignTool=ssl /d $q{#MyAppName}$q /du $q{#MyAppURL}$q $f
```

## Usage

### Manual Signing

Sign the executable after building:

```bash
python scripts/sign_executable.py
```

### Automated Build with Signing

Build, sign, and create installer in one command:

```bash
python scripts/build_release.py
```

Options:
- `--no-sign`: Skip code signing
- `--no-installer`: Skip installer build

### Build Without Signing

```bash
python scripts/build_release.py --no-sign
```

## Security Best Practices

### ✅ DO

- Store `sign_config.py` locally only (already in `.gitignore`)
- Store certificates in a secure location with restricted permissions
- Use a strong password for your certificate
- Keep certificate files out of cloud-synced directories
- Consider using environment variables for the password:

```python
import os
CERT_PASSWORD = os.environ.get('CODE_SIGNING_PASSWORD', '')
```

Then set the environment variable before building:

```bash
set CODE_SIGNING_PASSWORD=your_password
python scripts/build_release.py
```

### ❌ DON'T

- Never commit `sign_config.py` to Git
- Never commit `.pfx` or `.p12` certificate files
- Never hardcode passwords in scripts that get committed
- Never share your certificate password
- Never store certificates in public locations

## Troubleshooting

### "Certificate not found"

- Check that `CERT_PATH` in `sign_config.py` points to your actual certificate file
- Use absolute paths (e.g., `C:/Users/...`)

### "SignTool not found"

- Install Windows SDK: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
- Update `SIGNTOOL_PATH` to point to your installed version

### "Access denied" or "Invalid password"

- Verify your certificate password is correct
- Ensure you have read permissions on the certificate file

### "Timestamp server unavailable"

- Try a different timestamp server:
  - DigiCert: `http://timestamp.digicert.com`
  - Sectigo: `http://timestamp.sectigo.com`
  - GlobalSign: `http://timestamp.globalsign.com`

## Timestamp Servers

Using a timestamp server ensures your signature remains valid even after your certificate expires. Common servers:

- **DigiCert**: `http://timestamp.digicert.com` (recommended)
- **Sectigo**: `http://timestamp.sectigo.com`
- **GlobalSign**: `http://timestamp.globalsign.com`

## Verifying Signatures

After signing, verify the signature:

```bash
signtool verify /pa /v "release\MoriaMODCreator.exe"
```

You should see "Successfully verified" if signing worked.

---

**Note**: All signing credentials are stored locally and never committed to version control. Keep your certificate and password secure!
