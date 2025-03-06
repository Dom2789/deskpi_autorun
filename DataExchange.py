import threading

class Data:
    _instance = None
    _lock = threading.Lock()  # Lock für Thread-Sicherheit

    def __new__(cls):
        with cls._lock:  # Verhindert parallelen Zugriff in Multithreading-Umgebungen
            if cls._instance is None:
                cls._instance = super(Data, cls).__new__(cls)
                cls._instance.data = None  # Gemeinsame Datenvariable
        return cls._instance

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data