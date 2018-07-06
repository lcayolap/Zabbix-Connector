class Host:
    def __init__(self, *args, **kwargs):
        self.available = kwargs.get('available')
        self.description = kwargs.get('description')
        self.name = kwargs.get('name')
        self.host_id = kwargs.get('hostid')

        inventory = kwargs.get('inventory')
        if inventory:
            self.os = inventory.get('os')
        else:
            self.os = None
        self._client = kwargs.get('client')

    def __repr__(self):
        return '<Host id:%s>' % self.host_id

    def to_cmp(self):
        d = {
                "base": {
                    "name": self.name,
                    "provider_created_at": "2017-01-01T12:00:00.000000Z"
                    },
                "type": "server",
                "id": self.host_id,
                "details": {
                    "server": {
                        "image_detail": { "type": self.os},
                        "state": 'running' if self.available == '1' else 'stopped',
                        "ram_b": self.get_memory(),
                        "volumes_b": self.get_volume()
                        }
                    }
                }
        return d

    def get_memory(self):
        item = self._client.search_item('vm.memory.size[total]', self.host_id)
        if item:
            return int(item.last_value)


    def get_volume(self):
        item = self._client.search_item('vfs.fs.size[/,total]', self.host_id)
        if item:
            return int(item.last_value)


