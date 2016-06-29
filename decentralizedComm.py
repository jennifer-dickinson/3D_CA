import threading
import standardFuncs
import logging
import time

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates. When joined by communicate, run send then restart.
class synchronizer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, )
        # pass the class object through the plane generator to modify these values
        self.totalUAVs = 0
        self.uavCounter = 0
        self.readCounter = 0
        self.uavsInAir = 0
        self.synched = threading.Condition()
        self.receive = threading.Condition()
        self.sendLoc = threading.Lock()
        self.lastupdate = None

        self.ready = threading.Condition()

        self.msg = None

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated.")
        time.sleep(1)
        self.lastupdate = time.time()
        while self.uavsInAir > 0:
            if time.time() - self.lastupdate > 2:
                logging.info("Communication timed out.")
                print ("Communication timed out. No updates received.")
                break
            if self.readCounter == self.uavCounter == self.uavsInAir:
            # Will need to modify this. May cause errors with the way it is set up.
                self.synched.notifyAll()
                self.readCounter = 0
                self.uavCounter = 0
        if self.uavsInAir == 0:
            print ("All UAVs have either crashed or finished waypoints")
        logging.info("Global communicator terminated.")


# In planeGenerator, each plane object will start its own communication thread to update and receive telemetry.
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer):
        threading.Thread.__init__(self)
        self.sync = synchronizer
        self.get = synchronizer.receive
        self.plane = plane
        self.setDaemon(True)
        self.start()

    # Currently this is not starting. Why?
    def run(self):
        print ("Communicator started for UAV #%3i" % self.plane.id)
        logging.info("Communicator started for UAV #%3i" % self.plane.id)

        # i = 0
        # while i < 10:
        #     print ("Communicator thread working for UAV #%3i" % self.plane.id)
        #     i += 1

        while not self.plane.dead:
            #self.get.wait()
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
        logging.info("Communicator terminated for UAV #%3i." % self.plane.id)



    def update(self):
        self.sync.acquire()
        logging.info("UAV #%3i updating telemetry.")
        print ("updating telemetry")

        if not self.plane.dead:
            # Send information to all threads
            self.sync.msg = {"ID": self.plane.id, "loc": self.plane.cLoc}
            # Figure out a datastructure first
        elif self.plane.dead:
            self.sync.uavCounter -= 1

        ### Notify all threads of information
        self.sync.receive.notifyAll()  # let all receivers know there is a message
        self.sync.sendLock.release()  # release lock for next uav thread
        self.sync.synched.wait()  # wait to synch with all other UAVs
