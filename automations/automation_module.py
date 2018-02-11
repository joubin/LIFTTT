import threading
from Util import Observer, abstractmethod, logger
from homebridge import HomeBridge


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
        logger.debug("Stopping Action")
        if self.stop is False and self.thread is not None:
            self.stop = True
            self.thread.join()
            logger.debug("Action Stopped")


    @staticmethod
    def register_with_homebridge(identifier:str, clazz:object):
        HomeBridge.Instance().register_module(identifier=identifier, clazz=clazz)


    @abstractmethod
    def is_trigger(self, line):
        pass

    @abstractmethod
    def main(self):
        raise NotImplementedError()
