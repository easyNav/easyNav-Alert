import threading
import json
import smokesignal
import Queue

from easyNav_pi_dispatcher import DispatcherClient

class Alert(object):
    """ This is the Nav class, which handles navigation on the Raspberry Pi. 
    It retrieves remote location information and navigates to the point.  In addition,
    this class implements the REST API endpoints from the server. 
    """
    HOST_ADDR = "http://localhost:1337"
    THRESHOLD_DIST = 50
    THRESHOLD_ANGLE = 5 * 0.0174532925

    ## Run Levels here
    RUNLVL_NORMAL = 0
    RUNLVL_WARNING_OBSTACLE = 1

    def __init__(self):
        
        ## For interprocess comms 
        self.DISPATCHER_PORT = 9004
        self._dispatcherClient = DispatcherClient(port=self.DISPATCHER_PORT)

        ## Attach event listeners upon instantiation (to prevent duplicates)
        self.attachEvents()        
    
    def start(self):
        """ Start the daemon and run persistently.  Auto-retrieves new map in starting. 
        """
        ## Start inter-process comms
        self._dispatcherClient.start()      

    def attachEvents(self):
        """Configure event callbacks to attach to daemon on start.

        All events must be a series of event functions.
        
        1:345 2:60
        Do not call this externally!
        """
        ## clear all signals
        smokesignal.clear()

        @smokesignal.on('sonarData')
        def sonardata(args):
            leftvalue=eval(args.get('1'))
            rightvalue=eval(args.get('2'))
            leftvalue=int(leftvalue)
            rightvalue=int(rightvalue)
            threhold=70
            if((leftvalue <= theshold) and (rightvalue <= threshold)):
                #self._dispatcherClient.send(9001, 'obstacle', {'text': 'Stop'})
                self._dispatcherClient.send(9002, 'say', {'text': 'Stop'})
            if((leftvalue <= theshold) and (rightvalue >= threshold)):
                #self._dispatcherClient.send(9001, 'obstacle', {'text': 'Keep Right'})
                self._dispatcherClient.send(9002, 'say', {'text': 'Stop'})
            
            if((leftvalue >= theshold) and (rightvalue <= threshold)):
                #self._dispatcherClient.send(9001, 'obstacle', {'text': 'Keep Left'})
                self._dispatcherClient.send(9002, 'say', {'text': 'Stop'})
                    
def runMain():
    """ Main function called when run as standalone daemon
    """
    alert = Alert()
    alert.start()


if __name__ == '__main__':
    runMain()