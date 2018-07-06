import requests
import json

from host import Host
from item import Item

#TODO(kashif) Can zabbix url change for different accounts?
URL = 'http://zabbix.org/zabbix/api_jsonrpc.php'
HEADERS = {'Content-Type':'application/json-rpc'}


class BaseClient:
    def __init__(self, *args, **kwargs):
        self._url = kwargs.get('url', URL)
        self._headers = kwargs.get('headers', HEADERS)

    def _http(self, method, params=None, token=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
            "auth": token}
        r = requests.post(self._url, headers=self._headers, data=json.dumps(payload))

        if r.status_code != 200 or 'error' in r.json():
            error = ''
            try:
                error = r.json().get('error')
            except:
                pass
            raise HttpError('Request returned error %s input: %s' % (error, params))

        return r.json().get('result')

class HttpError(Exception):
    pass

class ZabbixClient(BaseClient):
    def __init__(self, username, password):
        self._creds = {'user':username, 'password':password}
        self._token = None
        BaseClient.__init__(self)

    @property
    def token(self):
        if not self._token:
            try:
                self._token = self._http('user.login', self._creds)
                if not self._token:
                    raise AuthenticationError('Unable to fetch token')
            except Exception as e:
                raise AuthenticationError(e.message)
        return self._token

    def hosts(self):
        hosts = self._http('host.get',{'selectInterfaces':'extend','selectInventory': [ 'os' ]}, self.token)
        for h in hosts:
            yield Host(client=self, **h)

    def items(self, host_id):
        """Return all items for given host"""
        items = self._http('item.get',{'output': [ 'name', 'key_', 'lastvalue','value_type', 'units' ], 'hostids':host_id}, self.token)
        for h in items:
            yield Item(**h)

    def get_item(self, item_id):
        data = self._http('item.get', {'output': [ 'name', 'key_', 'lastvalue','value_type', 'units' ],'itemids':item_id}, self.token)
        return Item(**data[0]) #One day I will hate myself for this line


    def search_item(self, key, host_id):
        data = self._http('item.get',
                            {'output': [ 'name', 'key_', 'lastvalue','value_type', 'units' ],
                            'hostids':host_id, 'search':{'key_':key}}, self.token)
        if data:
            return Item(**data[0])
        else:
            return None

    def get_points(self, item, time_from, time_till):
        """Return historical points for given item for given time period"""
        points = self._http('history.get',
                            {'history': item.value_type, 'itemids': item.item_id,
                             'time_from':time_from, 'time_till': time_till}, self.token)
        for h in points:
            yield h


class AuthenticationError(Exception):
    pass
