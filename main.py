import logging
import time
from datetime import datetime

from pygtail import Pygtail

from Util import Observable, Singleton, Configuration, logger
from homebridge import HomeBridge

SERVER = Configuration.Instance().config["DEFAULT"]["server"]
PORT = Configuration.Instance().config["DEFAULT"]["port"]
PIN_CODE = Configuration.Instance().config["DEFAULT"]["auth_code"]

logging.info("Starting time %s", time.time())
logger.info("Server %s", SERVER)
logger.info("Port %s", PORT)


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
                logger.debug("TailF read line: %s", line)
                logger.debug("Notifying %s observers", len(self.observers))
                self.update_observers(line)
            except (StopIteration, PermissionError):
                time.sleep(0.5)

def loaders():
    from automations.timer_off_module import AutoOff
    hb : HomeBridge = HomeBridge.Instance()
    hb.register_module(clazz=AutoOff, identifier="auto_off")

if __name__ == '__main__':

    loaders()
    HomeBridge.Instance().map_accessories()
    TailF.Instance().read()
