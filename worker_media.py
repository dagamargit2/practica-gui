import queue
import threading
import time
from medicion import Medicion

# Hebra trabajadora
class ThreadedTask(threading.Thread):
    def __init__(self, queue, lmediciones):
        threading.Thread.__init__(self)
        self.queue = queue
        self.lmediciones = lmediciones

    def run(self):
        try:
            tot = 0.0
            for m in self.lmediciones:
                tot += m.get_valor()

            res = tot / len(self.lmediciones)
            self.queue.put(str(res))
        except:
            self.queue.put("Error")

