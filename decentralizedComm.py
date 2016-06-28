import threading
import standardFuncs
import logging

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates. When joined by
# receive, run send then restart.
class synchronizer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, )
        # pass the class object through the plane generoator to modify these values
        self.totalUAVs = 0
        self.uavCounter = 0
        self.readCounter = 0
        self.uavsInAir = 0
        self.synched = threading.Condition()
        self.receive = threading.Condition()
        self.sendLoc = threading.Lock()

        self.msg = None

    def run(self):
        while self.uavsInAir > 0:
            if self.readCounter == self.uavCounter == self.uavsInAir:
                self.synched.notifyAll()
                self.readCounter, self.uavCounter = 0


# Have each UAV Run its own thread
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer, messenger):
        threading.Thread.__init__(self)
        self.daemon()
        self.sync = synchronizer
        self.get = synchronizer.receive()
        self.plane = plane

        self.start()

    def run(self):
        while not self.plane.dead:
            self.get.wait()
            message = self.sync.msg
            if message == None or message["ID"] == self.plane.id:
                pass
            else:
                for i in self.plane.map:
                    if self.plane.map[i]["ID"] == message["ID"]:
                        self.plane.map[i] = message
                        exists = True
                    else: exists = False
                    if not exists:
                        self.plane.map.append(message)


    def update(self, plane):
        self.sync.acquire()
        logging.info("UAV #%3i sy")

        if not plane.dead:
            # Send information to all threads
            self.sync.msg = {"ID": plane.id, "loc": plane.cLoc}
            # Figure out a datastructure first
        elif plane.dead:
            self.sync.uavCounter -= 1

        ### Notify all threads of information
        self.sync.receive.notifyAll()  # let all receivers know there is a message
        self.sync.sendLock.release()  # release lock for next uav thread
        self.sync.synched.wait()  # wait to synch with all other UAVs

synchronizer.start()