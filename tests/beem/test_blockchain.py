from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import super
import unittest
from parameterized import parameterized
from datetime import datetime, timedelta
import pytz
import time
from pprint import pprint
from beem import Steem
from beem.blockchain import Blockchain
from beem.block import Block
from beem.instance import set_shared_steem_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
nodes = ["wss://steemd.pevo.science", "wss://gtg.steem.house:8090", "wss://rpc.steemliberator.com", "wss://rpc.buildteam.io",
         "wss://rpc.steemviz.com", "wss://seed.bitcoiner.me", "wss://node.steem.ws", "wss://steemd.steemgigs.org", "wss://steemd.steemit.com",
         "wss://steemd.minnowsupportproject.org"]
nodes_appbase = ["https://api.steem.house", "https://api.steemit.com"]


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bts = Steem(
            node=nodes,
            nobroadcast=True,
            keys={"active": wif},
            num_retries=10
        )
        cls.appbase = Steem(
            node=nodes_appbase,
            nobroadcast=True,
            keys={"active": wif},
            num_retries=10
        )
        # from getpass import getpass
        # self.bts.wallet.unlock(getpass())
        set_shared_steem_instance(cls.bts)
        cls.bts.set_default_account("test")

        b = Blockchain(steem_instance=cls.bts)
        num = b.get_current_block_num()
        cls.start = num - 25
        cls.stop = num

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_blockchain(self, node_param):
        if node_param == "non_appbase":
            bts = self.bts
        else:
            bts = self.appbase
        b = Blockchain(steem_instance=bts)
        num = b.get_current_block_num()
        self.assertTrue(num > 0)
        self.assertTrue(isinstance(num, int))
        block = b.get_current_block()
        self.assertTrue(isinstance(block, Block))
        self.assertTrue((num - block.identifier) < 3)
        block_time = b.block_time(block.identifier)
        self.assertEqual(block.time(), block_time)
        block_timestamp = b.block_timestamp(block.identifier)
        timestamp = int(time.mktime(block.time().timetuple()))
        self.assertEqual(block_timestamp, timestamp)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_estimate_block_num(self, node_param):
        if node_param == "non_appbase":
            bts = self.bts
        else:
            bts = self.appbase
        b = Blockchain(steem_instance=bts)
        last_block = b.get_current_block()
        num = last_block.identifier
        old_block = Block(num - 60, steem_instance=bts)
        date = old_block.time()
        est_block_num = b.get_estimated_block_num(date, accurate=False)
        self.assertTrue((est_block_num - (old_block.identifier)) < 10)
        est_block_num = b.get_estimated_block_num(date, accurate=True)
        self.assertTrue((est_block_num - (old_block.identifier)) < 2)
        est_block_num = b.get_estimated_block_num(date, estimateForwards=True, accurate=True)
        self.assertTrue((est_block_num - (old_block.identifier)) < 2)
        est_block_num = b.get_estimated_block_num(date, estimateForwards=True, accurate=False)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_get_all_accounts(self, node_param):
        if node_param == "non_appbase":
            bts = self.bts
        else:
            bts = self.appbase
        b = Blockchain(steem_instance=bts)
        accounts = []
        for acc in b.get_all_accounts(steps=100, limit=100):
            accounts.append(acc)
        self.assertEqual(len(accounts), 100)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_awaitTX(self, node_param):
        if node_param == "non_appbase":
            bts = self.bts
        else:
            bts = self.appbase
        b = Blockchain(steem_instance=bts)
        trans = {'ref_block_num': 3855, 'ref_block_prefix': 1730859721,
                 'expiration': '2018-03-09T06:21:06', 'operations': [],
                 'extensions': [], 'signatures':
                 ['2033a872a8ad33c7d5b946871e4c9cc8f08a5809258355fc909058eac83'
                  '20ac2a872517a52b51522930d93dd2c1d5eb9f90b070f75f838c881ff29b11af98d6a1b']}
        with self.assertRaises(
            Exception
        ):
            b.awaitTxConfirmation(trans)

    @parameterized.expand([
        ("non_appbase"),
        ("appbase"),
    ])
    def test_stream(self, node_param):
        if node_param == "non_appbase":
            bts = self.bts
        else:
            bts = self.appbase
        b = Blockchain(steem_instance=bts)
        ops_stream = []
        opNames = ["transfer", "vote"]
        for op in b.stream(opNames=opNames, start=self.start, stop=self.stop):
            ops_stream.append(op)
        self.assertTrue(len(ops_stream) > 0)
        op_stat = b.ops_statistics(start=self.start, stop=self.stop)
        op_stat2 = {"transfer": 0, "vote": 0}
        for op in ops_stream:
            self.assertIn(op["type"], opNames)
            op_stat2[op["type"]] += 1
            self.assertTrue(op["block_num"] >= self.start)
            self.assertTrue(op["block_num"] <= self.stop)
        self.assertEqual(op_stat["transfer"], op_stat2["transfer"])
        self.assertEqual(op_stat["vote"], op_stat2["vote"])

        ops_ops = []
        for op in b.ops(start=self.start, stop=self.stop):
            ops_ops.append(op)
        self.assertTrue(len(ops_ops) > 0)
        op_stat3 = {"transfer": 0, "vote": 0}

        for op in ops_ops:
            if op["op"][0] in opNames:
                op_stat3[op["op"][0]] += 1
            self.assertTrue(op["block_num"] >= self.start)
            self.assertTrue(op["block_num"] <= self.stop)
        self.assertEqual(op_stat["transfer"], op_stat3["transfer"])
        self.assertEqual(op_stat["vote"], op_stat3["vote"])

        ops_blocks = []
        for op in b.blocks(start=self.start, stop=self.stop):
            ops_blocks.append(op)
        op_stat4 = {"transfer": 0, "vote": 0}
        self.assertTrue(len(ops_blocks) > 0)
        for block in ops_blocks:
            for tran in block["transactions"]:
                for op in tran['operations']:
                    if op[0] in opNames:
                        op_stat4[op[0]] += 1
            self.assertTrue(block.identifier >= self.start)
            self.assertTrue(block.identifier <= self.stop)
        self.assertEqual(op_stat["transfer"], op_stat4["transfer"])
        self.assertEqual(op_stat["vote"], op_stat4["vote"])

        ops_blocks = []
        for op in b.blocks():
            ops_blocks.append(op)
            break
        self.assertTrue(len(ops_blocks) == 1)
