import zabbix
import metrics

def get_resources(event, context):
    client = zabbix.get_client(event, context)
    hosts = client.hosts()
    return [h.to_cmp() for h in hosts]

def get_metrics(event, context):
    return metrics.get_metrics(event, context)

def validate_credentials(event, context):
    try:
        _ = zabbix.get_client(event, context).token
        return True
    except:
        return False




