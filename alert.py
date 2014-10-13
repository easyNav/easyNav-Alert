import threading
import json
import smokesignal
import Queue
import datetime

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
        self.sendflag=1
		self.state=1    #1-proceed #2-stop #3 step right #4 step left 
		self.sendAlertInterval = datetime.datetime(seconds=5)
		self.triggerAlertime=datetime.datetime(seconds=0)
		
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
	    threshold=70     
		
		if(currentsoundtime-triggersoundtime>self.sendAlertInterval):
		   sendflag=1;
		else 
		   sendflag=0;
					
		#1-proceed #2-stop #3 step right #4 step left 
		if (self.state ==1): # proceed state
		  
		  payload =eval(args.get("payload"))
          leftvalue= payload["1"]
          rightvalue=payload["2"]
	      leftvalue=int(leftvalue.rstrip('\u0'))
          rightvalue=int(rightvalue.rstrip('\u0'))	 
		  
		  if((leftvalue <= threshold) OR(rightvalue <= threshold)):
			  self.state=2 #stop state
			  currentsoundtime=datetime.datetime.now().time()
					
              if(sendflag==1):
				self._dispatcherClient.send(9002, 'say', {'text': 'stop'})
				triggersoundtime=datetime.datetime.now().time() # when it sends
			    
		  else
			   self.state=1 # proceed state
				
			
			
	    else if (self.state ==2): #stop state	 
		  if((leftvalue <= threshold) AND(rightvalue >= threshold)):
			  self.state=3 #go to step right state
			  currentsoundtime=datetime.datetime.now().time()
			  
			  if(sendflag==1):
				self._dispatcherClient.send(9002, 'say', {'text': 'keep right'})
				triggersoundtime=datetime.datetime.now().time() # when it sends
		  
		  else if((leftvalue >= threshold) AND(rightvalue <= threshold)):
			  self.state=4 #go to step left state
			  currentsoundtime=datetime.datetime.now().time()
			  
			  if(sendflag==1):
				self._dispatcherClient.send(9002, 'say', {'text': 'keep left'})
				triggersoundtime=datetime.datetime.now().time() # when it sends
		  
		  else
			  self.state =2 #go to proceed state
			  if(sendflag==1):
				self._dispatcherClient.send(9002, 'say', {'text': 'proceed'})
				triggersoundtime=datetime.datetime.now().time() # when it sends
		
		else if (self.state ==3):#keep right 
			  payload =eval(args.get("payload"))
			  leftvalue= payload["1"]
              rightvalue=payload["2"]
	          leftvalue=int(leftvalue.rstrip('\u0'))
              rightvalue=int(rightvalue.rstrip('\u0'))	 
			  
			  if((leftvalue >= threshold) OR(rightvalue >= threshold)):
			    self.state=1; #go to proceed state
				currentsoundtime=datetime.datetime.now().time()
				
				if(sendflag==1):
				  self._dispatcherClient.send(9002, 'say', {'text': 'proceed'})
				  triggersoundtime=datetime.datetime.now().time() # when it sends
				
		      else 
				self.state=2; #go to stop state
				if(sendflag==1):
				self._dispatcherClient.send(9002, 'say', {'text': 'proceed'})
				triggersoundtime=datetime.datetime.now().time() # when it sends
		  			
		else if (self.state == 4):#keep left state
				
			  payload =eval(args.get("payload"))
			  leftvalue= payload["1"]
              rightvalue=payload["2"]
	          leftvalue=int(leftvalue.rstrip('\u0'))
              rightvalue=int(rightvalue.rstrip('\u0'))	 
			  
			  if((leftvalue >= threshold) OR(rightvalue >= threshold)):
			    self.state=1; #go to proceed state
				currentsoundtime=datetime.datetime.now().time()
				
                if(sendflag==1):
				   self._dispatcherClient.send(9002, 'say', {'text': 'proceed'})
				   triggersoundtime=datetime.datetime.now().time() # when it sends
				
		      else 
				self.state=2;  #go to stop state      
				if(sendflag==1):
				 self._dispatcherClient.send(9002, 'say', {'text': 'proceed'})
				 triggersoundtime=datetime.datetime.now().time() # when it sends				
					
                 
def runMain():
    """ Main function called when run as standalone daemon
    """
    alert = Alert()
    alert.start()


if __name__ == '__main__':
    runMain()
