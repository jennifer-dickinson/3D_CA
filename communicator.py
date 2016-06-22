import threading
import time
import defaultValues

from collections import deque, namedtuple

info = namedtuple('info', 'id latitude longitude altitude')

class uavComm(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.q = deque('',defaultValues.MAX_QUEUE_SIZE)
        stop = False

    def run(self):
        timer = 0
        while True:
            if defaultValues.SIMULATE_TIME:
                time.sleep(defaultValues.DELAY)
                timer += defaultValues.DELAY


            if self.stop:
                print "Communication has ended."
                break

    def update(self, plane):
        # this function is called from outside
        data = info(plane.id, plane.cLoc.latitude, plane.cLoc.longitude, plane.cLoc.altitude)
        self.q.append(data)

        #add option to add to file

    # Copies the current queue and returns as a list
    def read (self):
        my_list = list()
        for obj in self.q:
            my_list.append(obj)
        while True:
            try:
                print self.q.pop()
            except:
                print "Que has ended"
                break

    # Ends the thread
    def stop (self):
        #try:
        #    while True:
        #        print self.q.pop()
        #except:
        #    print "End of Queue"
        self.read()
        self.stop = True