from unittest import TestCase

import main

class DummyCtxt:
    pass

good_event = {'credentials':{'user':'guest','password':''}, 'resource':{'provider_id':'10005'}}
bad_event = {'credentials':{'user':'bad_user','password':'bad_pass'}}
context = DummyCtxt()

class MainTests(TestCase):
    def test_validate_credentials_with_good_creds(self):
        main.validate_credentials(good_event, context)

    def test_get_metrics(self):
        print(main.get_metrics(good_event, context))

    def test_get_resources(self):
        expected = [
                {
                    "base": {
                        "name": "Zabbix.org",
                        "provider_created_at": "2017-01-01T12:00:00.000000Z"
                        },
                    "type": "server",
                    "id": "10005",
                    "details": {
                        "server": {
                            "image_detail": {
                                "type": "Linux"
                                },
                            "state": "running",
                            "ram_b": 4340441088,
                            "volumes_b": 33819574272
                            }
                        }
                    },
                {
                    "base": {
                        "name": "OpenStreetMap.lv",
                        "provider_created_at": "2017-01-01T12:00:00.000000Z"
                        },
                    "type": "server",
                    "id": "10019",
                    "details": {
                        "server": {
                            "image_detail": {
                                "type": None
                                },
                            "state": "stopped",
                            "ram_b": None,
                            "volumes_b": None
                            }
                        }
                    },
                {
                    "base": {
                        "name": "OpenStreetMap.org",
                        "provider_created_at": "2017-01-01T12:00:00.000000Z"
                        },
                    "type": "server",
                    "id": "10020",
                    "details": {
                        "server": {
                            "image_detail": {
                                "type": None
                                },
                            "state": "stopped",
                            "ram_b": None,
                            "volumes_b": None
                            }
                        }
                    },
                {
                        "base": {
                            "name": "Electricity in Latvia",
                            "provider_created_at": "2017-01-01T12:00:00.000000Z"
                            },
                        "type": "server",
                        "id": "10024",
                        "details": {
                            "server": {
                                "image_detail": {
                                    "type": None
                                    },
                                "state": "stopped",
                                "ram_b": None,
                                "volumes_b": None
                                }
                            }
                        },
                {
                        "base": {
                            "name": "development",
                            "provider_created_at": "2017-01-01T12:00:00.000000Z"
                            },
                        "type": "server",
                        "id": "10026",
                        "details": {
                            "server": {
                                "image_detail": {
                                    "type": None
                                    },
                                "state": "running",
                                "ram_b": None,
                                "volumes_b": None
                                }
                            }
                        }
                ]
        actual = main.get_resources(good_event, context)
        self.assertEqual(actual, expected)



