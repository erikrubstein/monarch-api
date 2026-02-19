"""
Secure Credential Manager for Monarch API

This script helps you securely store and manage your Monarch credentials
using your operating system's native credential storage:
- Windows: Credential Manager
- macOS: Keychain
- Linux: Secret Service (GNOME Keyring, KWallet, etc.)

Usage:
    python store_credentials.py         # Store new credentials
    python store_credentials.py --view  # View stored credentials (masked)
    python store_credentials.py --clear # Clear stored credentials
"""

import argparse
import getpass
import sys

try:
    import keyring
except ImportError:
    print("Error: 'keyring' package not found.")
    print("Please install it with: pip install keyring")
    sys.exit(1)


SERVICE_NAME = "Monarch-API"


def store_credentials():
    """Securely store Monarch credentials in the system keyring."""
    print("=" * 60)
    print("Monarch API - Secure Credential Storage")
    print("=" * 60)
    print("\nThis will securely store your credentials in your system's")
    print("native credential manager (Credential Manager/Keychain).\n")
    
    # Get email
    email = input("Email: ").strip()
    if not email:
        print("Error: Email cannot be empty")
        return False
    
    # Get password
    password = getpass.getpass("Password: ")
    if not password:
        print("Error: Password cannot be empty")
        return False
    
    # Get MFA secret (optional)
    print("\nMFA Secret Key (optional - press Enter to skip):")
    print("This is the text code shown when setting up 2FA in Monarch.")
    mfa_secret = getpass.getpass("MFA Secret: ")
    
    # Store credentials
    try:
        keyring.set_password(SERVICE_NAME, "email", email)
        keyring.set_password(SERVICE_NAME, email, password)
        
        if mfa_secret:
            keyring.set_password(SERVICE_NAME, f"{email}_mfa", mfa_secret)
            print("\n✅ Credentials stored successfully (including MFA secret)!")
        else:
            # Clear any existing MFA secret if user skipped it
            try:
                keyring.delete_password(SERVICE_NAME, f"{email}_mfa")
            except keyring.errors.PasswordDeleteError:
                pass
            print("\n✅ Credentials stored successfully (without MFA secret)!")
        
        print("\nYour credentials are now securely stored in your system's")
        print("credential manager and can be retrieved by the example scripts.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error storing credentials: {e}")
        return False


def view_credentials():
    """View stored credentials (with password masked)."""
    print("=" * 60)
    print("Monarch API - View Stored Credentials")
    print("=" * 60)
    
    try:
        # Get stored email
        email = keyring.get_password(SERVICE_NAME, "email")
        
        if not email:
            print("\n⚠️  No credentials found.")
            print("Run without --view flag to store credentials.")
            return
        
        # Check if password exists
        password = keyring.get_password(SERVICE_NAME, email)
        password_status = "✓ Stored" if password else "✗ Not found"
        
        # Check if MFA secret exists
        mfa_secret = keyring.get_password(SERVICE_NAME, f"{email}_mfa")
        mfa_status = "✓ Stored" if mfa_secret else "✗ Not stored"
        
        print(f"\nEmail:      {email}")
        print(f"Password:   {password_status}")
        print(f"MFA Secret: {mfa_status}")
        
        print("\n💡 Passwords are securely stored and not displayed.")
        
    except Exception as e:
        print(f"\n❌ Error retrieving credentials: {e}")


def clear_credentials():
    """Clear all stored credentials."""
    print("=" * 60)
    print("Monarch API - Clear Stored Credentials")
    print("=" * 60)
    
    try:
        email = keyring.get_password(SERVICE_NAME, "email")
        
        if not email:
            print("\n⚠️  No credentials found to clear.")
            return
        
        print(f"\nFound credentials for: {email}")
        confirm = input("Are you sure you want to delete these credentials? (yes/no): ")
        
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
        
        # Delete credentials
        try:
            keyring.delete_password(SERVICE_NAME, "email")
        except keyring.errors.PasswordDeleteError:
            pass
            
        try:
            keyring.delete_password(SERVICE_NAME, email)
        except keyring.errors.PasswordDeleteError:
            pass
            
        try:
            keyring.delete_password(SERVICE_NAME, f"{email}_mfa")
        except keyring.errors.PasswordDeleteError:
            pass
        
        print("\n✅ Credentials cleared successfully!")
        
    except Exception as e:
        print(f"\n❌ Error clearing credentials: {e}")


def get_credentials():
    """
    Retrieve stored credentials from the system keyring.
    
    Returns:
        tuple: (email, password, mfa_secret) or (None, None, None) if not found
    """
    try:
        email = keyring.get_password(SERVICE_NAME, "email")
        if not email:
            return None, None, None
        
        password = keyring.get_password(SERVICE_NAME, email)
        mfa_secret = keyring.get_password(SERVICE_NAME, f"{email}_mfa")
        
        return email, password, mfa_secret
    except Exception:
        return None, None, None


def main():
    parser = argparse.ArgumentParser(
        description="Securely manage Monarch API credentials using system keyring"
    )
    parser.add_argument(
        "--view",
        action="store_true",
        help="View stored credentials (passwords will be masked)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all stored credentials"
    )
    
    args = parser.parse_args()
    
    if args.view:
        view_credentials()
    elif args.clear:
        clear_credentials()
    else:
        store_credentials()


if __name__ == "__main__":
    main()
