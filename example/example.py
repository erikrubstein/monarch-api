"""
Monarch API - Example Usage

This script demonstrates how to use the Monarch Python library
to interact with Monarch's API.

Before running this script:
1. Install dependencies: pip install monarch
2. Set your credentials below or use environment variables
"""

import asyncio
import os
from datetime import datetime, timedelta
from monarch import Monarch, RequireMFAException


async def main():
    """Main function demonstrating various Monarch API features."""
    
    # Initialize the Monarch client
    mm = Monarch()
    
    print("=" * 60)
    print("Monarch API - Example Demo")
    print("=" * 60)
    
    # ========================================
    # AUTHENTICATION
    # ========================================
    
    # Option 1: Use environment variables (recommended)
    email = os.getenv('MONARCH_EMAIL')
    password = os.getenv('MONARCH_PASSWORD')
    mfa_secret = os.getenv('MONARCH_MFA_SECRET')  # Optional
    
    # Option 2: Hardcode credentials (not recommended for production)
    # email = "your-email@example.com"
    # password = "your-password"
    # mfa_secret = "your-mfa-secret"  # Optional
    
    # Option 3: Interactive login
    if not email or not password:
        print("\n🔐 Using interactive login...\n")
        await mm.interactive_login()
    else:
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
            mfa_code = input("Enter your MFA code: ")
            await mm.multi_factor_authenticate(email, password, mfa_code)
            print("✅ MFA authentication successful!\n")
    
    # ========================================
    # EXAMPLE 1: Get Accounts
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 1: Get All Accounts")
    print("-" * 60)
    
    accounts = await mm.get_accounts()
    print(f"\n📊 Found {len(accounts.get('accounts', []))} accounts:\n")
    
    for account in accounts.get('accounts', [])[:5]:
        name = account.get('displayName', 'Unknown')
        balance = account.get('currentBalance', 0)
        account_type = account.get('type', {}).get('display', 'Unknown')
        account_id = account.get('id')
        
        print(f"  • {name}")
        print(f"    ID: {account_id}")
        print(f"    Type: {account_type}")
        print(f"    Balance: ${balance:,.2f}")
        print()
    
    # ========================================
    # EXAMPLE 2: Get Recent Transactions
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 2: Get Recent Transactions")
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
    # EXAMPLE 3: Get Transaction Categories
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 3: Get Transaction Categories")
    print("-" * 60)
    
    categories = await mm.get_transaction_categories()
    print(f"\n🏷️  Transaction categories (showing first 10):\n")
    
    for category in categories.get('categories', [])[:10]:
        name = category.get('name', 'Unknown')
        group = category.get('group', {}).get('name', 'No Group')
        category_id = category.get('id')
        print(f"  • {name} ({group}) - ID: {category_id}")
    
    print()
    
    # ========================================
    # EXAMPLE 4: Get Budgets
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 4: Get Budget Information")
    print("-" * 60)
    
    budgets_data = await mm.get_budgets()
    
    if budgets_data and 'monthlyAmounts' in budgets_data:
        print(f"\n📅 Budget overview (current month):\n")
        
        for month_data in budgets_data.get('monthlyAmounts', [])[:1]:
            month = month_data.get('month', 'Unknown')
            print(f"Month: {month}\n")
            
            categories = month_data.get('categoryGroups', [])
            for cat_group in categories[:5]:
                group_name = cat_group.get('groupName', 'Unknown')
                budgeted = cat_group.get('budgeted', 0)
                actual = cat_group.get('actual', 0)
                
                print(f"  {group_name}")
                print(f"    Budgeted: ${budgeted:,.2f}")
                print(f"    Actual:   ${actual:,.2f}")
                
                if budgeted > 0:
                    percent = (actual / budgeted) * 100
                    print(f"    Usage:    {percent:.1f}%")
                print()
    
    # ========================================
    # EXAMPLE 5: Get Cashflow Summary
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 5: Get Cashflow Summary")
    print("-" * 60)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    cashflow = await mm.get_cashflow_summary(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if cashflow and isinstance(cashflow, dict) and 'summary' in cashflow:
        print(f"\n💰 Last 30 days cashflow:\n")
        
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
    
    # ========================================
    # EXAMPLE 6: Get Account Holdings (for investment accounts)
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 6: Get Account Holdings")
    print("-" * 60)
    
    # Find first investment account
    investment_account = None
    for account in accounts.get('accounts', []):
        if account.get('type', {}).get('name') in ['investment', 'brokerage']:
            investment_account = account
            break
    
    if investment_account:
        account_id = investment_account.get('id')
        account_name = investment_account.get('displayName')
        
        print(f"\n📈 Holdings for: {account_name}\n")
        
        holdings = await mm.get_account_holdings(account_id)
        
        for holding in holdings.get('holdings', [])[:5]:
            ticker = holding.get('ticker', 'N/A')
            name = holding.get('name', 'Unknown')
            quantity = holding.get('quantity', 0)
            value = holding.get('currentValue', 0)
            
            print(f"  • {ticker} - {name}")
            print(f"    Quantity: {quantity}")
            print(f"    Value: ${value:,.2f}")
            print()
    else:
        print("\n(No investment accounts found)\n")
    
    # ========================================
    # EXAMPLE 7: Get Subscription Details
    # ========================================
    
    print("-" * 60)
    print("EXAMPLE 7: Get Subscription Details")
    print("-" * 60)
    
    subscription = await mm.get_subscription_details()
    if subscription:
        print(f"\nSubscription ID: {subscription.get('id', 'N/A')}")
        print(f"Payment Source: {subscription.get('paymentSource', 'N/A')}")
        print()
    
    print("=" * 60)
    print("✨ Demo completed successfully!")
    print("=" * 60)
    print("\n💡 Session saved for faster future logins!")
    print("📚 Check the README.md for more API methods:\n")
    print("   • get_transactions_summary()")
    print("   • get_transaction_tags()")
    print("   • create_transaction()")
    print("   • update_transaction()")
    print("   • set_budget_amount()")
    print("   • request_accounts_refresh()")
    print("   • And many more!")
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
