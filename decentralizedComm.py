import logging
import threading
import time

import standardFuncs
import defaultValues

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates.
class synchronizer(threading.Thread):
    def __init__(self, numPlanes):
        threading.Thread.__init__(self, name="Global Communicator")
        # pass the class object through the plane generator to modify these values
        self.uavsInAir = numPlanes
        self.deathCount = 0

        self.msg = {"ID": 0, "Location": ""}

        self.startTime = time.time()

        self.lastUpdate = time.time()

        # For reading the message
        self.readCounter = 0
        self.readLock = threading.RLock()
        self.broadcast = threading.Event()
        self.readTurn = threading.Event()
        self.broadcast.clear()
        self.readTurn.clear()
        self.msgRcd = threading.Event()

        # For writing the message
        self.broadcastCounter = 0
        self.msgLock = threading.RLock()
        self.broadcastWrite = threading.Event()
        self.turn = threading.Event()
        self.broadcastWrite.set()
        self.turn.clear()

        self.start()

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated: %s" % self)
        startTime = self.lastUpdate
        try:
            while self.uavsInAir != 0:

                # Break if no updates within 4 seconds or no UAVs in air

                # if self.broadcast.isSet() and self.readTurn.isSet():
                #     self.readTurn.clear()
                if self.readCounter >= self.uavsInAir:
                    self.readCounter = 0
                    self.msgRcd.set()
                    #logging.info("----------All UAVs received message from #%3i" % self.msg["ID"])
                    self.broadcastWrite.set()
                    #self.broadcast.clear()
                    self.readTurn.set()

                if (time.time() - self.lastUpdate > defaultValues.COMM_KILL_TIME):
                    logging.info("Communication timed out.")
                    print "Communication timed out."
                    break

        except KeyboardInterrupt:
            logging.info("Program interrupted by user.")
        time.sleep(.1)
        if self.uavsInAir == 0: print "NO UAVS AIR."
        else:
            print "UAVs in air: %i" % self.uavsInAir
            print 'Read counter: %i' % self.readCounter
            print 'Read turn event: %s' % self.readTurn.isSet()
            print 'Broadcast Event: %s' %   self.broadcast.isSet()


            print 'Broadcast counter: %i' % self.broadcastCounter
            print 'Broadcast write event: %s' % self.broadcastWrite.isSet()
            print 'Broadcast turn event: %s' % self.turn.isSet()
        logging.info("Time elapsed: %.2fs" % (self.lastUpdate - startTime))


# In planeGenerator, each plane object will start its own communication thread to update and receive telemetry.
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer):
        self.plane = plane
        self.synch = synchronizer

        threading.Thread.__init__(self, name="UAV #%i Comm" % self.plane.id)
        self.setDaemon(True)
        self.start()
        self.msgCounter = 0

    def run(self):
        while True:
            # Wait for a broadcast from UAV
            logging.info("Com #%3i waiting for next broadcast." % self.plane.id)
            self.synch.broadcast.wait()

            #logging.info("Com #%3i waiting for readLock" % self.plane.id)
            self.synch.readLock.acquire()
            #logging.info("Com #%3i acquired readLock" % self.plane.id)
            # Read the message
            logging.info("Com #%3i received message #%i from UAV # %i" % (
                self.plane.id, self.synch.msg["#"], self.synch.msg["ID"]))
            # Increment counter for new read turn

            self.synch.readCounter += 1

            #logging.info("Com #%3i released readLock" % self.plane.id)

            self.synch.readLock.release()
            logging.info("Com #%3i waiting for next read turn." % self.plane.id)
            self.synch.readTurn.wait()
            if self.plane.dead or self.plane.wpAchieved >= self.plane.numWayPoints:
                break

    def update(self):
        # Wait for it to be ok to broadcast
        self.synch.msgLock.acquire()
        self.synch.broadcastWrite.wait()
        self.synch.lastUpdate = time.time()



        # Send Message
        if self.plane.dead or self.plane.wpAchieved == self.plane.numWayPoints:
            self.synch.uavsInAir -= 1
            logging.info("UAV #%3i crashed or reached all waypoints." % self.plane.id)
        else:
            self.synch.broadcastCounter += 1
            self.msgCounter += 1
            self.synch.msg = {"ID": self.plane.id, "Location": self.plane.cLoc, "#": self.msgCounter}



        logging.info("UAV #%3i broadcasting message." % self.plane.id)

        # Alert UAV Comms of message
        self.synch.broadcast.set()

        logging.info("Waiting for all Comms to receive message.")
        self.synch.msgRcd.wait()
        self.synch.msgRcd.clear()
        self.synch.broadcast.clear()
        logging.info("UAV #%3i confirmed UAV Comms received message" % self.plane.id)



        logging.info("**********UAV #%3i end of broadcast turn." % self.plane.id)

        if self.synch.broadcastCounter == self.synch.uavsInAir:
            self.synch.broadcastCounter = 0
            logging.info("##########All UAVs wrote a message")
            self.synch.turn.set()
        else:
            self.synch.turn.clear()

        self.synch.msgLock.release()
        self.synch.turn.wait()
