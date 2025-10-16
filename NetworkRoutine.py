import socket
import time
import threading
from DataExchange import Data

class Network_Routine(threading.Thread):
    def __init__(self):
        super(Network_Routine,self).__init__()
        self.data = Data()
    
    def run(self):
        global temp, pres, humi
        s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", 4081))
        while True:
            try:
                s.settimeout(15)                      
                daten, addr = s.recvfrom(1024)
                #print("[{}] {}".format(addr[0], daten.decode()))
                trigger = daten.decode()
                timestamp = time.strftime("%H:%M:%S")
                data = self.data.get_data()
                if data is None:
                    temp = 0.0
                    pres = 0.0
                    humi = 0.0
                else:
                    temp, pres, humi = data

                string = f"[{timestamp}] [{temp:.2f}C] [{pres:.2f}hPa] [{humi:.2f}%]"
                if trigger == "trigger":
                    s.sendto(string.encode("ascii"),("192.168.178.45", 4080))
                elif trigger =="desktop":
                    s.sendto(string.encode("ascii"),("192.168.178.117", 4080))
                elif trigger == "clock":
                    # network without sleep sometimes too fast for clockpi to open port for listening in time
                    time.sleep(0.2)
                    s.sendto(string.encode("ascii"),("192.168.178.100", 4080))
                elif trigger == "mini":
                    s.sendto(string.encode("ascii"),("192.168.178.128", 4080))
            except socket.timeout:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] Timeout bei Anfrage")
                continue
