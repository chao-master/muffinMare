#!/usr/bin/python
import socket
import threading
import time

### Parsing exception ###
class ParsingError(Exception):
    def __init__(self, msg, at, issue):
        self.msg = msg
        self.at = at
        self.issue = issue
    def __str__(self):
        return self.msg + ":- "+self.at+":- "+self.issue
        
class ircConnection():
    ### Initilisation with host and port ###
    def __init__(self,host,port=6667):
        self.HOST=host 
        self.PORT=port
        self.s = None
        self.t = None
        self.sLock = threading.Lock()
        self.lFlag = threading.Event()
        self.DEBUG = False #DEBUG
    
    ### Function to parse incoming messages with ###
    def parse(self,msg):
        prefix = ['','',''] #Prefix format: Nick/Server,User,Host
        
        #Parser assume /r/n has allready been removed
        if msg[0] == ":": #Check if message contains prefix
            i = msg.find(" ")
            if i == -1: raise ParsingError(msg,"Prefix Parsing","No space character after prefix")
            _prefix = msg[1:i] #Checking for a server name works the same as checking for a nick
                               #when being lazy, (assuming server name is correctlly formed)
                               #as it will not contain '!' or '@'
            msg = msg[i+1:].lstrip(" ")
            i = _prefix.find("!")
            j = _prefix.find("@")
            if i != -1 and j != -1: prefix = [_prefix[:i],_prefix[i+1:j],_prefix[j+1:]]
            elif i != -1: prefix = [_prefix[:i],_prefix[i+1:],'']
            elif j != -1: prefix = [_prefix[:j],'',_prefix[j+1:]]
            else: prefix = [_prefix,'','']
        i = msg.find(" ")
        if i == -1: raise ParsingError(msg,"Command Parsing","No space character after command")
        _command = msg[:i]
        if _command[0] >= "0" and _command[0] <= "9": #Command is numerical response code (have fun now)
            if len(_command) != 3: raise ParsingError(msg,"Command Parsing","Numeric code not 3 digits")
            try: command = int(_command)
            except ValueError: raise ParsingError(msg,"Command Parsing","Numeric code is not numeric")
        else: #Command is alpha
            for l in _command:
                if (l<"A")|(("Z"<l) & (l<"a"))|("z"<l): raise ParsingError(msg,"Command Parsing","Alpha Command '{0}' contains non-alphas '{1}'".format(_command,l))
            command = _command.upper()
        msg = msg[i+1:].lstrip(" ")
        params = []
        while len(msg) != 0:
            if msg[0] == ":": #Paramater is a trailing
                params.append(msg[1:])
                break
            else: #Paramater is non-trailing
                i = msg.find(" ")
                if i == -1: #Last paramater
                    params.append(msg)
                    break
                else:
                    params.append(msg[:i])
                    msg = msg[i+1:]
        return prefix,command,params
        
    ### send wrapper with lock ###
    def send(self,m):
        self.sLock.acquire()
        self.s.send(m)
        self.sLock.release()
    
    ### start connection and listening ###
    def start(self):
        self.s=socket.socket( ) #Create the socket 
        self.s.connect((self.HOST, self.PORT)) #Connect to server 
        self.t = threading.Thread(target=self.listen,args=[self])
        self.t.start()
    
    ### close connection, including sending QUIT message ###
    def close(self,qMsg = "Closing..."):
        print "closing connections waiting for threads to close"
        self.lFlag.set()
        self.send("QUIT :"+qMsg+"\r\n")
        self.t.join()
        self.threadTimer.join()
        self.s.close()
        print "IRC connection closed"
        
    ### Listening function for threading ###
    ### PING commands are handled at this level
    def listen(self,r):
        buff= ""
        looping = True
        while looping:
            try:
                buff= ""
                while (buff[-2:] != "\r\n"):
                    newData = r.s.recv(1024)
                    if not newData:
                        looping = False
                    buff = buff + newData
                for line in buff.split("\r\n"):
                    if line != "":
                        prefix,command,params = r.parse(line)
                        command = str(command).upper()
                        if command == "PING":
                            r.send("PONG :{0}\r\n".format(params[0]))
                        r.messageIn(prefix,command,params)
            except ParsingError as e:
                print "parseErr\t"+str(e)
            except socket.timeout:
                print "socket Timed out"
                self.close()

    #########
    ### Functions to be overwritten ###
                              #########

    ### messageIn, handles incoming messages ###
    def messageIn(self,prefix,command,params):
        return False
