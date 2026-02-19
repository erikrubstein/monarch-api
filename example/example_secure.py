"""
Monarch API - Secure Example Usage

This script demonstrates how to use the Monarch Python library
with credentials securely stored in your system's keyring.

Before running this script:
1. Install dependencies: 
   pip install monarch keyring
2. Store your credentials:
   python store_credentials.py
3. Run this script:
   python example_secure.py
"""

import asyncio
import sys
from datetime import datetime, timedelta

try:
    import keyring
except ImportError:
    print("Error: 'keyring' package not found.")
    print("Please install it with: pip install keyring")
    sys.exit(1)

try:
    from monarch import Monarch, RequireMFAException
except ImportError:
    print("Error: 'monarch' package not found.")
    print("Please install it with: pip install monarch")
    print("Or run from the parent directory: pip install -e .")
    sys.exit(1)


SERVICE_NAME = "Monarch-API"


def get_credentials():
    """Retrieve credentials from system keyring."""
    try:
        email = keyring.get_password(SERVICE_NAME, "email")
        if not email:
            return None, None, None
        
        password = keyring.get_password(SERVICE_NAME, email)
        mfa_secret = keyring.get_password(SERVICE_NAME, f"{email}_mfa")
        
        return email, password, mfa_secret
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        return None, None, None


async def main():
    """Main function demonstrating Monarch API with secure credentials."""
    
    print("=" * 60)
    print("Monarch API - Secure Example Demo")
    print("=" * 60)
    
    # Retrieve credentials from secure storage
    email, password, mfa_secret = get_credentials()
    
    if not email or not password:
        print("\n❌ No credentials found in system keyring!")
        print("\nPlease store your credentials first:")
        print("  python store_credentials.py")
        print("\nThen run this script again.")
        sys.exit(1)
    
    print(f"\n✅ Retrieved credentials from secure storage for: {email}")
    if mfa_secret:
        print("✅ MFA secret found - will use for automatic authentication")
    
    # Initialize the Monarch client
    mm = Monarch()
    
    # ========================================
    # AUTHENTICATION
    # ========================================
    
    print("\n🔐 Logging in...\n")
    try:
        await mm.login(
            email=email,
            password=password,
            save_session=True,
            use_saved_session=True,
            mfa_secret_key=mfa_secret if mfa_secret else None
        )
        print("✅ Login successful!\n")
    except RequireMFAException:
        # If MFA secret wasn't stored, prompt for code
        mfa_code = input("Enter your MFA code: ")
        await mm.multi_factor_authenticate(email, password, mfa_code)
        print("✅ MFA authentication successful!\n")
    
    # ========================================
    # EXAMPLE: Get Account Summary
    # ========================================
    
    print("-" * 60)
    print("Account Summary")
    print("-" * 60)
    
    accounts = await mm.get_accounts()
    total_balance = 0
    
    print(f"\n📊 You have {len(accounts.get('accounts', []))} accounts:\n")
    
    for account in accounts.get('accounts', []):
        name = account.get('displayName', 'Unknown')
        balance = account.get('currentBalance', 0)
        account_type = account.get('type', {}).get('display', 'Unknown')
        
        print(f"  • {name}")
        print(f"    Type: {account_type}")
        print(f"    Balance: ${balance:,.2f}")
        
        if account.get('includeInNetWorth'):
            total_balance += balance
        
        print()
    
    print(f"💰 Total Net Worth: ${total_balance:,.2f}\n")
    
    # ========================================
    # EXAMPLE: Recent Transactions
    # ========================================
    
    print("-" * 60)
    print("Recent Transactions")
    print("-" * 60)
    
    transactions = await mm.get_transactions(limit=5)
    print(f"\n💳 Last 5 transactions:\n")
    
    for txn in transactions.get('allTransactions', {}).get('results', []):
        date = txn.get('date', 'Unknown')
        merchant = txn.get('merchant', {}).get('name', 'Unknown')
        amount = txn.get('amount', 0)
        category = txn.get('category', {}).get('name', 'Uncategorized')
        
        sign = "+" if amount > 0 else "-"
        print(f"  {date} | {sign}${abs(amount):,.2f} | {merchant}")
        print(f"    Category: {category}")
        print()
    
    # ========================================
    # EXAMPLE: Cashflow Summary
    # ========================================
    
    print("-" * 60)
    print("Cashflow Summary (Last 30 Days)")
    print("-" * 60)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    cashflow = await mm.get_cashflow_summary(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if cashflow and isinstance(cashflow, dict) and 'summary' in cashflow:
        print(f"\n💰 Financial Overview:\n")
        
        summary_list = cashflow.get('summary', [])
        if summary_list and len(summary_list) > 0:
            summary_data = summary_list[0].get('summary', {})
            income = summary_data.get('sumIncome', 0)
            expenses = summary_data.get('sumExpense', 0)
            savings = summary_data.get('savings', income + expenses)
            
            print(f"  Income:       ${abs(income):,.2f}")
            print(f"  Expenses:     ${abs(expenses):,.2f}")
            print(f"  Net Savings:  ${savings:,.2f}")
            
            if income > 0:
                savings_rate = (savings / abs(income)) * 100
                print(f"  Savings Rate: {savings_rate:.1f}%")
            print()
    
    print("=" * 60)
    print("✨ Demo completed successfully!")
    print("=" * 60)
    print("\n🔒 Your credentials remain securely stored in your system keyring.")
    print("💡 Session has been saved for faster future logins!")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
