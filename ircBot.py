#!/usr/bin/python
import socket
import threading
import time
import traceback
import re
from ircBase import *

# === Base class for ircBots ===
# Parent: ircConnection (ircBase.py)
# Adds:
# * Own nick/indent/name/password/mode
# * OP and Voice recognition
# * Automatic nick serv auth
# * On timer commands [TODO still making]
class ircBot(ircConnection):

    def __init__(self,host,port=6667,nick="pyBot",indent="pyBot",realName="pyBot",mode="",password=None,autoJoin=None):
        ircConnection.__init__(self,host,port)
        self.NICK      = nick
        self.INDENT    = indent
        self.NAME      = realName
        self.PASSWORD  = password
        self.autoJoin  = autoJoin
        self.idealNick = nick
        self.MODE      = mode
        self._channels = {}
        self.OPCHARS   = "@"
        self.OPMODES   = "o"
        self.VOCHARS   = "+"
        self.VOMODES   = "v"
        self.threadTimer = None
        
    def __repr__(self):
        return "{0}-{1}:{2}".format(self.NICK,self.NAME,self._channels.keys())
        
    def start(self):
        ircConnection.start(self)
        self.send('NICK '+self.NICK+'\r\n')
        self.send('USER '+self.INDENT+' '+self.HOST+' bla :'+self.NAME+'\r\n')
    
    def onConnected(self):
        if self.MODE != "":
            self.send("MODE {0} {1}\r\n".format(self.NICK,self.MODE))  #Set Modes
        if self.PASSWORD != None:
            self.speak("REGAIN {0} {1}".format(self.idealNick,self.PASSWORD),"NICKSERV",False,"PRIVMSG")    #Regain if taken
            self.speak("IDENTIFY {0}".format(self.PASSWORD),"NICKSERV",False,"PRIVMSG")						#Register with nickserv
        if self.autoJoin != None:
            self.send("JOIN {0}\r\n".format(self.autoJoin))                                                 #Auto join
        #self.threadTimer = threading.Thread(target=self.timerWrapper,args=[self,300,5])
        #self.threadTimer.start()
        
    
    ### Message Handling ###
    def messageIn(self,prefix,command,params):
    
        #Check nick changes and update list as requried
        #Also detects when connected and runs onConnected
        #JOIN PART KICK NICK MODE 353 396
        if command == "PING": #Bot beacon
            pidtLog = open("pidt","w")
            pidtLog.write(str(os.getpid()))
            pidtLog.close()
            os.system("top -p "+str(os.getpid())+" -b -n 1 | tail -n 1 >> webLog") #I know it's bad pratice shut up ok it's mainly a debug thing anyway
        elif command == "JOIN":
            if prefix[0] == self.NICK:
                self[params[0]] = channel(self,params[0])
                self.nickChanges("JOIN",params[0],self.NICK)
            else:
                self[params[0]].nickHandler(self,"JOIN",prefix[0])
        elif command == "PART":
            self[params[0]].nickHandler(self,"PART",prefix[0])
        elif command == "KICK":
            self[params[0]].nickHandler(self,"KICK",params[1],prefix[0]) #Kicked, Kicker
        elif command == "QUIT":
            for c in self._channels.values():
                c.nickHandler(self,"QUIT",prefix[0])
        elif command == "NICK":
            for c in self._channels.values():
                c.nickHandler(self,"NICK",prefix[0],params[0])
        elif command == "MODE":
            if params[0][0] == "#":
                self[params[0]].nickHandler(self,"MODE",params[2],params[1])
        elif command == "353":
            self[params[2]].nickHandler(self,"LIST",params[3])
        elif command == "396":
            self.onConnected()
        else:
            return False
        return True 
    
    ### Timer handling ###
    def timerWrapper(self,r,interval,gap=5):
        i = interval//gap
        gap = interval/i
        while not r.lFlag.is_set():
            j=0
            while j<i:
                time.sleep(gap)
                i+=1
            if not r.onTimer(): break
    
    #Container type funtions
    def __setitem__(self,key,value):
        key = key.lower()
        if (key[0] != "&") and (key[0] != "#"):
            key = "#" + key
        self._channels[key] = value
    
    def __getitem__(self,key):
        key = key.lower()
        if (key[0] != "&") and (key[0] != "#"):
            key = "#" + key
        try: return self._channels[key]
        except KeyError: raise noChannelException(key)
    
    def __delitem__(self,key):
        key = key.lower()
        if (key[0] != "&") and (key[0] != "#"):
            key = "#" + key
        try: del self._channels[key]
        except KeyError: raise noChannelException(key)
    
    def __len__(self):
        return len(self._channels)

    def __iter__(self):
        return self._channels
    
    def __contains__(self,key):
        key = key.lower()
        if (key[0] != "&") and (key[0] != "#"):
            key = "#" + key
        return key in self._channels.keys()
    
    #########
    ### Functions to be overwritten ###
                              #########                    
    
    ### nickChanges, called when nick operations occout
    def nickChanges(self,kind,channel,nick1,nick2=None):
        return False
    
    ### onTimer, called every X seconds to preform automated tasks
            #Return false to STOP the automatic timer calling
    def onTimer(self):
        return False
        
# === Channel object ===
# Handels: 
# * List of user names on the channel
# * The time limits between users issuing commands
# * Function to control nicks [TODO fix user leaving]
class channel():
    def __init__(self,bot,chan,flTimer=15,voTimer=5,opTimer=0):
        self.chan = chan
        self._userList = {}
        self.parent = bot
        self.flTimer = flTimer
        self.needVoice = False
        self.speaks = False
        self.voTimer = voTimer
        self.opTimer = opTimer
        
    def __repr__(self):
        return "{0}|{1}".format(self.chan,self._userList.keys())

    def getFlags(self):
        pFlags,pSetts = "",""
        #Flood timers
        if self.flTimer:
            pFlags+="f"
            pSetts+=" {0}".format(self.flTimer)
        if self.voTimer:
            pFlags+="v"
            pSetts+=" {0}".format(self.voTimer)
        if self.opTimer:
            pFlags+="o"
            pSetts+=" {0}".format(self.opTimer)
        if self.needVoice:
            pFlags+="r"
        if self.speaks:
            pFlags+="s"
        rtn = ""
        if pFlags: rtn+="+"+pFlags
        if pSetts: rtn+=pSetts
        return rtn
        
    def setFlags(self,strFlags):
        data = re.findall(r"\b[^+-]\S+",strFlags)
        for i in re.findall("[+\-][a-zA-Z]+",strFlags):
            s = i[0] == "+"
            for j in i[1:]:
                if j == "r": self.needVoice = s
                elif j == "s": self.speaks = s
                elif j == "f":
                    if s: self.flTimer = int(data.pop(0))
                    else: self.flTimer = 0
                elif j == "v":
                    if s: self.voTimer = int(data.pop(0))
                    else: self.voTimer = 0
                elif j == "o":
                    if s: self.opTimer = int(data.pop(0))
                    else: self.opTimer = 0
                    
            
        
    def getNickCase(self,nick):
        return self[nick].nick
    
    def nickHandler(self,parent,type,nick1,nick2=None):
        sent = False
        if type == "NICK":
            if nick1 == self.parent.NICK:
                self.parent.NICK = nick1
            try:
                if nick1.lower() == nick2.lower():
                    self[nick1].nick = nick2				   #update capatlisation
                else:
                    self[nick2] = self[nick1]                  #swap pointers
                    del self[nick1]                            #del old one
                    self[nick2].nick = nick2                   #update name
            except noUserException: pass
        elif type == "JOIN":
                self[nick1] = user(self,nick1)
        elif type == "LIST":
            sent = True
            for nick in nick1.split(" "):                                   #Iter through list
                try:
                    if nick != "":               #Not blank
                        if (nick[0] < "A") | ((nick[0] > "Z") & (nick[0] < "a")) | (nick[0] > "z"):
                            op = nick[0] in parent.OPCHARS
                            vo = nick[0] in parent.VOCHARS
                            nick = nick[1:]
                        else:
                            nick = nick
                            op = False
                            vo = False
                        self[nick] = user(self,nick,op,vo)          #Add to list
                        self.parent.nickChanges("LIST",self.chan,nick)
                except selfUserException:
                    pass
        elif type == "PART" or type == "KICK" or type == "QUIT":
            try:
                if nick1 == self.parent.NICK:
                    sent = True
                    self.parent.nickChanges(type,self.chan,nick1,nick2)
                    del self.parent[self.chan]                      #Left channel
                else:
                    del self[nick1]
            except noUserException: pass
        elif type == "MODE" and nick1 != self.parent.NICK: #TODO Change to use self user exceptions
            try:
                if not "-" in nick2:
                    add,sub = nick2[1:],""
                elif not "+" in nick2:
                    add,sub = "",nick2[1:]
                else:
                    i,j = nick2.find("+"),nick2.find("-")
                    add,sub = nick2[i+1:j],nick2[j+1:i]
                    if i > j: add,sub = sub,add
                userObj = self[nick1]
                for s in sub:
                    if s in parent.OPMODES: userObj.op -=1
                    if s in parent.VOMODES: userObj.vo -=1
                for s in add:
                    if s in parent.OPMODES: userObj.op +=1
                    if s in parent.VOMODES: userObj.vo +=1
            except noUserException: pass
        if not sent: self.parent.nickChanges(type,self.chan,nick1,nick2)

    #Container type funtions
    def __setitem__(self,key,value):
        key = key.lower()
        if key == self.parent.NICK.lower():
            raise selfUserException(key,self)
        else:
            if (key[0] < "A") | ((key[0] > "Z") & (key[0] < "a")) | (key[0] > "z"):
                key = key[1:]
            self._userList[key] = value
    def __getitem__(self,key):
        key = key.lower()
        if (key[0] < "A") | ((key[0] > "Z") & (key[0] < "a")) | (key[0] > "z"):
            key = key[1:]
        try: return self._userList[key]
        except KeyError:
            if key == self.parent.NICK.lower():
                raise selfUserException(key,self)
            else:
                raise noUserException(key,self)
    
    def __delitem__(self,key):
        key = key.lower()
        if (key[0] < "A") | ((key[0] > "Z") & (key[0] < "a")) | (key[0] > "z"):
            key = key[1:]
        try: del self._userList[key]
        except KeyError:
            if key == self.parent.NICK.lower():
                raise selfUserException(key,self)
            else:
                raise noUserException(key,self)
    
    def __len__(self):
        return len(self._userList)

    def __iter__(self):
        return iter(self._userList.values())
    
    def __contains__(self,key):
        key = key.lower()
        if (key[0] < "A") | ((key[0] > "Z") & (key[0] < "a")) | (key[0] > "z"):
            key = key[1:]
        return key in self._userList.keys()
         
# === User Object ===    
# Handels:
# * Infomation on user including:
#   * Time of last commands
#   * Allowance to use commands
#   * OP/VOICE/REGULAR
#   * Correct name captilization    
class user():
    def __init__(self,parent,nick,op=0,vo=False,allow=True):
        self.nick = nick
        self.op = op
        self.vo = vo
        self.channel = parent
        self.lastCmd = 0
        self.allow = allow
        if nick.lower() == "ripp_": self.op = 999 #DEBUG GOD MODE!
        
    def __repr__(self):
        return "{0}|{1}".format(self.nick,self.op)
    
    #Administration/Flag controls
    def getFlags(self):
        #Controlable flags
        a,b="",""
        if self.allow: a+="a"
        if a != "": a="+"+a
        
        #IRC controlled flags
        if self.op: b+="o"
        if self.vo: b+="v"
        if b != "": return a+" +"+b
        else: return a
    
    def setFlags(self,strFlags):
        groups = re.findall("[+\-][a-zA-Z]+",strFlags)
        for i in groups:
            s = i[0] == "+"
            for j in i[1:]:
                if j == "a": self.allow = s
    
    #Used for testing if the user is currentlly allowed to issue commands
    #TODO raise errors if user can't use command insted of returning string
    def allowed(self,private,reqOp=False):
        if not self.allow:
            return "You are not allowed to use commands in this channel."
        if self.channel.needVoice and not (self.vo or self.op):
            return "You need to have atleast voice to use commadns in this channel."
        if not private:
            if   self.op:
                if self.lastCmd + self.channel.opTimer > time.time(): return "Flood protection in place."
            elif self.vo:
                if self.lastCmd + self.channel.voTimer > time.time(): return "Flood protection in place."
            elif   self.lastCmd + self.channel.flTimer > time.time(): return "Flood protection in place."  
        if reqOp and not self.op:
                return "This Command needs op privilages."
        return ""
        
    def issuedCommand(self):
        self.lastCmd = int(time.time())
        
# === Command Object ===
# Handels:
# * Checking users are allowed to,
# * Calling command functions,
# * Updating the user timer,
# * & Command error wrapping
class command():    #TODO Shift to ircBase file? Or split bot functions out to seperate file?
    def __init__(self,name,argCount,req,flags,fun,help):
        self.name = name
        self.argCount = argCount
        self.req = req
        self.fun = fun
        self.flags = flags
        self.help = help
    
    def __call__(self,parent,channel,user,private,argStr):
        if channel[0] == "#":
            chanObj = parent[channel]
            userObj = chanObj[user]
            alow = userObj.allowed(private,"o" in self.flags)
            if alow != "" :
                parent.speak("You are not allowed to issue commands becuase {0}".format(alow),user)
                return False
        if argStr == "" or self.argCount == 0:
            args = []
        else:
            args = argStr.split(" ")
            
        if   "c" in self.flags: replyToArg = channel
        elif "u" in self.flags: replyToArg = user
        else:
            if "s" in self.flags: private = not private
            if private: replyArg = user
            else: replyArg = channel
            
        userArg = ""
        channelArg = ""
        while len(args) > 0:
            if args[0][0] != "-":
                break
            else:
                if args.pop(0) == "-":  #-: Flag, End of flags
                    break
                elif args.pop(0) == "-u": # -u: User modifier flag
                    if userObj.op:
                        userArg = args.pop(0)
                    else:
                        args.pop(0)
                elif args.pop(0) == "-b" # -b: bot as user flag
                    if userObj.op:
                        userArg = parent.NICK
                elif args.pop(0) == "-c": # -c: Channel modifer flag
                    if userObj.op:
                        channelArg = args.pop(0)
                    else:
                        args.pop(0)
                elif args.pop(0) == "-r": # -r: ReplyTo Modifier flag
                    if userObj.op:
                        replyArg = args.pop(0)
                    else:
                        args.pop(0)
        
        #Reduce arguments
        if len(args) > self.argCount:
            args[self.argCount-1:]=[' '.join(map(str,args[self.argCount-1:]))]
        
        #Check length
        if len(args) < self.req:
            parent.speak("{0} requries at least {2} paramters only {1} given".format(self.name,len(args),self.req),user)
            return False
        
        #Exectute command
        try:
            self.fun(channel,user,replyTo,*args)
            return True
        except Exception as e:
            parent.speak("Error in command {0}: {1} - {2}".format(self.name,argStr,str(e)),user)
            print "Error in command {0}: {1} - {2}".format(self.name,argStr,str(e))
            traceback.print_exc()
            return False

# == Restricted Command Object ===
# Parent: command
# Adds:
# * Restriction tied to the command as oppsed to the user
### TODO: Check over class is broken
class restCmd(command):
    def __init__(self,name,argCount,req,flags,fun,fTimer,help):
        command.__init__(self,name,argCount,req,flags,fun,help)
        self.fTimer = fTimer
        self.lstCalled = 0
    
    def __call__(self,parent,channel,user,private,argStr):
        if private:
            return command(self,parent,channel,user,private,argStr)
        else:
            if self.lstCalled + self.fTimer < time.time():
                if command(self,parent,channel,user,private,argStr):
                    self.lstCalled = time.time()
                    return True
                else:
                    parent.speak("You are not allowed to use this command as it has recentally been used",user)
                    return False

class noUserException(Exception):
    def __init__(self,user,chanObj):
        self.user = user
        self.chanObj = chanObj
    def __str__(self):
        return "User {0} not found in channel {1}".format(self.user,self.chanObj.chan)

class selfUserException(Exception):
    def __init__(self,user,chanObj):
        self.user = user
        self.chanObj = chanObj
    def __str__(self):
        return "{0} cannot apply that action to itself.".format(self.user)
        
class noChannelException(Exception):
    def __init__(self,chan):
        self.chan = chan
    def __str__(self):
        return "Channel {0} not found".format(self.chan)
