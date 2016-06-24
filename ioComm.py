import threading

# Make a single thread object to listen for telemetry updates. When joined by
# receive, run send then restart.
class listen(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run():
        pass

# Have each UAV
class receive(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run():
        pass

class send(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run():
        pass
