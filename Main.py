import configparser
import json
import threading
from abc import abstractmethod
from pygtail import Pygtail
import re, sys, time
from datetime import datetime
import requests

SERVER = "pi"
PORT = "33425"
PIN_CODE = "335-28-246"

RUNNERS = []

class Configuration():
    config = configparser.ConfigParser()
    config.read('config.cfg')


class Runner:
    def __init__(self, name, config):
        self.name = name
        self.command = config

    def run(self):
        thread = threading.Thread(target=self.main)
        thread.start()

    def is_trigger(self, line):
        match = TailF.regex.match(line)
        return match.groups()[2] == self.name


    @abstractmethod
    def main(self):
        raise NotImplementedError()

class Auto_Off(Runner):
    auto_off_regex = re.compile("(\d*).*(\w)", re.IGNORECASE)
    def __init__(self, name, config, aid, iid):
        super().__init__(name, config)
        self.time = self.parse_auto_off(config['auto_off'])
        self.aid = aid
        self.iid = iid

    def parse_auto_off(self, str, default_duration=1):
        match = Auto_Off.auto_off_regex.match(str)
        if match is not None:
            duration = float(match.groups()[0])
            multiplier = match.groups()[1]
            if multiplier == "m":
                multiplier = 60
            elif multiplier == "h":
                multiplier = 60*60
            else:
                multiplier = 1
            return duration*multiplier
        return default_duration

    def main(self):
        print("running logic and waiting", self.time)
        time.sleep(self.time)
        HomeBridge.request("PUT", self.aid, self.iid, False)


class HomeBridge():
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
            on = None
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
                        if name['value'] in Configuration.config.sections():
                            if Configuration.config[name['value']]['type'] == "auto_off":
                                RUNNERS.append(Auto_Off(name=name['value'], config=Configuration.config[name['value']],aid=aid, iid=on['iid']))







class TailF:
    log = "/var/log/homebridge.log"
    regex = re.compile("\[(.*)\] \[(.*)\] (.*)\ - Set state: (Off|On)",
                       re.IGNORECASE)

    def __init__(self, file_path=log):
        self.log_file_path = file_path
        self.pygtail = Pygtail(self.log_file_path)

    @staticmethod
    def parse_line(line):
        print(line)
        match = TailF.regex.match(line)
        if match is not None:
            time = match.groups()[0]
            platform = match.groups()[1]
            name = match.groups()[2]
            state = match.groups()[3]
            time = datetime.strptime(time, '%m/%d/%Y, %I:%M:%S %p')
            state = True if state == 'On' else False
            return time, state
        return None

    def __consume(self):
        try:
            while True:
                self.pygtail.next()
        except Exception:
            pass

    def read(self):
        self.__consume() # Just throwing away all logs until this moment.
        while True:
            try:
                line = self.pygtail.next()
                print(line)
                triggered = [runner for runner in RUNNERS if runner.is_trigger(line)]
                [runner.run() for runner in triggered]
            except (StopIteration, PermissionError):
                time.sleep(0.5)

if __name__ == '__main__':
    hb = HomeBridge()
    hb.map_accessories()
    log = TailF()
    log.read()