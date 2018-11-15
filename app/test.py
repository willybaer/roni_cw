from scrap_wrapper import ScrapWarpper
import time
class Test(ScrapWarpper):
    def test(self):
        pass

    def main(self):
        while 1 < 10:
            print('Hello')
            time.sleep(1)

t = Test()

