import os
import pickle
import unittest
from unittest.mock import patch

import json
from gql import Client
from monarch import Monarch
from monarch.monarch import LoginFailedException


class TestMonarch(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """
        Set up any necessary data or variables for the tests here.
        This method will be called before each test method is executed.
        """
        with open("temp_session.pickle", "wb") as fh:
            session_data = {
                "cookies": {"test_cookie": "test_value"},
                "token": "test_token",
            }
            pickle.dump(session_data, fh)
        self.monarch_money = Monarch()
        self.monarch_money.load_session("temp_session.pickle")

    @patch.object(Client, "execute_async")
    async def test_get_accounts(self, mock_execute_async):
        """
        Test the get_accounts method.
        """
        mock_execute_async.return_value = TestMonarch.loadTestData(
            filename="get_accounts.json",
        )
        result = await self.monarch_money.get_accounts()
        mock_execute_async.assert_called_once()
        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(len(result["accounts"]), 7, "Expected 7 accounts")
        self.assertEqual(
            result["accounts"][0]["displayName"],
            "Brokerage",
            "Expected displayName to be Brokerage",
        )
        self.assertEqual(
            result["accounts"][1]["currentBalance"],
            1000.02,
            "Expected currentBalance to be 1000.02",
        )
        self.assertFalse(
            result["accounts"][2]["isAsset"],
            "Expected isAsset to be False",
        )
        self.assertEqual(
            result["accounts"][3]["subtype"]["display"],
            "Roth IRA",
            "Expected subtype display to be 'Roth IRA'",
        )
        self.assertFalse(
            result["accounts"][4]["isManual"],
            "Expected isManual to be False",
        )
        self.assertEqual(
            result["accounts"][5]["institution"]["name"],
            "Rando Employer Investments",
            "Expected institution name to be 'Rando Employer Investments'",
        )
        self.assertEqual(
            result["accounts"][6]["id"],
            "90000000030",
            "Expected id to be '90000000030'",
        )
        self.assertEqual(
            result["accounts"][6]["type"]["name"],
            "loan",
            "Expected type name to be 'loan'",
        )

    @patch.object(Client, "execute_async")
    async def test_get_transactions_summary(self, mock_execute_async):
        """
        Test the get_transactions_summary method.
        """
        mock_execute_async.return_value = TestMonarch.loadTestData(
            filename="get_transactions_summary.json",
        )
        result = await self.monarch_money.get_transactions_summary()
        mock_execute_async.assert_called_once()
        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(
            result["aggregates"][0]["summary"]["sumIncome"],
            50000,
            "Expected sumIncome to be 50000",
        )

    @patch.object(Client, "execute_async")
    async def test_delete_account(self, mock_execute_async):
        """
        Test the delete_account method.
        """

        mock_execute_async.return_value = {
            "deleteAccount": {
                "deleted": True,
                "errors": None,
                "__typename": "DeleteAccountMutation",
            }
        }

        result = await self.monarch_money.delete_account("170123456789012345")

        mock_execute_async.assert_called_once()

        kwargs = mock_execute_async.call_args.kwargs
        self.assertEqual(kwargs["operation_name"], "Common_DeleteAccount")
        self.assertEqual(kwargs["variable_values"], {"id": "170123456789012345"})

        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(result["deleteAccount"]["deleted"], True)
        self.assertEqual(result["deleteAccount"]["errors"], None)

    @patch.object(Client, "execute_async")
    async def test_get_account_type_options(self, mock_execute_async):
        """
        Test the get_account_type_options method.
        """
        # Mock the execute_async method to return a test result
        mock_execute_async.return_value = TestMonarch.loadTestData(
            filename="get_account_type_options.json",
        )

        # Call the get_account_type_options method
        result = await self.monarch_money.get_account_type_options()

        # Assert that the execute_async method was called once
        mock_execute_async.assert_called_once()

        # Assert that the result is not None
        self.assertIsNotNone(result, "Expected result to not be None")

        # Assert that the result matches the expected output
        self.assertEqual(
            len(result["accountTypeOptions"]), 10, "Expected 10 account type options"
        )
        self.assertEqual(
            result["accountTypeOptions"][0]["type"]["name"],
            "depository",
            "Expected first account type option name to be 'depository'",
        )
        self.assertEqual(
            result["accountTypeOptions"][1]["type"]["name"],
            "brokerage",
            "Expected second account type option name to be 'brokerage'",
        )
        self.assertEqual(
            result["accountTypeOptions"][2]["type"]["name"],
            "real_estate",
            "Expected third account type option name to be 'real_estate'",
        )

    @patch.object(Client, "execute_async")
    async def test_get_account_holdings(self, mock_execute_async):
        """
        Test the get_account_holdings method.
        """
        # Mock the execute_async method to return a test result
        mock_execute_async.return_value = TestMonarch.loadTestData(
            filename="get_account_holdings.json",
        )

        # Call the get_account_holdings method
        result = await self.monarch_money.get_account_holdings(account_id=1234)

        # Assert that the execute_async method was called once
        mock_execute_async.assert_called_once()

        # Assert that the result is not None
        self.assertIsNotNone(result, "Expected result to not be None")

        # Assert that the result matches the expected output
        self.assertEqual(
            len(result["portfolio"]["aggregateHoldings"]["edges"]),
            3,
            "Expected 3 holdings",
        )
        self.assertEqual(
            result["portfolio"]["aggregateHoldings"]["edges"][0]["node"]["quantity"],
            101,
            "Expected first holding to be 101 in quantity",
        )
        self.assertEqual(
            result["portfolio"]["aggregateHoldings"]["edges"][1]["node"]["totalValue"],
            10000,
            "Expected second holding to be 10000 in total value",
        )
        self.assertEqual(
            result["portfolio"]["aggregateHoldings"]["edges"][2]["node"]["holdings"][0][
                "name"
            ],
            "U S Dollar",
            "Expected third holding name to be 'U S Dollar'",
        )

    @patch.object(Client, "execute_async")
    async def test_get_budgets(self, mock_execute_async):
        """
        Test the get_accounts method.
        """
        mock_execute_async.return_value = TestMonarch.loadTestData(
            filename="get_budgets.json",
        )
        result = await self.monarch_money.get_budgets(
            start_date="2024-12-01", end_date="2025-2-31"
        )
        mock_execute_async.assert_called_once()
        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(
            len(result["budgetData"]["monthlyAmountsByCategory"]),
            2,
            "Expected 2 categories",
        )
        self.assertEqual(len(result["categoryGroups"]), 2, "Expected 2 category groups")
        self.assertEqual(len(result["goalsV2"]), 1, "Expected 1 goal")

    @patch.object(Client, "execute_async")
    async def test_receipt_and_ordering_endpoints(self, mock_execute_async):
        """
        Ensures new receipt/ordering endpoint wrappers call the expected
        GraphQL operation names and variables.
        """
        mock_execute_async.return_value = {}

        cases = [
            (
                "add_transaction_attachment",
                "Common_AddTransactionAttachment",
                {"input": {"transactionId": "txn-1", "publicId": "pub-1"}},
                lambda: self.monarch_money.add_transaction_attachment(
                    {"transactionId": "txn-1", "publicId": "pub-1"}
                ),
            ),
            (
                "complete_retail_sync",
                "Common_CompleteRetailSync",
                {"syncId": "sync-1"},
                lambda: self.monarch_money.complete_retail_sync("sync-1"),
            ),
            (
                "create_retail_sync",
                "Common_CreateRetailSync",
                {"input": {"vendor": "amazon"}},
                lambda: self.monarch_money.create_retail_sync({"vendor": "amazon"}),
            ),
            (
                "delete_retail_sync",
                "Common_DeleteRetailSync",
                {"syncId": "sync-2"},
                lambda: self.monarch_money.delete_retail_sync("sync-2"),
            ),
            (
                "get_transaction_attachment_upload_info",
                "Common_GetTransactionAttachmentUploadInfo",
                {"transactionId": "11111111-1111-1111-1111-111111111111"},
                lambda: self.monarch_money.get_transaction_attachment_upload_info(
                    "11111111-1111-1111-1111-111111111111"
                ),
            ),
            (
                "match_retail_transaction",
                "Common_MatchRetailTransaction",
                {"retailTransactionId": "retail-1", "transactionId": "txn-2"},
                lambda: self.monarch_money.match_retail_transaction(
                    "retail-1", "txn-2"
                ),
            ),
            (
                "start_retail_sync",
                "Common_StartRetailSync",
                {"syncId": "sync-3"},
                lambda: self.monarch_money.start_retail_sync("sync-3"),
            ),
            (
                "update_account_group_order",
                "Common_UpdateAccountGroupOrder",
                {"input": {"order": ["asset", "liability"]}},
                lambda: self.monarch_money.update_account_group_order(
                    {"order": ["asset", "liability"]}
                ),
            ),
            (
                "update_retail_order",
                "Common_UpdateRetailOrder",
                {"input": {"id": "order-1", "merchantName": "Target"}},
                lambda: self.monarch_money.update_retail_order(
                    {"id": "order-1", "merchantName": "Target"}
                ),
            ),
            (
                "update_retail_vendor_settings",
                "Common_UpdateRetailVendorSettings",
                {
                    "input": {
                        "vendor": "amazon",
                        "shouldCategorizeAndSplitTransactions": True,
                    }
                },
                lambda: self.monarch_money.update_retail_vendor_settings(
                    {
                        "vendor": "amazon",
                        "shouldCategorizeAndSplitTransactions": True,
                    }
                ),
            ),
            (
                "update_transaction_tag_order",
                "Common_UpdateTransactionTagOrder",
                {"tagId": "tag-1", "order": 4},
                lambda: self.monarch_money.update_transaction_tag_order("tag-1", 4),
            ),
            (
                "delete_transaction_attachment_mobile",
                "Mobile_DeleteAttachment",
                {"attachmentId": "22222222-2222-2222-2222-222222222222"},
                lambda: self.monarch_money.delete_transaction_attachment_mobile(
                    "22222222-2222-2222-2222-222222222222"
                ),
            ),
            (
                "update_category_group_order_mobile",
                "Mobile_UpdateCategoryGroupOrderMutation",
                {"id": "33333333-3333-3333-3333-333333333333", "order": 3},
                lambda: self.monarch_money.update_category_group_order_mobile(
                    "33333333-3333-3333-3333-333333333333", 3
                ),
            ),
            (
                "update_category_order_mobile",
                "Mobile_UpdateCategoryOrderMutation",
                {
                    "id": "44444444-4444-4444-4444-444444444444",
                    "categoryGroupId": "55555555-5555-5555-5555-555555555555",
                    "order": 2,
                },
                lambda: self.monarch_money.update_category_order_mobile(
                    "44444444-4444-4444-4444-444444444444",
                    "55555555-5555-5555-5555-555555555555",
                    2,
                ),
            ),
            (
                "cancel_subscription_sponsorship",
                "Web_BillingSettingsCancelSponsorship",
                {"input": {"subscriptionSponsorshipId": "sponsor-1"}},
                lambda: self.monarch_money.cancel_subscription_sponsorship(
                    {"subscriptionSponsorshipId": "sponsor-1"}
                ),
            ),
            (
                "delete_transaction_attachment_web",
                "Web_TransactionDrawerDeleteAttachment",
                {"id": "66666666-6666-6666-6666-666666666666"},
                lambda: self.monarch_money.delete_transaction_attachment_web(
                    "66666666-6666-6666-6666-666666666666"
                ),
            ),
            (
                "update_account_order",
                "Web_UpdateAccountOrder",
                {"input": {"id": "acct-1", "order": 1}},
                lambda: self.monarch_money.update_account_order(
                    {"id": "acct-1", "order": 1}
                ),
            ),
            (
                "update_category_group_order_web",
                "Web_UpdateCategoryGroupOrder",
                {"id": "77777777-7777-7777-7777-777777777777", "order": 1},
                lambda: self.monarch_money.update_category_group_order_web(
                    "77777777-7777-7777-7777-777777777777", 1
                ),
            ),
            (
                "update_category_order_web",
                "Web_UpdateCategoryOrder",
                {
                    "id": "88888888-8888-8888-8888-888888888888",
                    "categoryGroupId": "99999999-9999-9999-9999-999999999999",
                    "order": 5,
                },
                lambda: self.monarch_money.update_category_order_web(
                    "88888888-8888-8888-8888-888888888888",
                    "99999999-9999-9999-9999-999999999999",
                    5,
                ),
            ),
            (
                "update_dismissed_retail_sync_banner",
                "Web_UpdateDismissedRetailSyncBanner",
                {
                    "dismissedRetailSyncBanner": True,
                    "dismissedRetailSyncTargetBannerAt": "2026-02-19T00:00:00Z",
                },
                lambda: self.monarch_money.update_dismissed_retail_sync_banner(
                    True, "2026-02-19T00:00:00Z"
                ),
            ),
            (
                "update_transaction_rule_order",
                "Web_UpdateRuleOrderMutation",
                {"id": "rule-1", "order": 7},
                lambda: self.monarch_money.update_transaction_rule_order("rule-1", 7),
            ),
            (
                "get_retail_extension_settings",
                "Common_GetRetailExtensionSettings",
                {},
                lambda: self.monarch_money.get_retail_extension_settings(),
            ),
            (
                "get_retail_sync",
                "Common_RetailSyncQuery",
                {"syncId": "sync-4"},
                lambda: self.monarch_money.get_retail_sync("sync-4"),
            ),
            (
                "get_retail_syncs_with_total",
                "Common_RetailSyncsQueryWithTotal",
                {
                    "filters": {"status": "completed"},
                    "offset": 5,
                    "limit": 10,
                    "includeTotalCount": True,
                },
                lambda: self.monarch_money.get_retail_syncs_with_total(
                    filters={"status": "completed"},
                    offset=5,
                    limit=10,
                    include_total_count=True,
                ),
            ),
            (
                "get_transaction_attachment",
                "Mobile_GetAttachmentDetails",
                {"attachmentId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
                lambda: self.monarch_money.get_transaction_attachment(
                    "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
                ),
            ),
            (
                "get_user_dismissed_retail_sync_banner",
                "Web_GetUserDismissedRetailSyncBanner",
                {},
                lambda: self.monarch_money.get_user_dismissed_retail_sync_banner(),
            ),
            (
                "get_user_has_configured_extension",
                "Web_GetUserHasConfiguredExtension",
                {},
                lambda: self.monarch_money.get_user_has_configured_extension(),
            ),
        ]

        for case_name, expected_operation, expected_variables, invoke in cases:
            with self.subTest(case=case_name):
                mock_execute_async.reset_mock()
                await invoke()
                kwargs = mock_execute_async.call_args.kwargs
                self.assertEqual(kwargs["operation_name"], expected_operation)
                self.assertEqual(kwargs["variable_values"], expected_variables)

    async def test_login(self):
        """
        Test the login method with empty values for email and password.
        """
        with self.assertRaises(LoginFailedException):
            await self.monarch_money.login(use_saved_session=False)
        with self.assertRaises(LoginFailedException):
            await self.monarch_money.login(
                email="", password="", use_saved_session=False
            )

    @patch("builtins.input", return_value="")
    @patch("getpass.getpass", return_value="")
    async def test_interactive_login(self, _input_mock, _getpass_mock):
        """
        Test the interactive_login method with empty values for email and password.
        """
        with self.assertRaises(LoginFailedException):
            await self.monarch_money.interactive_login(use_saved_session=False)

    @classmethod
    def loadTestData(cls, filename) -> dict:
        filename = f"{os.path.dirname(os.path.realpath(__file__))}/{filename}"
        with open(filename, "r") as file:
            return json.load(file)

    def tearDown(self):
        """
        Tear down any necessary data or variables for the tests here.
        This method will be called after each test method is executed.
        """
        self.monarch_money.delete_session("temp_session.pickle")


if __name__ == "__main__":
    unittest.main()
