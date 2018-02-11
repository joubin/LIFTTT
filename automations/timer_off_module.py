from automations import automation_module
import re, time
from Util import logger
from main import TailF


class AutoOff(automation_module.Runner):

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
        logger.info("Created Action Listener AutoOff")

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
        logger.debug("payload %s", payload)
        if self.is_trigger(payload, "On"):
            self.run_action()
        elif self.is_trigger(payload, "Off"):
            self.void_action()
        else:
            logger.debug("Doing nothing")

    def is_trigger(self, line, state: str = "On"):
        logger.debug("Checking Trigger: %s", line)
        match = self.on_off_regex.match(line)
        logger.debug("Checking matching in is_trigger: %s", match)
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
        from homebridge import HomeBridge

        logger.info("%s Queued Action %s", self.__class__, self.time)
        try:
            self.wait(self.time)
            HomeBridge.Instance().request("PUT", self.aid, self.iid, False)
        except InterruptedError:
            pass


automation_module.Runner.register_with_homebridge("auto_off", AutoOff)
