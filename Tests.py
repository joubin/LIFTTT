import unittest
from Util import Configuration
import re
class Tests(unittest.TestCase):
    def test(self):
        test1 = "[2/10/2018, 2:25:11 PM] [WeMo Platform] Wemo Mini - Set state: On"
        test2 = "[2/10/2018, 2:25:08 PM] [WeMo Platform] Wemo Mini - Set state: Off"
        regex = Configuration.Instance().config["Wemo Mini"]["on_off_regex"]
        print(regex)
        regex_compile = re.compile(r""+regex, re.IGNORECASE)
        match1 = regex_compile.match(test1)
        self.assertIsNotNone(match1)

if __name__ == '__main__':
    unittest.main()