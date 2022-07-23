import time
import datetime
'''
쓰는법

'''
class TIMER:
    def __init__(self) -> None:
        self.StartTime = datetime.datetime.now()
        self.time = 0
        # datetime.datetime.now()-self.StartTime

    def start(self):
        self.StartTime = datetime.datetime.now()

    def stop(self,print_result=True,name='timer'):
        self.time = datetime.datetime.now() - self.StartTime
        if print_result:
            print(name,':',self.time)
        
        return self.time

def timeNow():
    return datetime.datetime.now()

if __name__ == "__main__":
    t = datetime.datetime.now()

    print(t)
    t2 = t+datetime.timedelta(minutes=3)
    print(t2)
    print(t>t2)