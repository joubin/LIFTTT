import time
from Util import Configuration, Singleton, Observable, logger
from pygtail import Pygtail
from datetime import datetime
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
                logger.debug("Notifying %s observers", self.observers.qsize())
                self.update_observers(line)
            except (StopIteration, PermissionError):
                time.sleep(0.5)
