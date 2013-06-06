#!/usr/bin/python
#Muffin Mare V0.12.0
from ircBot import *
import random
import time
import urllib as ul
import re
import sys
import traceback
import calc
import socket
from datetime import timedelta,datetime

class muffinMare(ircBot):
    ### initilasation ###
    def __init__(self,host,port=6667,nick="pyBot",indent="pyBot",realName="pyBot",mode="",password=None,autoJoin=None):
        ircBot.__init__(self,host,port,nick,indent,realName,mode,password,autoJoin)
        
        self.OPCHARS = "%@&~"
        self.OPMODES = "hoaq"
        
        #CONSTANTS
        self.VERSION = (0,12,0)
        self.mufTypes = [
            (0.65,["apple","blueberry","chocolate","plain","double chocolate","oatmeal","sugar free","banana","kiwi","lactose free","hug"]),
            (0.35,["magic","custard","purple","ice cream","polkadot","hummas","mushroom","Ferrero rocher","jaffa","tofu","muffin","fire","hot sauce","squeaky plastic","sarsaparilla","paperclip","strawberry angel delight","Controller shaped","pony shaped","tower of","rainbow","sweet berry wine","pruppet","Broogaloo","Marmite","Sapphire","Friendship","DISCOREDED","Bogo","Cider","ChimiCherryChanga","inside-out","cupcake disguised as a","letter","Chib", "Mad Wae It", "Caber","singing","minecraft"])
        ]
        self.responses = [">Beep?","Ok {0}",">Boop","muffffinnnns","muffinMare is happy to help you all!"]
        self.defMuffin = {} #TODO revamp def muffin
        self.initCommands()
        self.PASTEBINCODE = "ab5c4f6d1af4affc3bfd32aecc80f8e6" #TODO remove pastebin stuffs
        self.COMMAND_CHAR_PRIVATE = "!"
        self.COMMAND_CHAR_PUBLIC  = "`"
        
        messages = [ #   |            |            |            |
            ("KEEP CALM" ,"AND"       ,"EAT"       ,"MUFFINS"   ),
            ("MUFFINS"   ,"FOR"       ,"EVERYPONY" ,"DARLING"   ),
            ("GIVE US"   ,"THIS DAY"  ,"OUR DAILY" ,"MUFFIN"    ),
            ("MUFFINS"   ,"FOR ALL &" ,"BOXES FOR" ,"BOXPONY"   ),
            ("'I BROUGHT","YOU A"     ,"LETTER'"   ,"9.6"       ),
            ("muffinMare","BAKED YOU" ,"A MUFFIN"  ,"BUT ATE IT"),
            ("FOR 45qg I","COULD GET" ,"ALL THE"   ,"MUFFINS"   ),
            ("HATS FOR"  ,"STYLISH"   ,"PONIES"    ,"AND EM..." )
        ]
        a,b,c,d = [i.center(10) for i in random.choice(messages)]
        
        self.responses.extend([' '.join([s.lower() for s in m]) for m in messages])
        f = open("muffinArt.txt")
        print f.read().format('.'.join(str(i) for i in self.VERSION).ljust(10),a,b,c,d)
        f.close()

    #Old logging system
    """### OVERRIDE close connection, and save logs ###
    def close(self,qMsg = "Closing..."):
        for c in self._channels.keys():
            self.closeLog(c)
        ircBot.close(self)"""

    ### Speak, warapper function for NOTIFY and PRIVMSG
    ### Also outputs to screen and recorder
    def speak(self,message,channel,logIt=True,form=None): #TODO Disputed: Should muffinMare use NOTICE or PRIVMSG.
        try:
            form = form or (self[channel].speaks and "PRIVMSG" or "NOTICE")
        except noChannelException:
            form = form or "NOTICE"
        self.send("{0} {1} :{2}\r\n".format(form,channel,message))
        #if logIt: self.log(channel,form,self.NICK,message) #Old logging system
        print "^",channel.ljust(30)[:30],message
        
    ### Message Handler ###
    def messageIn(self,prefix,command,params):
        ircBot.messageIn(self,prefix,command,params)
        if command == "PRIVMSG":
            if params[1] == "\x01VERSION\x01":
                self.speak("\x01VERSION angelicMuffins Living in a tower of the things! Sign on door reads: Pinkie can keep her cupakes!\x01",prefix[0])
            #MESSAGES
            params[1] = ''.join(re.split("[\x02\x1F\x16]|(?:\x03[0-9]{0,2}(?:,[0-9]{1,2})?)",params[1])) #REMOVE CRAP
            if params[1] == "": return True #TODO return possible error?
            print "v",params[0].ljust(30)[:30], prefix[0].ljust(30)[:30], params[1] #Display on console #TODO include time
            if params[1][0] == self.COMMAND_CHAR_PRIVATE:
                self.handleCommand(params[0],prefix[0],params[1][1:],True)
            elif params[1][0] == self.COMMAND_CHAR_PUBLIC:
                self.handleCommand(params[0],prefix[0],params[1][1:],False)
            #Random response when being addressed
            elif re.match(r"@?{0}\W".format(self.NICK),params[1]) and random.random() < 1/9 or \
              self.NICK in params[1] and random.random() < 0.1:
                self.speak(random.choice(self.responses).format(prefix[0]),params[0],form="PRIVMSG")
                
        elif command == "NOTICE":
            params[1] = ''.join(re.split("[\x02\x1F\x16]|(?:\x03[0-9]{0,2}(?:,[0-9]{1,2})?)",params[1])) #REMOVE CRAP
            if params[1] == "": return True
            print "n",params[0].ljust(30)[:30], prefix[0].ljust(30)[:30], params[1] #Display on console
        if self.DEBUG: print "{0}{1}{2}".format(prefix,command,params)

    def nickChanges(self,kind,channel,nick1,nick2=None):
        if kind == "LIST":
            pass
        elif kind == "JOIN":
            try:
                self.giveMuffin(channel,nick1,True) #TODO: Despuited should muffinMare msg muffinTypes to channel or private (TRUE=PRIVATE)
            except selfUserException:
                self.speak("Muffins for everypony... Darling",channel)
        #TODO log nick changes to concole
    
    #########
    ### Bot Functions ###
                ######### 

    ### Command Initiliser ###
    def initCommands(self):
        self.COMMANDS = {
            "help"      :command("help"     ,1,0,""  ,self.commandHelp ,"HELP {command}, Provides help on the given command or lists commands"),
            "about"     :command("about"    ,0,0,""  ,self.aboutSelf   ,"ABOUT, Provides about info on muffinMare"),
            "muffin"    :command("muffin"   ,2,0,""  ,self.wrapMuffin  ,"MUFFIN {user} {type}, passes a muffin to the given user, if no user is given you recive then muffin"),
            "spin"      :command("spin"     ,0,0,"c" ,self.spinBottle  ,"SPIN, Spins a bottle and selects a random member of the channel"),
            "dice"      :command("dice"     ,2,0,"c" ,self.rollDice    ,"DICE {number} {sides}, rolls a given amount of x-sided dice and returns the total and indivual results"),
            "quote"     :command("quote"    ,2,0,""  ,self.getQuote    ,"QUOTE {character} {episode}, Selects a random quote spoken matching the character(s) and episode(s) given. Both can be a list of comma (,) seperated values or keyword ALL"),
            #"events"    :command("events"   ,0,0,""  ,self.listEvents  ,"EVENTS, lists upto the next 3 events as listed on http://ukofequestria.co.uk/forums/upcoming-events.10"),
            "trains"    :command("trains"   ,5,2,""  ,self.trainTimes  ,"TRAINS [from] [to] {date} {outTime} {returnTime},date can be a date or a day of the week, prefix either time with 'a' or 'd' for arrival or depart."),
            "c"         :command("c"        ,1,1,""  ,self.calc        ,"C [calculation], Preforms calculations, can handel ()+-/*^ operations"),
            "mccheck"   :command("mcCheck",  1,0,""  ,self.mcServCheck ,"MCCHECK {address:port}, Checks the minecraft server running at current port, defults to UKofEquestria's mcserver"),
            "ponyep"    :command("ponyEp",   0,0,""  ,self.ponyEpisode ,"PONYEP Select a random episode to watch"),
            "youtube"   :command("youtube",  1,1,""  ,self.youtube     ,"YOUTUBE [Search term], Returns the first youtube seach result for the given term"),
            "flags"     :command("flags",    2,1,"uo",self.flags       ,"FLAGS [BOT|{user}#{channel}] {Flags}, OP ONLY. Used to set or retrive flags about the channel, user or bot"),
            #"echo"      :command("echo",     1,1,"o" ,self.echo        ,"Operator Command."), #TODO add echo command
            "ship"      :command("ship",     1,0,""  ,self.ship        ,"SHIP {User} Ships 2 random chat users, or ships the given user with a random user.") #TODO determin how it's broken and fix
        }
                
    def handleCommand(self,channel,user,command,private):
        #Check command exists
        c = command.split(" ",1)
        if len(c) == 1:
            cmdName,cmdArgs = c[0],""
        else:
            cmdName,cmdArgs = c
        cmdName = cmdName.lower()
        # Execute command
        try:
            if self.COMMANDS[cmdName](self,channel,user,private,cmdArgs) and (channel[0] == "#") and (not private):
                self[channel][user].issuedCommand()
        except KeyError:
            self.speak("Command {0} not found. {1}HELP to list commands".format(cmdName,self.COMMAND_CHAR_PRIVATE),user)
            return
        
    #########
    ### Command functions ###
                    #########
    def commandHelp(self,channel,user,replyTo,command=None):
        if command == None:
            self.speak("Command are prefixed with {1} (private response) or {2} (global response).Some commands return private response regardless. Commands are: {0}. Type !HELP [command] for more help on each command".format(', '.join(self.COMMANDS.keys()).upper(),self.COMMAND_CHAR_PRIVATE,self.COMMAND_CHAR_PUBLIC),replyTo)
        elif command in self.COMMANDS:
            self.speak(self.COMMANDS[command].help,replyTo)
        else:
            self.speak("Command {0} not found. {1}HELP to list commands".format(cmdName,self.COMMAND_CHAR_PRIVATE),replyTo)

    def ship(self,channel,user,replyTo,shipee1=None):
        chanObj = self[channel]
        if shipee1==None:        
            shipee1 = random.choice(self[channel]._userList.keys())
            shipee1 = chanObj.getNickCase(shipee1)
        shipee2 = random.choice(self[channel]._userList.keys())
        shipee2 = chanObj.getNickCase(shipee2)
        self.speak("{0} Ships {1} and {2}",user,shipee1,shipee2,replyTo)
            
    def flags (self,channel,user,replyTo,apply,flags=None):
        if apply == "bot":
            refObj = self
        if apply == "#":
            refObj = self[channel]
        else:
            try:
                u,c = apply.split("#",1)
            except ValueError:
                refObj = self[channel][apply]
            else:
                if u == '': refObj = self[c]
                elif c == '': refObj = self[channel][u]
                else: refObj = self[c][u]
        if flags == None:
            self.speak("Flags for {0}: {1}".format(apply,refObj.getFlags()),replyTo)
        else:
            refObj.setFlags(flags)
            self.speak("Flags set.".format(apply,refObj.getFlags()),replyTo)
            
    def wrapMuffin (self,channel,user,replyTo,recip=None,type=None):
        chanObj = self[channel]
        user = chanObj.getNickCase(user)
        private = replyTo == user
        if recip == None:
            recip = user
            user = None
        else:
            recip = chanObj.getNickCase(recip)
        self.giveMuffin(channel,recip,private,user,type)
    
    def youtube (self,channel,user,replyTo,query):
        d=ul.urlopen("https://gdata.youtube.com/feeds/api/videos?orderby=relevance&start-index=1&max-results=3&v=2&q={0}".format(ul.quote_plus(query))).read()
        videos = re.findall("<id>tag:youtube.com,2008:video:(.*?)</id>.*?<title>(.*?)</title>.*?<name>(.*?)</name>",d)
        self.speak("Youtube search results for {0}".format(query),replyTo)
        [self.speak("{1} by {2} http://youtu.be/{0}".format(*v),replyTo) for v in videos]
    
    def muffinAll (self,channel,user,replyTo,type=None):
        chanObj = self[channel]
        for n in chanObj:
            self.giveMuffin(channel,n.nick,True,type=type)
            
    def spinBottle (self,channel,user,replyTo):
        chanObj = self[channel]
        x = random.choice(self[channel]._userList.keys())
        x = chanObj.getNickCase(x)
        self.speak("{0} spins the bottle and it points to {1}".format(user,x),replyTo)
    
    def calc(self,channel,user,replyTo,s):
        self.speak("{0}={1}".format(s,calc.evalInfix(s)),replyTo)
    
    def wrapBirthday(self,channel,user,replyTo,d,m):
        mo = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        self.speak("Born on {0}/{1}: {2}".format(d,mo[int(m)-1],self.ponyBDayScheme(int(d),int(m))),replyTo)
    
    def getQuote (self,channel,user,replyTo,characters="all",episodes="all"):
        self.speak("Sorry my quote list got lost - \"I dont wanna talk about it\"",replyTo) #TODO
    
    def aboutSelf(self,channel,user,replyTo):
        self.speak("muffin mare version {0}, info: http://derpy.me/aboutMuffin - Built and maintained by Ripp_ in python. Designed to preform helpful tasks for the ponies of UKoE. Contact Ripp_ with sugestions or if help is requried http://derpy.me/helpMuffin".format('.'.join(str(i) for i in self.VERSION)),replyTo)
    
    def rollDice(self,channel,user,replyTo,amount=1,sides=6):
        amount,sides = int(amount),int(sides)   #Convert paramter types
        if (sides < 1) | (amount < 1) | (amount > 50): return
        d = [random.randint(1,sides) for i in range(amount)]
        self.speak("{0} rolled {1}d{2} and got {3} {4}".format(user,amount,sides,sum(d),d),channel)
    
    #TODO shorten links then include them
    #TODO multi thread web/socket request
    def listEvents(self,channel,user,replyTo):
        f = ul.urlopen("https://www.google.com/calendar/feeds/pineqj5t9k8i79chutmr1gt5s0%40group.calendar.google.com/public/basic")
        s = f.read()
        f.close()
        d = re.findall(r"<title.*?>(.*?)</title><summary type='html'>When: (.*?)&lt;.*?Where: (.*?)&lt;.*?<link .*?href='(.*?)'",s,re.DOTALL)
        tdy = []
        rst = []
        for title,date,location,link in d:
            date = date.split(" to ")[0]
            eDate = datetime.strptime(date,"%a %d %b %Y")
            if eDate == datetime.today():
                tdy.append( (title,location,link) )
            elif eDate > datetime.today():
                rst.append( (eDate,date,title,location,link) )
        rst.sort()
        if len(tdy) != 0:
            self.speak("There is {0} event(s) on today!".format(len(tdy)),replyTo)
            for title,location,link in tdy:
                self.speak(title,replyTo)
        self.speak("The next {0}/{1} upcomming events are below, for more events check http://ukofequestria.co.uk/forums/10".format(min(3,len(rst)),len(rst)),replyTo)
        for eDate,date,title,location,link in rst[:3]:
            self.speak("{0}:{1}".format(date,title),replyTo)
            
    def giveMuffin(self,channel,mFor,private,uFrom=None,type=None):
        if type == None:
            try:
                type = self.defMuffin[mFor.lower()]
            except KeyError:
                i = random.random()
                for m in self.mufTypes:
                    if i < m[0]:
                        type = random.choice(m[1])
                        break
                    else:
                        i -= m[0]
        if uFrom == None:
            if private:
                self.speak("Slides a {0} muffin to {1} under the table".format(type,mFor),mFor)
            else:
                self.speak("Gives a {0} muffin to {1}".format(type,mFor),channel)
        else:
            if private:
                self.speak("Sneakly passes a {0} muffin to {1} courtesy of {2}".format(type,mFor,uFrom),mFor)
                self.speak("{1} was given a {0} muffin as requested".format(type,mFor),uFrom)
            else:
                self.speak("Gives a {0} muffin to {1} courtesy of {2}".format(type,mFor,uFrom),channel)
    
    #UNUSED
    def postPasteBin(self,post,expire):
        query = {
            "api_dev_key":self.PASTEBINCODE,
            "api_option":"paste","api_paste_private":"1",
            "api_paste_code":post,"api_paste_expire_date":expire
        }
        f = ul.urlopen("http://pastebin.com/api/api_post.php",ul.urlencode(query))
        d = f.read()
        f.close()
        if d[:4] == "http":
            return (1,d)
        else:
            return (0,d)
            
    #TODO: Determin method to lookup a member
    #TODO Contact alteran and have him add forum API
    def lookupMember(self,channel,user,replyTo,member):
        easters = {
            "muffinmare":"Who am I? Who is but the form following the function of what. And What I am is a pony who gives out muffins. Oh you can see that? Well Im built by Ripp_ and here to help !about for more info.",
            "twilight sparkle":"Book head student to princess celestria",
            "rainbow dash":"Fastest young flier and wanna-be-bolt",
            "pinkie pie":"PINK POWER PARTY PONY (can normally party for an HOUR)",
            "rarity":"Dress maker extraordinaire, go buy some off her",
            "fluttershy":"Sweet kind gentle animal loving soft voiced pony",
            "apple jack":"Hardworking helpful cowfilly and applebucker",
            "derpy hooves":"Well wishing bringer of muffins and mail"
        }
        if member in easters:
            self.speak(easters[member],replyTo)
            return
        f = ul.urlopen("http://ukofequestria.co.uk/members/?"+ul.quote(member))
    
    #TODO Finish
    def trainTimesNEW(self,channel,user,replyTo,sFrom,sTo,*args):
        sVia = []
        dDate = ""
        dTime = ""
        rDate = ""
        rTime = ""
        colVia = True
        days = ["mon","tue","wed","thu","fri","sat","sun","monday","tuesday","wednesday","friday","saturday","sunday"]
        for a in args:
            #check if it is a date
            c = re.match(r"({0})([aAdD])([0-9][0-9]:?[0-9][0-9])",a)
            
    
    #TODO Complete overhaul
    def trainTimes(self,channel,user,replyTo,sFrom,sTo,oDate=None,oTime=None,rTime=None):
        #Check date
        days = ["mon","tue","wed","thu","fri","sat","sun","monday","tuesday","wednesday","friday","saturday","sunday"]
        if oDate == None:
            oDate = datetime.today()
        elif oDate.lower() in days:
            t = datetime.today()
            i = (days.index(oDate.lower()) - t.weekday() + 7) % 7
            oDate = t+timedelta(days=i)
        else:
            oDate = datetime.strptime(oDate,"%d/%m/%y")
            
        #Out time
        if oTime == None:
            oType = "ARR"
            oTime = "1200"
        elif oTime[0].lower() == "a":
            oType = "ARR"
            oTime = oTime[1:].replace(":","")
        elif oTime[0].lower() == "d":
            oType = "DEP"
            oTime = oTime[1:].replace(":","")
        else:
            oType = "ARR"
            oTime = oTime.replace(":","")
        url = "http://ojp.nationalrail.co.uk/service/timesandfares/"+sFrom+"/"+sTo+"/"+oDate.strftime("%d%m%y")+"/"+oTime+"/"+oType
        
        #Return time
        if rTime != None:
            if rTime[0].lower() == "a":
                rType = "ARR"
                rTime = rTime[1:].replace(":","")
            elif rTime[0].lower() == "d":
                rType = "DEP"
                rTime = rTime[1:].replace(":","")
            else:
                rType = "ARR"
                rTime = rTime.replace(":","")
            url += "/"+oDate.strftime("%d%m%y")+"/"+rTime+"/"+rType
        
        self.speak("Trains for {0} to {1} on {2}: {3}".format(sFrom,sTo,oDate,url),replyTo)
    
    #TODO multi thread web/socket request
    def mcServCheck(self,channel,user,replyTo,ad="mcsrv.ukofequestria.co.uk:25565"):
        ad = ad.split(":")
        address = ad[0]
        if len(ad)>1 : port = ad[1]
        else : port = 25565
        try:
            s = socket.create_connection((address,port))
            s.send("\xfe")
            a = s.recv(256)
            s.close()
            assert a[0] == "\xff"
            self.speak("{0}:{1} - {2} {3}/{4}".format(address,port,*a[3:].decode('utf-16be').split(u'\xa7')),replyTo)
        except socket.error as e:
            self.speak("{0}:{1} - Error, server may be down, Error no-{2}".format(address,port,e[0]),replyTo)
    
    #TODO update
    def ponyEpisode(self,channel,user,replyTo):
        episodes = ["S01E01 - Episode 1","S01E02 - Episode 2","S01E03 - The Ticket Master","S01E04 - Applebuck Season","S01E05 - Griffon the Brush-Off","S01E06 - Boast Busters","S01E07 - Dragonshy","S01E08 - Look Before You Sleep","S01E09 - Bridle Gossip","S01E10 - Swarm of the Century","S01E11 - Winter Wrap-Up","S01E12 - Call of the Cutie","S01E13 - Fall Weather Friends","S01E14 - Suited for Success","S01E15 - Feeling Pinkie Keen","S01E16 - Sonic Rainboom","S01E17 - Stare Master","S01E18 - The Show Stoppers","S01E19 - A Dog and Pony Show","S01E20 - Green is not your Color","S01E21 - Over a Barrel","S01E22 - A Bird in the Hoof","S01E23 - The Cutie Mark Chronicles","S01E24 - Owls well that Ends well","S01E25 - Party of One","S01E26 - The Best Night Ever","S02E01 - Return of Harmony Part 1","S02E02 - Return of Harmony Part 2","S02E03 - Lesson Zero","S02E04 - Luna Eclipsed","S02E05 - Sisterhooves Social","S02E06 - The Cutie Pox","S02E07 - May the Best Pet Win","S02E08 - The Mysterious Mare Do Well","S02E09 - Sweet and Elite","S02E10 - Secret of My Excess","S02E11 - Hearth's Warming Eve","S02E12 - Family Appreciation Day","S02E13 - Baby Cakes","S02E14 - The Last Roundup","S02E15 - The Super Speedy Cider Squeezy 6000","S02E16 - Read it and Weep","S02E17 - Hearts and Hooves day","S02E18 - A Friend In Deed","S02E19 - Putting Your Hoof Down","S02E20 - It's About Time","S02E21 - Dragon Quest","S02E22 - Hurricane Fluttershy","S02E23 - Ponyville Confidential","S02E24 - MMMystery on the Friendship Express"]
        d = random.randint(1,(len(episodes)-1))
        self.speak("muffinMare thinks {0} should watch {1}".format(user,episodes[d]),replyTo)    

### Main execution ###

if len(sys.argv)>1 and sys.argv[1].lower() == "debug":
    MAIN = muffinMare("irc.canternet.org",6669,nick="muffinMareDB",password=sys.argv[2],realName="ranByRipp_",mode="+BIix",autoJoin="#mmdb")
    MAIN.DEBUG == 1
    print "---------\nSTARTING IN DEBUG MODE\n---------"
else:   
    MAIN = muffinMare("irc.canternet.org",6669,nick="muffinMare",indent="pyBot",realName="ranByRipp_",mode="+BIix",password=sys.argv[1],autoJoin="#ukofequestria")
MAIN.start()
while 1:
    try:
        s = raw_input()
        if len(s) != 0:
            print ">>> "+s
            if s[0] == "#":       
                try: print str(eval(s[1:]))
                except Exception as e: print "ERROR ",str(e)
            elif s[0] == "~":
                try: exec s[1:]
                except Exception as e: print "ERROR ",str(e)
            elif s[0] == '"':
                a=s[1:].split(" ",1)
                MAIN.speak(a[1],a[0],True,"PRIVMSG")
            elif s[0] == "!":
                a=s[1:].split(" ",1)
                MAIN.speak(a[1],a[0])
            else:
                MAIN.send(s+"\r\n")
    except Exception as e:
        print str(e)
        a = raw_input("[C]ontinue, [S]top, [R]estart").lower()
        if a == "s":
            MAIN.close()
        elif a == "r":
            MAIN.close()
            MAIN.start()
    except KeyboardInterrupt:
        if raw_input("-----\nCONFIRM [E]XIT?").lower() == "e":
            MAIN.close()
        print "EXIT CANCELED."
