from threading import Thread, Event
from time import sleep

class inComm(Thread):
    # This receives an output signal and should post message.
    def __init__(self):
        Thread.__init__(self)
        self.start()
        self.is_stopped = False
        self.signal = Event()

    def run(self):
        print "Receiver listener started."
        while not self.is_stopped:
            print "Listening...."
            self.signal.wait()
            print "Worked."


            self.signal.clear()


Receiver = inComm()
sleep(5)
Receiver.signal.set()
sleep(2)
Receiver.is_stopped = True
sleep(2)
if Receiver.isAlive: print "Receiver listener is still running, but not listening."
else: print "Receiver shut down"
