#!/usr/bin/python3
from DisplayRoutine import Display_Routine
from NetworkRoutine import Network_Routine
from LedStripRoutine import Strip_Routine
from time import sleep


if __name__ == "__main__":

    DR = Display_Routine()
    NR = Network_Routine()
    DR.start()
    NR.start()
    sleep(5) 
    SR = Strip_Routine() 
    SR.start()

