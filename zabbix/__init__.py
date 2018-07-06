from client import ZabbixClient


def get_client(event, context):
    user = event.get('credentials',{}).get('user')
    password = event.get('credentials',{}).get('password')
    return ZabbixClient(user, password)


