import logging
import time
from tailf import TailF
from Util import Configuration, logger
from homebridge import HomeBridge


SERVER = Configuration.Instance().config["DEFAULT"]["server"]
PORT = Configuration.Instance().config["DEFAULT"]["port"]
PIN_CODE = Configuration.Instance().config["DEFAULT"]["auth_code"]

logging.info("Starting time %s", time.time())
logger.info("Server %s", SERVER)
logger.info("Port %s", PORT)




def loaders():
    from automations.timer_off_module import AutoOff
    hb: HomeBridge = HomeBridge.Instance()
    hb.register_module(clazz=AutoOff, identifier="auto_off")


if __name__ == '__main__':
    logReader : TailF = TailF.Instance()
    loaders()
    HomeBridge.Instance().map_accessories()
    logReader.read()
