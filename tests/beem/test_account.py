from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from builtins import super
import unittest
import mock
from parameterized import parameterized
from pprint import pprint
from beem import Steem, exceptions
from beem.account import Account
from beem.amount import Amount
from beem.asset import Asset
from beem.utils import formatTimeString, get_node_list
from beem.instance import set_shared_steem_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.bts = Steem(
            node=get_node_list(appbase=False),
            nobroadcast=True,
            bundle=False,
            # Overwrite wallet to use this list of wifs only
            keys={"active": wif},
            num_retries=10
        )
        cls.appbase = Steem(
            node=get_node_list(appbase=True, testing=True),
            nobroadcast=True,
            bundle=False,
            # Overwrite wallet to use this list of wifs only
            keys={"active": wif},
            num_retries=10
        )
        cls.account = Account("test", full=True, steem_instance=cls.bts)
        cls.account_appbase = Account("test", full=True, steem_instance=cls.appbase)
        set_shared_steem_instance(cls.bts)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_account(self, node_param):
        if node_param == "non_appbase":
            stm = self.bts
            account = self.account
        else:
            stm = self.appbase
            account = self.account_appbase
        Account("test", steem_instance=stm)
        with self.assertRaises(
            exceptions.AccountDoesNotExistsException
        ):
            Account("DoesNotExistsXXX", steem_instance=stm)
        # asset = Asset("1.3.0")
        # symbol = asset["symbol"]
        self.assertEqual(account.name, "test")
        self.assertEqual(account["name"], account.name)
        self.assertIsInstance(account.get_balance("available", "SBD"), Amount)
        account.print_info()
        # self.assertIsInstance(account.balance({"symbol": symbol}), Amount)
        self.assertIsInstance(account.available_balances, list)
        self.assertTrue(account.virtual_op_count() > 0)

        # BlockchainObjects method
        account.cached = False
        self.assertTrue(list(account.items()))
        account.cached = False
        self.assertIn("id", account)
        account.cached = False
        # self.assertEqual(account["id"], "1.2.1")
        self.assertEqual(str(account), "<Account test>")
        self.assertIsInstance(Account(account), Account)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_history(self, node_param):
        if node_param == "non_appbase":
            account = self.account
            zero_element = 0
        else:
            account = self.account_appbase
            zero_element = 0  # Bug in steem
        h_all_raw = []
        for h in account.history_reverse(raw_output=True):
            h_all_raw.append(h)
        # h_all_raw = h_all_raw[zero_element:]
        h_list = []
        for h in account.history(stop=10, use_block_num=False, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], zero_element)
        self.assertEqual(h_list[-1][0], 10)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-1][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-11 + zero_element][1]['block'])
        h_list = []
        for h in account.history(start=1, stop=9, use_block_num=False, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 1)
        self.assertEqual(h_list[-1][0], 9)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        start = formatTimeString(h_list[0][1]["timestamp"])
        stop = formatTimeString(h_list[-1][1]["timestamp"])
        h_list = []
        for h in account.history(start=start, stop=stop, use_block_num=False, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 1)
        self.assertEqual(h_list[-1][0], 9)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        h_list = []
        for h in account.history_reverse(start=10, stop=0, use_block_num=False, batch_size=10, raw_output=False):
            h_list.append(h)
        self.assertEqual(h_list[0]['index'], 10)
        self.assertEqual(h_list[-1]['index'], zero_element)
        self.assertEqual(h_list[0]['block'], h_all_raw[-11 + zero_element][1]['block'])
        self.assertEqual(h_list[-1]['block'], h_all_raw[-1][1]['block'])
        h_list = []
        for h in account.history_reverse(start=9, stop=1, use_block_num=False, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 9)
        self.assertEqual(h_list[-1][0], 1)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        start = formatTimeString(h_list[0][1]["timestamp"])
        stop = formatTimeString(h_list[-1][1]["timestamp"])
        h_list = []
        for h in account.history_reverse(start=start, stop=stop, use_block_num=False, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 9)
        self.assertEqual(h_list[-1][0], 1)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=False, order=1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], zero_element)
        self.assertEqual(h_list[-1][0], 10)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-1][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-11 + zero_element][1]['block'])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=False, start=1, stop=9, order=1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 1)
        self.assertEqual(h_list[-1][0], 9)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        start = formatTimeString(h_list[0][1]["timestamp"])
        stop = formatTimeString(h_list[-1][1]["timestamp"])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=False, start=start, stop=stop, order=1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 1)
        self.assertEqual(h_list[-1][0], 9)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=False, order=-1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 10)
        self.assertEqual(h_list[-1][0], zero_element)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-11 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-1][1]['block'])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=False, start=9, stop=1, order=-1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 9)
        self.assertEqual(h_list[-1][0], 1)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        start = formatTimeString(h_list[0][1]["timestamp"])
        stop = formatTimeString(h_list[-1][1]["timestamp"])
        h_list = []
        for h in account.get_account_history(10, 10, start=start, stop=stop, order=-1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 9)
        self.assertEqual(h_list[-1][0], 1)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-2 + zero_element][1]['block'])

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_history2(self, node_param):
        if node_param == "non_appbase":
            stm = self.bts
        else:
            stm = self.appbase
        account = Account("gtg", steem_instance=stm)
        h_list = []
        max_index = account.virtual_op_count()
        for h in account.history(start=max_index - 4, stop=max_index, use_block_num=False, batch_size=2, raw_output=False):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i]["index"] - h_list[i - 1]["index"], 1)

        h_list = []
        for h in account.history(start=max_index - 4, stop=max_index, use_block_num=False, batch_size=6, raw_output=False):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i]["index"] - h_list[i - 1]["index"], 1)

        h_list = []
        for h in account.history(start=max_index - 4, stop=max_index, use_block_num=False, batch_size=2, raw_output=True):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i][0] - h_list[i - 1][0], 1)

        h_list = []
        for h in account.history(start=max_index - 4, stop=max_index, use_block_num=False, batch_size=6, raw_output=True):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i][0] - h_list[i - 1][0], 1)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_history_reverse2(self, node_param):
        if node_param == "non_appbase":
            stm = self.bts
        else:
            stm = self.appbase
        account = Account("gtg", steem_instance=stm)
        h_list = []
        max_index = account.virtual_op_count()
        for h in account.history_reverse(start=max_index, stop=max_index - 4, use_block_num=False, batch_size=2, raw_output=False):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i]["index"] - h_list[i - 1]["index"], -1)

        h_list = []
        for h in account.history_reverse(start=max_index, stop=max_index - 4, use_block_num=False, batch_size=6, raw_output=False):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i]["index"] - h_list[i - 1]["index"], -1)

        h_list = []
        for h in account.history_reverse(start=max_index, stop=max_index - 4, use_block_num=False, batch_size=6, raw_output=True):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i][0] - h_list[i - 1][0], -1)

        h_list = []
        for h in account.history_reverse(start=max_index, stop=max_index - 4, use_block_num=False, batch_size=2, raw_output=True):
            h_list.append(h)
        self.assertEqual(len(h_list), 5)
        for i in range(1, 5):
            self.assertEqual(h_list[i][0] - h_list[i - 1][0], -1)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_history_block_num(self, node_param):
        if node_param == "non_appbase":
            account = self.account
            zero_element = 0
        else:
            account = self.account_appbase
            zero_element = 0  # bug in steem
        h_all_raw = []
        for h in account.history_reverse(raw_output=True):
            h_all_raw.append(h)
        h_list = []
        for h in account.history(start=h_all_raw[-1][1]["block"], stop=h_all_raw[-11 + zero_element][1]["block"], use_block_num=True, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], zero_element)
        self.assertEqual(h_list[-1][0], 10)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-1][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-11 + zero_element][1]['block'])
        h_list = []
        for h in account.history_reverse(start=h_all_raw[-11 + zero_element][1]["block"], stop=h_all_raw[-1][1]["block"], use_block_num=True, batch_size=10, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 10)
        self.assertEqual(h_list[-1][0], zero_element)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-11 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-1][1]['block'])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=True, start=h_all_raw[-2 + zero_element][1]["block"], stop=h_all_raw[-10 + zero_element][1]["block"], order=1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 1)
        self.assertEqual(h_list[-1][0], 9)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-2 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        h_list = []
        for h in account.get_account_history(10, 10, use_block_num=True, start=h_all_raw[-10 + zero_element][1]["block"], stop=h_all_raw[-2 + zero_element][1]["block"], order=-1, raw_output=True):
            h_list.append(h)
        self.assertEqual(h_list[0][0], 9)
        self.assertEqual(h_list[-1][0], 1)
        self.assertEqual(h_list[0][1]['block'], h_all_raw[-10 + zero_element][1]['block'])
        self.assertEqual(h_list[-1][1]['block'], h_all_raw[-2 + zero_element][1]['block'])

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_account_props(self, node_param):
        if node_param == "non_appbase":
            account = self.account
        else:
            account = self.account_appbase
        rep = account.get_reputation()
        self.assertTrue(isinstance(rep, float))
        vp = account.get_voting_power()
        self.assertTrue(vp >= 0)
        self.assertTrue(vp <= 100)
        sp = account.get_steem_power()
        self.assertTrue(sp >= 0)
        vv = account.get_voting_value_SBD()
        self.assertTrue(vv >= 0)
        bw = account.get_bandwidth()
        self.assertTrue(bw['used'] <= bw['allocated'])
        followers = account.get_followers()
        self.assertTrue(isinstance(followers, list))
        following = account.get_following()
        self.assertTrue(isinstance(following, list))
        count = account.get_follow_count()
        self.assertEqual(count['follower_count'], len(followers))
        self.assertEqual(count['following_count'], len(following))

    def test_withdraw_vesting(self):
        w = self.account
        tx = w.withdraw_vesting("100 VESTS")
        self.assertEqual(
            (tx["operations"][0][0]),
            "withdraw_vesting"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["account"])

    def test_delegate_vesting_shares(self):
        w = self.account
        tx = w.delegate_vesting_shares("test1", "100 VESTS")
        self.assertEqual(
            (tx["operations"][0][0]),
            "delegate_vesting_shares"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["delegator"])

    def test_claim_reward_balance(self):
        w = self.account
        tx = w.claim_reward_balance()
        self.assertEqual(
            (tx["operations"][0][0]),
            "claim_reward_balance"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["account"])

    def test_cancel_transfer_from_savings(self):
        w = self.account
        tx = w.cancel_transfer_from_savings(0)
        self.assertEqual(
            (tx["operations"][0][0]),
            "cancel_transfer_from_savings"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["from"])

    def test_transfer_from_savings(self):
        w = self.account
        tx = w.transfer_from_savings(1, "STEEM", "")
        self.assertEqual(
            (tx["operations"][0][0]),
            "transfer_from_savings"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["from"])

    def test_transfer_to_savings(self):
        w = self.account
        tx = w.transfer_to_savings(1, "STEEM", "")
        self.assertEqual(
            (tx["operations"][0][0]),
            "transfer_to_savings"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["from"])

    def test_convert(self):
        w = self.account
        tx = w.convert("1 SBD")
        self.assertEqual(
            (tx["operations"][0][0]),
            "convert"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["owner"])

    def test_transfer_to_vesting(self):
        w = self.account
        tx = w.transfer_to_vesting("1 STEEM")
        self.assertEqual(
            (tx["operations"][0][0]),
            "transfer_to_vesting"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "test",
            op["from"])

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_json_export(self, node_param):
        if node_param == "non_appbase":
            account = self.account
            content = self.bts.rpc.get_accounts([account["name"]])[0]
        else:
            account = self.account_appbase
            content = self.appbase.rpc.find_accounts({'accounts': [account["name"]]}, api="database")["accounts"][0]

        keys = list(content.keys())
        json_content = account.json()

        for k in keys:
            if k not in "json_metadata" and k != 'reputation' and k != 'active_votes':
                self.assertEqual(content[k], json_content[k])
