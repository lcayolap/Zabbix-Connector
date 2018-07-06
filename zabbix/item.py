
class Item:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.key = kwargs.get('key_')
        self.last_value = kwargs.get('lastvalue')
        self.value_type = kwargs.get('value_type')
        self.item_id = kwargs.get('itemid')
        self.unit = kwargs.get('units')

    def __str__(self):
        return 'Item id:%s' % self.item_id

    def __repr__(self):
        return '<Item id:%s>' % self.item_id


