import threading

# Hebra trabajadora
class ExporterTask(threading.Thread):
    def __init__(self, filename, data):
        threading.Thread.__init__(self)
        self.filename = filename
        self.data = data

    def run(self):
        fout = open(self.filename, 'w')
        for l in self.data:
            fout.write(str(l)+"\n")
        fout.close()
