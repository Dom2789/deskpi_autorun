#!/usr/bin/python3
from DisplayRoutine import Display_Routine
from NetworkRoutine import Network_Routine
from LedStripRoutine import Strip_Routine
from time import sleep
import logging

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        filename='/home/pi/prog/autorun/error_log.txt',  # Log file name
        level=logging.ERROR,       # Log level
        format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
    )
    try:
        DR = Display_Routine()
        NR = Network_Routine()
        DR.start()
        NR.start()
        sleep(10)

        try:
            SR = Strip_Routine() 
        except Exception as e:
            logging.error("Error instantiate Strip_Routine: %s", str(e), exc_info=True)

        try:
            SR.start()
        except Exception as e:
            logging.error("Error starting thread for Strip_Routine: %s", str(e), exc_info=True)    

    except KeyboardInterrupt as k:
            logging.error("Terminated via keyboard interrupt: %s", str(k))


