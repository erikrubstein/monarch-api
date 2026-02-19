# Monarch API - Examples

This directory contains example scripts demonstrating how to use the Monarch API.

## Running the Examples

### Prerequisites

1. Install the monarch library:
   ```bash
   pip install monarch
   ```

2. Install example dependencies (for secure credential storage):
   ```bash
   cd example
   pip install -r requirements.txt
   ```

3. Set up your credentials (choose one method):

   **Option A: Secure System Keyring (RECOMMENDED) 🔒**
   
   Store credentials securely in your OS's native credential manager:
   ```bash
   cd example
   python store_credentials.py
   ```
   
   Then run the secure example:
   ```bash
   python example_secure.py
   ```
   
   This method uses:
   - **Windows**: Credential Manager
   - **macOS**: Keychain
   - **Linux**: Secret Service (GNOME Keyring, KWallet)
   
   Your credentials are encrypted by your OS and never stored in plaintext!

   **Option B: Environment Variables**
   ```bash
   # Windows PowerShell
   $env:MONARCH_EMAIL = "your-email@example.com"
   $env:MONARCH_PASSWORD = "your-password"
   $env:MONARCH_MFA_SECRET = "your-mfa-secret"  # Optional
   
   # Linux/Mac
   export MONARCH_EMAIL="your-email@example.com"
   export MONARCH_PASSWORD="your-password"
   export MONARCH_MFA_SECRET="your-mfa-secret"  # Optional
   ```

   **Option C: Interactive Login**
   
   Simply run the script without setting environment variables, and you'll be prompted for credentials.

   **Option D: Hardcode Credentials**
   
   Edit the example script and set the `email`, `password`, and `mfa_secret` variables directly (not recommended).

### Running the Example

```bash
cd example

# Secure method (recommended):
python store_credentials.py      # First time: store credentials
python example_secure.py         # Run secure example

# Or standard method:
python example.py
```

## Available Scripts

### `example_secure.py` (Recommended)
Demonstrates API usage with credentials securely stored in your system keyring. No plaintext passwords!

### `store_credentials.py`
Utility to manage credentials in your system keyring:
```bash
python store_credentials.py         # Store new credentials
python store_credentials.py --view  # View what's stored (masked)
python store_credentials.py --clear # Remove stored credentials
```

### `example.py`
Standard example using environment variables or interactive login.

## What the Examples Demonstrate

The `example.py` script showcases:

1. **Authentication** - Login with MFA support
2. **Get Accounts** - Retrieve all linked accounts with balances
3. **Get Transactions** - Fetch recent transactions
4. **Get Categories** - List transaction categories
5. **Get Budgets** - View budget data and spending
6. **Get Cashflow** - Calculate income, expenses, and savings
7. **Get Holdings** - View investment account holdings
8. **Get Subscription** - Check account subscription status

## More Examples

For a complete list of available API methods, see the main [README.md](../README.md) in the repository root.

## Security Notes

- **✅ RECOMMENDED**: Use `example_secure.py` with system keyring for secure credential storage
- Credentials stored in keyring are encrypted by your operating system
- Sessions are saved automatically for faster subsequent logins (stored in `.mm/` directory)
- MFA Secret Key is optional but eliminates the need to manually enter codes
- All example files in this directory can be safely deleted without affecting the core API

## Troubleshooting

**Q: "keyring" module not found**
```bash
pip install keyring
```

**Q: Permission denied on Linux**

You may need to install a keyring backend:
```bash
# Ubuntu/Debian
sudo apt-get install gnome-keyring

# Fedora
sudo dnf install gnome-keyring
```

**Q: How do I see my stored credentials?**
```bash
python store_credentials.py --view
```
Note: Passwords are never displayed, only their presence is confirmed.
