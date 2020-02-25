import queue
import threading
import time

# Hebra trabajadora
class ThreadedTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        time.sleep(10)  # Simulate long running process
        self.queue.put("Tarea parada")
