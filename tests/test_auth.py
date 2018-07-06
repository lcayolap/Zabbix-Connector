from unittest import TestCase

from zabbix.client import ZabbixClient, AuthenticationError
from zabbix.host import Host
from zabbix.item import Item


class ZabbixTests(TestCase):
    def setUp(self):
        self.client = ZabbixClient('guest','')

    def test_get_token_with_bad_creds(self):
        c = ZabbixClient('bad', 'password')
        with self.assertRaises(AuthenticationError):
            c.token

    def test_get_token_with_good_creds(self):
        self.assertIsNotNone(self.client.token)
#
#    def test_list_hosts(self):
#        hosts = self.client.hosts()
#        for h in hosts:
#            self.assertIsInstance(h, Host)
#
#    def test_list_items(self):
#        items = self.client.items('10005')
#        for h in items:
#            self.assertIsInstance(h, Item)
