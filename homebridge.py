from typing import Dict

import json
import requests
from Util import logger, Configuration, Singleton
from automations import *


@Singleton
class HomeBridge:
    def __init__(self):
        from main import SERVER, PORT, PIN_CODE
        from automations import automation_module as Runner

        self.url = "http://" + SERVER + ":" + PORT
        self.accessories = "/accessories"
        self.characteristics = "/characteristics"
        self.headers = {
            'Content-Type': "application/json",
            'authorization': PIN_CODE,
            'Sender': "LIFTTT"
        }
        self.modules: Dict[str, Runner] = {}

    def register_module(self, identifier: str, clazz):
        self.modules[identifier] = clazz

    def create_payload(self, aid, iid, value):
        values = [{'aid': aid, 'iid': iid, 'value': value}]
        payload = {'characteristics': values}
        payload = json.dumps(payload)
        return payload

    def request(self, method, aid, iid, value):
        return requests.request(method=method,
                                url=HomeBridge.url + HomeBridge.characteristics,
                                data=HomeBridge.create_payload(aid, iid, value),
                                headers=HomeBridge.headers)

    def get_accessories(self):
        try:
            return json.loads(
                requests.request("GET", url=self.url + self.accessories,
                                 headers=self.headers).text)
        except Exception as exception:
            logger.error(exception)

    def map_accessories(self):
        # noinspection PyUnresolvedReferences
        data = self.get_accessories()
        data = data['accessories']
        for i in data:
            aid = i['aid']
            name = None
            for services in i['services']:
                for characteristics in services['characteristics']:
                    if characteristics['type'] == "00000023-0000-1000-8000-0026BB765291":
                        name = characteristics
                    if characteristics['type'] == "00000025-0000-1000-8000-0026BB765291":
                        on = characteristics
                        # print("aid --->", aid)
                        # print("name -->", name)
                        # print("on -->", on)
                        # print("\n")
                        if name['value'] in Configuration.Instance().config.sections():
                            if Configuration.Instance().config[name['value']]['type'] in self.modules.keys():
                                Configuration.Instance().config[name['value']]['type'](name=name['value'],
                                        config=Configuration.Instance().config[name['value']],
                                        aid=aid,
                                        iid=on['iid'])
                            else:
                                logger.warning("No modules with the name %s",
                                               Configuration.Instance().config[name['value']][
                                                   'type'])
                                for k, v in self.modules.items():
                                    logger.warning("%s : %s", k, v)
