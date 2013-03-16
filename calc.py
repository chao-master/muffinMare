import re
import math
import time
import urllib as ul

class CalculatorError(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class _op():
    def __init__(self,ods,ops):
        self.ods = ods
        self.ops = ops
    def __call__(self,stk):
        if self.ods == 0:
            stk.append(self.ops())
        elif self.ods == 1:
            stk[-1] = self.ops(stk[-1])
        else:
            stk[-self.ods:]=[self.ops(stk[-self.ods:])]

""" #Removing to simplify
class _unitNumber():
	def __init__(self,s):
		self.K	= 0
		self.s	= 0
		self.m	= 0
		self.g	= 0
		self.cd	= 0
		self.mol= 0
		self.A	= 0
		try:
			self.value = int(re.match(r"-?[0-9]+(?:\.[0-9]+)?",s).group(0))
		except ValueError:
			pass
	
		units = re.findall("(Y|Z|E|P|T|G|M|k|h|da|d|c|m|u|n|p|f|a|z|y)?(K|s|m|g|cd|mol|A|Hz|rad|sr|N|Pa|J|W|C|V|F|S|Wb|T|H|lm|lx|Bq|Gy|Sv|kat|h|min)(-?[0-9]+)?",s)
		for _m,u,d in units:
			print _m,u,d
			try:
				d = int(d)
			except ValueError:
				pass
			try:
				print _m
				if   _m == "h": m = 100
				elif _m =="da": m = 10
				elif _m == "" : m = 1
				elif _m == "d": m = 0.1
				elif _m == "c": m = 0.01
				else: m = 1000**("yzafpnum kMGTPEZY".index(_m)-8)
				_bu = {
					#		K	s	m	Kg	cd	mol	A
					"K":(	1,	0,	0,	0,	0,	0,	0),
					"s":(	0,	1,	0,	0,	0,	0,	0),
					"m":(	0,	0,	1,	0,	0,	0,	0),
					"g":(	0,	0,	0,	1,	0,	0,	0),
					"cd":(	0,	0,	0,	0,	1,	0,	0),
					"mol":(	0,	0,	0,	0,	0,	1,	0),
					"A":(	0,	0,	0,	0,	0,	0,	1),
					"Hz":(	0, -1,	0,	0,	0,	0,	0),
					"N":(	0, -2,	1,	1,	0,	0,	0),
					"Pa":(	0, -2, -1,	1,	0,	0,	0),
					"J":(	0, -2,	2,	1,	0,	0,	0),
					"W":(	0, -3,	2,	1,	0,	0,	0),
					"C":(	0,	1,	0,	0,	0,	0,	1),
					"V":(	0, -3,	2,	1,	0,	0, -1),
					"F":(	0,	4, -2, -1,	0,	0,	2),
					"S":(  	0,	3, -2, -1,	0,	0,	2),
					"Wb":(	0, -2,	2,	1,	0,	0, -1),
					"T":(	0, -2,	0,	1,	0,	0, -2),
					"H":(	0, -2,	2,	1,	0,	0, -2),
					"lx":(	0,	0, -2,	0,	1,	0,	0),
					"Bq":(	0, -1,	0,	0,	0,	0,	0),
					"Gy":(	0, -2,	2,	0,	0,	0,	0),
					"Sv":(	0, -2,	2,	0,	0,	0,	0),
					"kat":(	0, -1,	0,	0,	0,	1,	0)
				}[u]
				self.K	+= _bu[0]
				self.s	+= _bu[1]
				self.m	+= _bu[2]
				self.g	+= _bu[3]
				self.cd	+= _bu[4]
				self.mol+= _bu[5]
				self.A	+= _bu[6]
			except ValueError:
				pass
			
class _currency():
	def __init__(self,symbol,updateCode):
		self.symbol = symbol
		self.updateCode = updateCode
		self.rate = 0
		self.lastUpdated = 0
	def convertFrom(self,amount,symbol=False):
		if self.lastUpdated+_currencyTimeOut < time.time():
			self.rate = re.search('rhs: "([0-9.]*)',urllib.urlopen("http://www.google.com/ig/calculator?hl=en&q={0}%3D%3F{1}".format(self.updateCode,_baseCurrency.updateCode)).read()).group(1)
		return amount*self.rate + (symbol and self.symbol or 0)
	def convertTo(self,amount,symbol=False):
		if self.lastUpdated+_currencyTimeOut < time.time():
			self.rate = re.search('rhs: "([0-9.]*)',urllib.urlopen("http://www.google.com/ig/calculator?hl=en&q={0}%3D%3F{1}".format(self.updateCode,_baseCurrency.updateCode)).read()).group(1)
		return amount/self.rate + (symbol and _baseCurrency.symbol or 0)

_currencies = {
	"qg":	_currency("qg","GBP"),
	"ap":	_currency("qp","AUD"),
	"sg":	_currency("sg","USD")
}
_currencyTimeOut = 24*60*60*60 #1 hour
_baseCurrency = _currencies["qg"]
"""
_Ops = {
    #Infix operators
    "^":	_op(2,lambda (a,b):a**b),
    "/":	_op(2,lambda (a,b):a/b),
    "*":	_op(2,lambda (a,b):a*b),
    "-":	_op(2,lambda (a,b):a-b),
    "+":	_op(2,lambda (a,b):a+b),
    #Number-theoretic and representation functions
    "ceil": _op(1,math.ceil),
    "floor":_op(1,math.floor),
    "abs":  _op(1,math.fabs),
    "fact": _op(1,math.factorial),
    #Power and logarithmic functions
    "log":	_op(2,math.log),
    "ln":	_op(1,math.log),
    "sqrt":	_op(1,math.sqrt),
    #Trigonometric functions
    "acos": _op(1,math.acos),
    "asin": _op(1,math.asin),
    "atan": _op(1,math.atan),
    "atanp": _op(2,math.atan2),
    "cos": _op(1,math.cos),
    "sin":  _op(1,math.sin),
    "tan": _op(1,math.tan),
    "hypot": _op(2,math.hypot),
    #Angular conversion
    "deg": _op(1,math.degrees),
    "rad": _op(1,math.radians),
    #Hyperbolic functions
    "acosh": _op(1,math.acosh),
    "asinh": _op(1,math.asinh),
    "atanh": _op(1,math.atanh),
    "cosh": _op(1,math.cosh),
    "sinh": _op(1,math.sinh),
    "tanh": _op(1,math.tanh),
    #Constants
    "e":	_op(0,lambda :math.e),
    "pi":	_op(0,lambda :math.pi),
    "tau":  _op(0,lambda :math.pi*2),
    "i":	_op(0,lambda:complex(0,1)),
    #Eastereggs
    "interrobangpie": _op(0,lambda:complex(0,math.pi))
}
_order = ['+', '-', '*', '/', '^']

def _convert(s):
    infix = re.findall(r'(?:(?<![a-zA-Z0-9.])-)?[0-9]+(?:\.[0-9]+)?|[a-zA-Z]+|[^a-zA-Z0-9 ]',s)
    stk = []
    post = []
    for i in infix:
        try:
            n = float(i)
            post.append(n)
        except ValueError:
            #m = re.match(r'((?<=[^a-zA-Z0-9.])-[0-9.]+|[0-9.]+)({0})'.format('|'.join(_currencies.keys())),i)
            #if m:
            #    post.append(_currencies[m.group(2)].convertFrom(int(m.group(1))))
            if i==",":
                pass
            elif i==".":
                raise CalculatorError("Unexpected decimal point incountred".format(stk.pop()))
            elif i=="(":
                stk.append(-1)
            elif i==")":
                try:
                    while stk[-1]!=-1:
                        a=stk.pop()
                        try:
                            post.append(_order[a])
                        except:
                            post.append(a)
                    stk.pop()
                except IndexError:
                    raise CalculatorError("Too many closing brackets")
            elif re.match(r'[^a-zA-Z0-9.]',i):
                try:
                    p=_order.index(i)
                except ValueError:
                    raise CalculatorError("{0} is not an infix operation".format(i))
                while len(stk)>0 and stk[-1]>p:
                   a=stk.pop()
                   try:
                       post.append(_order[a])
                   except TypeError:
                       post.append(a)
                stk.append(p)
            else:
                stk.append(i)

    while len(stk)>0:
        a=stk.pop()
        if a == -1: raise CalculatorError("Too many opening brackets")
        try:
            post.append(_order[a])
        except TypeError:
            post.append(a)
    return post

def _evalPost(post):
    stk = []
    for p in post:
        if isinstance(p, float):
            stk.append(p)
        else:
            try:
                _Ops[p](stk)
            except KeyError:
                raise CalculatorError("{0} is not a defined function".format(p))
    if len(stk) != 1:
        raise CalculatorError("Unexpected token {0} remaining".format(stk.pop()))
    return stk.pop()

def evalInfix(s):
    return _evalPost(_convert(s))
