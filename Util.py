import configparser
from abc import ABCMeta, abstractmethod
import logging

from multiprocessing import Queue


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


class Observable(object):
    def __init__(self):
        self.observers = Queue()

    def register(self, observer):
        tmp = []
        while self.observers.qsize() > 0:
            tmp.append(self.observers.get())
        tmp.append(observer)
        tmp = list(set(tmp))
        for i in tmp:
            self.observers.put(i)


    def unregister(self, observer):
            # this is bad, fix later
            tmp = []
            while self.observers.qsize() > 0:
                tmp.append(self.observers.get())
            tmp.remove(observer)
            for i in tmp:
                self.observers.put(i)


    def unregister_all(self):
        if self.observers:
            while self.observers.qsize() > 0:
                self.observers.get()

    def update_observers(self, payload):

            # this is bad, fix later
        tmp = []
        while self.observers.qsize() > 0:
            tmp.append(self.observers.get())
        for i in tmp:
            i.update(payload)
            self.observers.put(i)


class Observer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, payload):
        pass


@Singleton
class Configuration():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')


logging.basicConfig(level=Configuration.Instance().config["DEFAULT"]["logging_level"])
logger = logging.getLogger(__name__)


