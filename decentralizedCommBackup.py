import threading
import standardFuncs
import logging
import time

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates. When joined by communicate, run send then restart.
class synchronizer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name = "Global Communicator")
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
        self.start()

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated: %s" % self)
        time.sleep(1)
        self.lastupdate = time.time()
        while self.uavsInAir > 0:
            if time.time() - self.lastupdate > 4:
                logging.info("Communication timed out.")
                print ("Communication timed out. No updates received.")
                break
            if self.readCounter  == self.uavsInAir:
                # Will need to modify this. May cause errors with the way it is set up.
                self.synched.notifyAll()
                self.readCounter = 0
                self.uavCounter = 0

        if self.uavsInAir == 0:
            print ("All UAVs have either crashed or finished waypoints")


# In planeGenerator, each plane object will start its own communication thread to update and receive telemetry.
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer):
        self.plane = plane
        self.sync = synchronizer
        self.get = synchronizer.receive

        threading.Thread.__init__(self, name = "UAV #%i Comm" % self.plane.id)
        self.setDaemon(True)
        self.start()

    def run(self):
        # print ("Communicator started for UAV #%3i" % self.plane.id)
        logging.info("UAV #%3i communicator started: %s" % (self.plane.id, self))

        while not self.plane.dead:
            try:
                self.get.acquire()
                logging.info("Waiting for an update: %s"  % self)
                self.get.wait()

            except:
                logging.info("Could not wait for synchronizer.")
                break
            message = self.sync.msg
            if message == None or message["ID"] == self.plane.id:
                pass
            else:
                for i in self.plane.map:
                    if self.plane.map[i]["ID"] == message["ID"]:
                        self.plane.map[i] = message
                        logging.info ("UAV #3i added updated threat on map")
                        exists = True
                    else:
                        exists = False
                    if not exists:
                        self.plane.map.append(message)
                        logging.info ("UAV #3i added threat to map")


        logging.info("Communicator terminated for UAV #%3i: %s" % (self.plane.id, self))

    def update(self):
        self.sync.synched.acquire()
        logging.info("UAV #%3i updating telemetry." % self.plane.id)

        if not self.plane.dead:
            # Send information to all threads
            self.sync.msg = {"ID": self.plane.id, "loc": self.plane.cLoc}
            # Figure out a datastructure first
        elif self.plane.dead:
            self.sync.uavCounter -= 1
        logging.info ("%s updated telemetry " % self)
        ### Notify all threads of information
        self.get.notifyAll()  # let all receivers know there is a message
        self.sync.sendLock.release()  # release lock for next uav thread
        self.sync.synched.wait()  # wait to sync with all other UAVs

