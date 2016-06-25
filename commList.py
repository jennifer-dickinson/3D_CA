from threading import Thread, Event, RLock
import time
from defaultValues import *
from standardFuncs import *

class uavComm(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.positions = list()
        self.stopped = False

        self.timer = 0
        self.counter = 0
        self.total_uavs = 0     # Total number of UAVs in the air
        self.steps_counter = 0

        self.writeState = Event()
        self.readState = Event()

        self.lock = RLock()
        self.lock2 = RLock()
        try:
            self.readState.set()
        except:
            print "Read state not set"
        if self.readState.isSet(): print "Read state set!"

    def run(self):
        while not self.stopped:
            time.sleep(1)

            # Increment timer with each loop. If no updates after threshold, break.
            self.timer += 1

            # If no UAVs in air, end communicator thread.
            if self.total_uavs == 0:
                print "\nNO UAVS IN AIR"
                self.readmessage = ""
                self.writemessage = ""
                break

            # If timer reaches 4 seconds without an update, end communicator thread.
            elif self.timer > 5:
                print "Communication timed out"
                print "UAV counter set to %.f" % self.counter
                print "UAVs still in air: %.f" % self.total_uavs
                self.stopped = True
                break

            # If timer reaches 2 seconds without an update, check read and write states.
            elif  self.timer > 2:
                if self.writeState.isSet:
                    print "Write state set."
                    try:
                        self.lock.release()
                        print "Write lock released"
                    except:
                        print "Write lock not acquired."
                        # Switch to readState
                        self.writeState.clear()
                        self.readState.set()
                        print "Switched to readState"

                elif self.readState.isSet:
                    print "Read state set."
                    try:
                        self.lock2.release()
                        print "Read lock released."
                    except:
                        print "Read lock not acquired."
                        # Switch to writeState
                        self.readState.clear()
                        self.writeState.set()
                        print "Switched to writeState"



        print "\nCommunication has ended.\n"

        # Print status for each UAV.
        title = '\n%-4s %-40s %-10s %-10s %-10s %-10s ' % (
            'ID#',
            'Final Location',
            'Distance',
            'Waypoints',
            'Crashed?',
            'Killed By?'
        )
        print title
        line = ""
        for i in title:
            line += "_"
        print line
        for elem in self.positions:
            if elem["dead"]: killed = "UAV #%s" % elem["killedBy"]
            else: killed = ""
            location = "(%.7f%s, %.7f%s, %.1f m)" % (
                elem["cLoc"].latitude, DEGREE,
                elem["cLoc"].longitude, DEGREE,
                elem["cLoc"].altitude,
            )
            print '%3i  %-39s  %9s  %9s  %-9s  %-9s' % (
                elem["ID"],
                location,
                elem["tdis"],
                elem["wpts"],
                elem["dead"],
                killed
            )

        #print "\nTotal UAVS still flying: %.0f." % self.total_uavs
        print "\nTime taken: %.1f seconds." % (self.steps_counter * DELAY)
        print self.readmessage
        print self.writemessage

    def startUp (self, plane):
        dict = {"ID" : plane.id,
                "cLoc" : plane.cLoc,
                "bear": plane.cBearing,
                "elev": plane.cElevation,
                "dead" : plane.dead,
                "killedBy" : None,
                "wpts" : 0,
                "tdis" : 0
                }
        self.positions.append(dict)
        self.timer = 0
        self.total_uavs += 1
        print "Initial position for UAV", plane.id, "updated!"


    def update(self, plane):
        self.writeState.wait()
        self.lock.acquire()

        self.writemessage = "\nUAV #%.f accesed write lock." % plane.id

        # Update telemetry
        dict = (item for item in self.positions if item["ID"] == plane.id).next()
        dict["cLoc"] = plane.cLoc
        dict["bear"] = plane.cBearing
        dict["elev"] = plane.cElevation
        dict["tdis"] = plane.distanceTraveled

        # Update waypoints achieved
        if dict["wpts"] < plane.wpAchieved:
            dict["wpts"] = plane.wpAchieved
            # Display message if waypoint achieved
            print "UAV #%.0f achieved waypoint #%.0f." % (dict["ID"], dict["wpts"])

        # Update plane status & reduce number of UAVs in air
        if plane.dead and not dict["dead"]:
            dict["dead"] = plane.dead
            dict["killedBy"] = plane.killedBy
            self.total_uavs -= 1

            # Just in case the second plane thinks its still alive, do the same for it
            dict2 = (item for item in self.positions if item["ID"] == plane.killedBy).next()
            if  dict2["dead"] == False:
                dict2["dead"] = plane.dead
                dict2["killedBy"] = plane.id
                self.total_uavs -= 1

        self.writemessage += "\nUAV #%.f updated position" % plane.id

        # If this UAV reached all waypoints, change status to done & reduce UAVs in air.
        if plane.numWayPoints == plane.wpAchieved:
            self.total_uavs -= 1
            done = True
        else: done = False

        # Only increment counter for writeState if this UAV is alive and still has waypoints
        if not plane.dead and not done:
            self.counter += 1

        # If the counter is equal to or greater than total UAVs, switch to readState & reset counter
        if self.counter >= self.total_uavs:
            self.counter = 0
            self.steps_counter += 1
            self.writeState.clear()
            self.readState.set()

        # Reset timeout timer.
        self.timer = 0  # Reset timeout timer
        self.lock.release()
        self.writemessage = "\nUAV #%.f completed write." % plane.id
        return True

    def read(self, plane):

        self.readState.wait()
        self.lock2.acquire()

        # Get list of UAV positions.
        list = self.positions

        self.readmessage = "\nUAV #%.f accessed memory" % plane.id

        # Increment counter.
        self.counter += 1

        # Switch to writeState if counter is equal to or greater than UAVs in the air.
        if self.counter >= self.total_uavs:
            self.counter = 0
            self.readState.clear()
            self.writeState.set()

        self.lock2.release()

        self.readmessage = "\nUAV #%.f completed read." % plane.id

        return list


    # Ends the thread
    def stop(self):
        self.stopped = True
