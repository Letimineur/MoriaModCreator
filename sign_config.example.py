"""Code signing configuration template for SSL.com eSigner.

Copy this file to sign_config.py and fill in your actual values.
The sign_config.py file is in .gitignore and will NOT be committed.

⚠️ NEVER commit sign_config.py to Git! ⚠️
"""

# SSL.com eSigner credentials
USERNAME = "your-email@example.com"
PASSWORD = "your_password_here"
CREDENTIAL_ID = "your-credential-id-here"
TOTP_SECRET = "your-totp-secret-here"

# App info for signature
APP_NAME = "Moria MOD Creator"
APP_URL = "https://github.com/jbowensii/MoriaModCreator"

# CodeSignTool directory path (not the .bat file, just the directory)
# Download from: https://www.ssl.com/how-to/esigner-codesigntool-command-guide/
CODESIGNTOOL_PATH = "C:/Users/YourName/AppData/Local/SSL.com/CodeSignTool"
