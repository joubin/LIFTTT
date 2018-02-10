import json
import re
import threading
import time
from abc import abstractmethod
from datetime import datetime

import requests
from pygtail import Pygtail

from Util import Observer, Observable, Singleton, Configuration

SERVER = Configuration.Instance().config["DEFAULT"]["server"]
PORT = Configuration.Instance().config["DEFAULT"]["port"]
PIN_CODE = Configuration.Instance().config["DEFAULT"]["auth_code"]


class Runner(Observer):
    def __init__(self, name, config):
        self.name = name
        self.command = config
        self.thread: threading.Thread = None
        self.stop = False

    def run_action(self):
        print("Running Action")
        self.stop = False
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def void_action(self):
        print("Stopping Action")
        self.stop = True
        self.thread.join()
        print("Action Stopped")

    @abstractmethod
    def is_trigger(self, line):
        pass

    @abstractmethod
    def main(self):
        raise NotImplementedError()


class AutoOff(Runner):
    # auto_off = 30s
    # auto_off = 30m
    auto_off_time_regex = re.compile("(\d*).*(\w)", re.IGNORECASE)

    def __init__(self, name, config, aid, iid):
        super().__init__(name, config)
        self.time = self.parse_auto_off(config['auto_off'])
        self.aid = aid
        self.iid = iid
        self.on_off_regex = re.compile(config['on_off_regex'], re.IGNORECASE)
        TailF.Instance().register(self)

    @staticmethod
    def parse_auto_off(input_string, default_duration=1):
        match = AutoOff.auto_off_time_regex.match(input_string)
        if match is not None:
            duration = float(match.groups()[0])
            multiplier = match.groups()[1]
            if multiplier == "m":
                multiplier = 60
            elif multiplier == "h":
                multiplier = 60 * 60
            else:
                multiplier = 1
            return duration * multiplier
        return default_duration

    def update(self, payload):
        if self.is_trigger(payload, "On"):
            self.run_action()
        elif self.is_trigger(payload, "Off"):
            self.void_action()
        else:
            print("Doing nothing")

    def is_trigger(self, line, state : str = "On"):
        match = self.on_off_regex.match(line)
        if match is None:
            return False
        return match.groups()[2] == self.name and match.groups()[3] == state

    def wait(self, time_seconds: int = 0):
        _time = time_seconds
        while _time != 0:
            time.sleep(1)
            _time -= 1
            if self.stop is True:
                raise InterruptedError

    def main(self):
        print("running logic and waiting", self.time)
        try:
            self.wait(self.time)
            HomeBridge.request("PUT", self.aid, self.iid, False)
        except InterruptedError:
            pass


class HomeBridge:
    url = "http://" + SERVER + ":" + PORT
    accessories = "/accessories"
    characteristics = "/characteristics"
    headers = {
        'Content-Type': "application/json",
        'authorization': PIN_CODE,
        'Sender': "LIFTTT"
    }

    @staticmethod
    def create_payload(aid, iid, value):
        values = [{'aid': aid, 'iid': iid, 'value': value}]
        payload = {'characteristics': values}
        payload = json.dumps(payload)
        return payload

    @staticmethod
    def request(method, aid, iid, value):
        return requests.request(method=method,
                                url=HomeBridge.url + HomeBridge.characteristics,
                                data=HomeBridge.create_payload(aid, iid, value),
                                headers=HomeBridge.headers)

    @staticmethod
    def get_accessories():
        return json.loads(
            requests.request("GET", url=HomeBridge.url + HomeBridge.accessories,
                             headers=HomeBridge.headers).text)

    @staticmethod
    def map_accessories():
        data = HomeBridge.get_accessories()
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
                            if Configuration.Instance().config[name['value']]['type'] == "auto_off":
                                AutoOff(name=name['value'],
                                        config=Configuration.Instance().config[name['value']], aid=aid,
                                        iid=on['iid'])


@Singleton
class TailF(Observable):
    log = Configuration.Instance().config['DEFAULT']['log_file']

    def __init__(self, file_path=log):
        super().__init__()
        self.log_file_path = file_path
        self.pygtail = Pygtail(self.log_file_path)

    @staticmethod
    def parse_line(line):
        print(line)
        match = TailF.regex.match(line)
        if match is not None:
            action_time = match.groups()[0]
            # platform = match.groups()[1]
            # name = match.groups()[2]
            state = match.groups()[3]
            action_time = datetime.strptime(action_time, '%m/%d/%Y, %I:%M:%S %p')
            state = True if state == 'On' else False
            return action_time, state
        return None

    def __consume(self):
        # noinspection PyBroadException
        try:
            while True:
                self.pygtail.next()
        except Exception:
            pass

    def read(self):
        self.__consume()  # Just throwing away all logs until this moment.
        while True:
            try:
                line = self.pygtail.next()
                print(line)
                self.update_observers(line)
            except (StopIteration, PermissionError):
                time.sleep(0.5)


if __name__ == '__main__':
    hb = HomeBridge()
    hb.map_accessories()
    TailF.Instance().read()
