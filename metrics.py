import json
import requests
from datetime import datetime, timedelta


FALLBACK_TIME = "2017-10-31T00:00:00.000Z"

#dict of cmp key and zabbix key for tracked metrics
TRACKED_METRICS = [
        {
            'cmp_key':'cpu-usage',
            'cmp_unit':'percent',
            'native_key':'system.cpu.load', 
            'native_unit':0,
        },
        {
            'cmp_key':'memory-cache-bytes',
            'native_key':'vm.memory.size[cached]', 
            'cmp_unit':'B',
            'native_unit':3,
        },
        {
            'cmp_key':'memory-available-bytes',
            'native_key':'vm.memory.size[available]', 
            'cmp_unit':'B',
            'native_unit':3,
        },
        {
            'cmp_key':'ping',
            'native_key':'agent.ping', 
            'cmp_unit':'state',
            'native_unit':3,
        },
        
        {
            'cmp_key':'zabbix-queue',
            'native_key':'zabbix[queue]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'zabbix-queue-over-10',
            'native_key':'zabbix[queue,10m]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'zabbix-irc-users',
            'native_key':'zabbix.irc.users', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        
        {
            'cmp_key':'processes',
            'native_key':'proc.num[]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        
        {
            'cmp_key':'processes-running',
            'native_key':'proc.num[,,run]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-syslogd',
            'native_key':'proc.num[syslogd]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-rsyslogd',
            'native_key':'proc.num[rsyslogd]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-inetd',
            'native_key':'proc.num[inetd]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-sshd',
            'native_key':'proc.num[sshd]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-apache2',
            'native_key':'proc.num[apache2]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-httpd2-prefork',
            'native_key':'proc.num[httpd2-prefork]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'processes-running-httpd',
            'native_key':'proc.num[httpd]', 
            'cmp_unit':'count',
            'native_unit':3,
        },
        {
            'cmp_key':'http-server',
            'native_key':'net.tcp.service[http]', 
            'cmp_unit':'state',
            'native_unit':3,
        },
        
        
    ]
    
    


def get_metrics(event, context):
    host_id = event.get('resource',{}).get('provider_id', '10005')
    try:
        metrics = []
        
        last_update = event.get('last_update', FALLBACK_TIME)
        #This timedelta hack for the last_update issue in cmp
        time_from = from_cmp_time(last_update) - timedelta(hours=1)
        time_till = datetime.utcnow()

        for m in TRACKED_METRICS:
            cmp_key = m.get('cmp_key')
            cmp_unit = m.get('cmp_unit')
            native_key = m.get('native_key')
            native_unit = m.get('native_unit')
            
            results = fetch(host_id, native_key, time_from, time_till, native_unit)

            metrics += [zabbix_to_cmp(cmp_key, i, cmp_unit) for i in results]

        data = {
            "metrics": metrics,
            "last_update": time_till.isoformat() + "Z"
            }
        return data
    except Exception as e:
        raise #Exception(e.message + ' and event data: ' + str(event))

def from_cmp_time(time_string):
    return datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S.%fZ')

def fetch(host_id, metric_name, time_from, time_till, native_unit):
    url = "http://zabbix.org/zabbix/api_jsonrpc.php"
    headers = { "Content-Type": "application/json-rpc" }

    token = "9288114a91fe359ff1dd870598bb0d04"
    
    time_from_timestamp = (time_from - datetime(1970, 1, 1)).total_seconds()
    time_till_timestamp = (time_till - datetime(1970, 1, 1)).total_seconds()

    p1 = {
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {
                    "output":[
                        "itemid",
                        ],
                    "hostids":host_id,
                    "search":{ "key_" : metric_name }
                    
                },
                "id": 1,
                "auth":token
    }
    
    item_response = requests.post(url, headers=headers, data=json.dumps(p1))
    result = item_response.json().get('result')
    if result:
        item_id = result[0].get('itemid')
        
        print(result)
    
        payload = {
                    "jsonrpc": "2.0",
                    "method": "history.get",
                    "params": {
                        "history": native_unit,
                        "itemids": item_id,
                        "time_from": time_from_timestamp,
                        "time_till": time_till_timestamp,
                        },
                    "id": 2,
                    "auth":token
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    
        if response.status_code == 200:
            return response.json().get('result',[])
    
    return []

def zabbix_to_cmp(cmp_key, data, cmp_unit):
    formatter = get_formatter(cmp_key, cmp_unit)
    
    return {
            "metric": cmp_key,
            "value": formatter.format_value(data),
            "time": formatter.format_time(data),
            "unit": cmp_unit,
    }
    
def get_formatter(cmp_key, cmp_unit):
    formatters = {
        'cpu-usage':CpuUsageFormatter,
    }
    
    return formatters.get(cmp_key, Formatter)()
        
        
class Formatter:
    def format_value(self, data):
        return int(data.get('value'))
    
    def format_time(self, data):
        epoch = datetime.fromtimestamp(int(data.get('clock')))
        microsecs = self._nano_to_microseconds(data.get('ns'))
        total = self._add_microseconds(epoch, microsecs)
        return total.isoformat() + "Z"
            
    def _nano_to_microseconds(self, nanoseconds):
        """Just ignore last three digits and return time in ms"""
        return str(nanoseconds)[:-3]
        
    def _add_microseconds(self, time_obj, microseconds):
        return time_obj + timedelta(microseconds=int(microseconds))


class CpuUsageFormatter(Formatter):
    def format_value(self, data):
        return float(data.get('value'))*100
        


        
