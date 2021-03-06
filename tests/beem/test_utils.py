from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import unittest
from datetime import datetime
from beem.utils import (
    formatTimedelta,
    assets_from_string,
    resolve_authorperm,
    resolve_authorpermvoter,
    construct_authorperm,
    construct_authorpermvoter,
    sanitize_permlink,
    derive_permlink,
    resolve_root_identifier,
    make_patch,
    remove_from_dict
)


class Testcases(unittest.TestCase):
    def test_constructAuthorperm(self):
        self.assertEqual(construct_authorperm("A", "B"), "@A/B")
        self.assertEqual(construct_authorperm({'author': "A", 'permlink': "B"}), "@A/B")

    def test_resolve_root_identifier(self):
        self.assertEqual(resolve_root_identifier("/a/@b/c"), ("@b/c", "a"))

    def test_constructAuthorpermvoter(self):
        self.assertEqual(construct_authorpermvoter("A", "B", "C"), "@A/B|C")
        self.assertEqual(construct_authorpermvoter({'author': "A", 'permlink': "B", 'voter': 'C'}), "@A/B|C")
        self.assertEqual(construct_authorpermvoter({'authorperm': "A/B", 'voter': 'C'}), "@A/B|C")

    def test_assets_from_string(self):
        self.assertEqual(assets_from_string('USD:BTS'), ['USD', 'BTS'])
        self.assertEqual(assets_from_string('BTSBOTS.S1:BTS'), ['BTSBOTS.S1', 'BTS'])

    def test_authorperm_resolve(self):
        self.assertEqual(resolve_authorperm('theaussiegame/cryptokittie-giveaway-number-2'),
                         ('theaussiegame', 'cryptokittie-giveaway-number-2'))
        self.assertEqual(resolve_authorperm('holger80/virtuelle-cloud-mining-ponzi-schemen-auch-bekannt-als-hypt'),
                         ('holger80', 'virtuelle-cloud-mining-ponzi-schemen-auch-bekannt-als-hypt'))
        self.assertEqual(resolve_authorperm('https://steemit.com/deutsch/holger80/virtuelle-cloud-mining-ponzi-schemen-auch-bekannt-als-hypt'),
                         ('holger80', 'virtuelle-cloud-mining-ponzi-schemen-auch-bekannt-als-hypt'))

    def test_authorpermvoter_resolve(self):
        self.assertEqual(resolve_authorpermvoter('theaussiegame/cryptokittie-giveaway-number-2|test'),
                         ('theaussiegame', 'cryptokittie-giveaway-number-2', 'test'))
        self.assertEqual(resolve_authorpermvoter('holger80/virtuelle-cloud-mining-ponzi-schemen-auch-bekannt-als-hypt|holger80'),
                         ('holger80', 'virtuelle-cloud-mining-ponzi-schemen-auch-bekannt-als-hypt', 'holger80'))

    def test_sanitizePermlink(self):
        self.assertEqual(sanitize_permlink("aAf_0.12"), "aaf-0-12")
        self.assertEqual(sanitize_permlink("[](){}|"), "")

    def test_derivePermlink(self):
        self.assertEqual(derive_permlink("Hello World"), "hello-world")
        self.assertEqual(derive_permlink("aAf_0.12"), "aaf-0-12")
        self.assertEqual(derive_permlink("[](){}"), "")

    def test_patch(self):
        self.assertEqual(make_patch("aa", "ab"), '@@ -1 +1 @@\n-aa\n+ab\n')
        self.assertEqual(make_patch("Hello!\n Das ist ein Test!\nEnd.\n", "Hello!\n This is a Test\nEnd.\n"),
                         '@@ -1,3 +1,3 @@\n Hello!\n- Das ist ein Test!\n+ This is a Test\n End.\n')

    def test_formatTimedelta(self):
        now = datetime.now()
        self.assertEqual(formatTimedelta(now - now), '0:00:00')

    def test_remove_from_dict(self):
        a = {'a': 1, 'b': 2}
        b = {'b': 2}
        self.assertEqual(remove_from_dict(a, ['b'], keep_keys=True), {'b': 2})
        self.assertEqual(remove_from_dict(a, ['a'], keep_keys=False), {'b': 2})
        self.assertEqual(remove_from_dict(b, ['b'], keep_keys=True), {'b': 2})
        self.assertEqual(remove_from_dict(b, ['a'], keep_keys=False), {'b': 2})
        self.assertEqual(remove_from_dict(b, [], keep_keys=True), {})
        self.assertEqual(remove_from_dict(a, ['a', 'b'], keep_keys=False), {})
