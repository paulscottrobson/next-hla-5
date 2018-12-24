# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		democodegen.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		24th December 2018
#		Purpose :	Dummy Code Generator class
#
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
#					This is a code generator for an idealised CPU
# ***************************************************************************************

class DemoCodeGenerator(object):
	def __init__(self):
		self.pc = 0x1000
		self.vars = 0x2000
		self.ops = { "+":"add","-":"sub","*":"mul","/":"div","%":"mod","&":"and","|":"ora","^":"xor" }
	#
	#		Get current address
	#
	def getAddress(self):
		return self.pc
	#
	#		Load a constant or variable into the accumulator.
	#
	def loadDirect(self,isConstant,value):
		src = ("#${0:04x}" if isConstant else "(${0:04x})").format(value)
		print("${0:06x}  lda   {1}".format(self.pc,src))
		self.pc += 1
	#
	#		Do a binary operation on a constant or variable on the accumulator
	#
	def binaryOperation(self,operator,isConstant,value):
		if operator == "!" or operator == "?":
			self.binaryOperation("+",isConstant,value)
			print("${0:06x}  lda.{1} [a]".format(self.pc,"b" if operator == "?" else "w"))			
			self.pc += 1
		else:
			src = ("#${0:04x}" if isConstant else "(${0:04x})").format(value)
			print("${0:06x}  {1}   {2}".format(self.pc,self.ops[operator],src))
			self.pc += 1
	#
	#		Store direct
	#
	def storeDirect(self,value):
		print("${0:06x}  sta   (${1:04x})".format(self.pc,value))
		self.pc += 1
	#
	#		Copy A to index, A indeterminate.
	#
	def transferIndex(self):
		print("${0:06x}  tax".format(self.pc))
		self.pc += 1
	#
	#		Store indirect
	#
	def storeIndirect(self,operator):
		print("${0:06x}  sta.{1} [x]".format(self.pc,"b" if operator == "?" else "w"))
		self.pc += 1
	#
	#		Allocate space for n variables. Must be a continuous block.
	#
	def allocSpace(self,count):
		addr = self.vars
		self.vars += (2 * count)
		print("${0:06x}  dw    {1}".format(addr,",".join(["$0000"]*count)))
		return addr
	#
	#		Load A with address of string constant
	#
	def loadStringConstant(self,string):
		sAddr = self.pc
		print("${0:06x}  db    \"{1}\",0".format(self.pc,string))
		self.pc += len(string)+1
		self.loadDirect(True,sAddr)
	#
	#		Call a subroutine
	#
	def callSubroutine(self,address):
		print("${0:06x}  jsr   ${1:06x}".format(self.pc,address))
		self.pc += 1
	#
	#		Return from subroutine.
	#
	def returnSubroutine(self):
		print("${0:06x}  rts".format(self.pc))
		self.pc += 1

if __name__ == "__main__":
	cg = DemoCodeGenerator()
	cg.loadDirect(True,42)
	cg.loadDirect(False,42)	
	print("------------------")
	cg.binaryOperation("%",True,44)
	cg.binaryOperation("&",False,44)	
	cg.binaryOperation("?",True,44)
	cg.binaryOperation("!",False,44)
	print("------------------")
	cg.storeDirect(46)
	print("------------------")
	cg.transferIndex()
	cg.storeIndirect("?")
	cg.storeIndirect("!")
	print("------------------")
	cg.allocSpace(4)
	cg.allocSpace(1)	
	print("------------------")
	cg.loadStringConstant("Hello world!")
	print("------------------")
	cg.callSubroutine(42)
	cg.returnSubroutine()
	print("------------------")

