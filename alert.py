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
        self.flag=0
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
	    
	   # print args  
	    payload =eval(args.get("payload"))
           # print payload
	    leftvalue= payload["1"]
            rightvalue=payload["2"]
	    #print leftvalue

            leftvalue=int(leftvalue.rstrip('\u0'))
            rightvalue=int(rightvalue.rstrip('\u0'))
            threshold=70
            if((leftvalue <= threshold) and (rightvalue <= threshold)):
                #self._dispatcherClient.send(9001, 'obstacle', {'text': 'Stop'})
                self._dispatcherClient.send(9002, 'say', {'text': 'Stop'})
		self.flag=1;
            if((leftvalue <= threshold) and (rightvalue >= threshold)):
                #self._dispatcherClient.send(9001, 'obstacle', {'text': 'Keep Right'})
                self._dispatcherClient.send(9002, 'say', {'text': 'keep right'})
                self.flag=1;
            if((leftvalue >= threshold) and (rightvalue <= threshold)):
                #self._dispatcherClient.send(9001, 'obstacle', {'text': 'Keep Left'})
                self._dispatcherClient.send(9002, 'say', {'text': 'keep left'})
		self.flag=1
            if((leftvalue >=threshold) and (rightvalue>=threshold) and self.flag ==1):
		self._dispatcherClient.send(9002, 'say', {'text': 'proceed'})
		self.flag=0;        
def runMain():
    """ Main function called when run as standalone daemon
    """
    alert = Alert()
    alert.start()


if __name__ == '__main__':
    runMain()
