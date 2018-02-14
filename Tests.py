test_arr = {}
from Util import *
@Singleton
class TOB(Observable):


    def dosomething(self):
        self.update_observers("test")




class TO(Observer):
    def update(self, payload):
        print(payload)

    def __init__(self, ):
        self.name = "observer"
        TOB.Instance().register(self)




observer1 = TO()
observer2 = TO()
observer3 = TO()
observer4 = TO()
observer5 = TO()
TOB.Instance().dosomething()