# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		nhla.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		27th December 2018
#		Purpose :	Next High Level Assembler
#
# ***************************************************************************************
# ***************************************************************************************

from democodegen import *
import re

# ***************************************************************************************
#									Exception for HLA
# ***************************************************************************************

class AssemblerException(Exception):
	def __init__(self,message):
		Exception.__init__(self)
		self.message = message
		print(message,AssemblerException.LINE)

# ***************************************************************************************
#									Main Assembler class
# ***************************************************************************************

class Assembler(object):
	def __init__(self,codeGenerator):
		self.codeGen = codeGenerator 											# save the code generator
		self.dictionary = { "$return":self.codeGen.allocSpace() } 				# dictionary, ident to address mapping.
		self.keywords = "if,endif,while,endwhile,for,next,endproc".split(",")
		self.rxIdentifier = "[\$a-z][a-z0-9\.]*"								# rx matching identifier
	#
	#		Assemble a list of strings.
	#
	def assemble(self,source):
		#
		#		Source pre process, also removes quoted strings
		#
		source = [x if x.find("//") < 0 else x[:x.find("//")] for x in source]	# remove comments
		source = [x.replace("\t"," ").strip() for x in source]					# remove tabs, indent, trailing space
		source = self.processQuotedString(source)								# remove quoted strings.
		source = (":~:".join(source)).replace(" ","").lower()					# join with line marker, no space, lower case
		#
		#		Split into procedures and check code outside procedure boundary.
		#
		procList = re.split("\:proc",source)									# subdivide into procedures
		currentLine = 1															# tracks line numeber
		if procList[0].startswith(':'): 										# before first procedure definition.
			if re.match("^[\:\~]*$",procList[0]) is None:						# must be empty other than comments.
				AssemblerException.LINE = 1
				raise AssemblerException("Code before first procedure definition")
			currentLine += procList[0].count("~")								# adjust first line.
			procList.pop(0)														# remove it.
		#
		#		Assemble each procedure
		#
		for procedure in procList:												# work through all procedures
			#
			#		Break into component parts
			#
			AssemblerException.LINE = currentLine 								# set current line for proc preprocess
			m = re.match("^("+self.rxIdentifier+")\((.*?)\)(.*)$",procedure)	# split into name,params,body
			parameters = [x for x in m.group(2).split(",") if x != ""]			# definition parameters
			if len(parameters) > 4:												# Max of 4.
				raise AssemblerException("Too many parameters in procedure definition")
			#
			#		Remove old locals, add new identifiers and convert identifiers to addresses
			#
			self.removeLocalVariables()											# remove the locals
			body = self.processIdentifiers(m.group(3),parameters)				# process identifiers and parameters
			currentLine += body.count("~")										# start line next procedure
			#
			#		Define procedure, save parameter registers, compile body
			#
			self.addIdentifier(m.group(1)+"(",self.codeGen.getAddress())		# Add identifier for procedure
			for i in range(0,len(parameters)):									# code to store parameters.
				self.codeGen.storeParamRegister(i,self.dictionary[parameters[i]])
			#
			#		Assemble the body of the procedure.
			#
			self.structureStack = [ ["marker",0] ] 								# Dummy to be popped on popping error
																				# (e.g. endwhile before while)
			for line in [x for x in body.split(":") if x != ""]:				# Assemble all ines
				if line == "~":													# New line marker
					AssemblerException.LINE += 1
				else:															# Code of some sort
					self.assembleOne(line)
			if len(self.structureStack) != 1:									# check structures balance.
				raise AssemblerException("Procedure has unclosed structure")
		self.endOfModule()														# tidy up.
	#
	#		Remove quoted strings - allocate them in data memory and replace them with the address.
	#
	def processQuotedString(self,source):
		strx = re.compile("(\".*?\")")											# splits up quoted strings
		for line in range(0,len(source)):										# work through all lines
			if source[line].find('"') >= 0:										# if quoted string found
				parts = strx.split(source[line])								# split line up.
				for pn in range(0,len(parts)):									# look for quoted strings
					if parts[pn].startswith('"'):
						if parts[pn][-1] != '"' or len(parts[pn]) < 2:			# validate the string.
							AssemblerException.LINE = line+1 	
							raise AssemblerException("Bad quoted string")
																				# replace with address of string
						parts[pn] = str(self.codeGen.createStringConstant(parts[pn][1:-1]))
				source[line] = "".join(parts)									# put it back together.
		return source
	#
	#		End of module code. Remove all identifiers except global procedures and $return.
	#
	def endOfModule(self):
		oldDict = self.dictionary
		self.dictionary = {}
		for k in oldDict.keys():												# look through
			if k.startswith("$") and k.endswith("("):							# keep $<identifier>(  only
				self.dictionary[k] = oldDict[k]
		self.dictionary["$return"] = oldDict["$return"]							# preserve $return as well
	#
	#		Remove local variables
	#
	def removeLocalVariables(self):
		oldDict = self.dictionary 												# remove local variables
		self.dictionary = {}
		for k in oldDict.keys():
			if k.startswith("$") or k.endswith("("):							# leave globals and procedures
				self.dictionary[k] = oldDict[k]
	#
	#		Process parameters and body identifiers
	#
	def processIdentifiers(self,body,parameters):
		#
		#		Allocate space for parameters
		#
		for p in parameters:													# work through parameters
			if re.match(self.rxIdentifier,p) is None or p.startswith("$"):		# validate the name
				raise AssemblerException("Bad parameter "+p)
			self.addIdentifier(p,self.codeGen.allocSpace())					# create the local if okay
		#
		#		Find everything that is assigned to directly (e.g. >xx not >xx[4]) and create if required.
		#
		parts = re.split("(\>"+self.rxIdentifier+"\[?)",body)					# split up to find assignments to direct store
		for pn in range(0,len(parts)):											# check assignments exist.
			if parts[pn].startswith(">") and not parts[pn].endswith("["):		# exclude indirection.
				if parts[pn][1:] not in self.dictionary: 						# create if needed
					self.addIdentifier(parts[pn][1:],self.codeGen.allocSpace())
		#
		#		Look for every identifier, except procedure names, and replace it with identifier address.
		#
		parts = re.split("("+self.rxIdentifier+"\(?)",body)						# now replace identifiers
		rxc = re.compile("^"+self.rxIdentifier+"$")								# compile identifier test
		for pn in range(0,len(parts)):											# check all the bits for identifiers
			if rxc.match(parts[pn]) and parts[pn] not in self.keywords:			# not proc call, not keyword
				if parts[pn] not in self.dictionary:							# not known
					raise AssemblerException("Variable not defined "+parts[pn])
				parts[pn] = "@"+str(self.dictionary[parts[pn]])					# put address in
		return "".join(parts)													# put back together
	#
	#		Add an identifier to the dictionary, testing for collision.
	#
	def addIdentifier(self,name,value):
		if name in self.dictionary:												# check doesn't already exist
			raise AssemblerException("Duplicate identifier "+name)
		self.dictionary[name] = value											# update dictionary.
		#print("Created {0} {1:04x}".format(name,value))
	#
	#		Assemble a single instruction
	#
	def assembleOne(self,line):
					print("\t\t *** "+line+" ***")

source = """
proc demo(a,b,c):a[1]+b>c>d:4>d[3]:endproc			// comment
proccalc()
1+2-3*4/5%6&7^8|8>$test:endproc
proc $demo2(a)
calc()
demo(4,5,a[b])
if (a#0):b+1>b:endif
while(c#0):c-1>c:endif
for (42):b+"text">d:endif
"hello world">$message
endproc""".split("\n")
asm = Assembler(DemoCodeGenerator())
asm.assemble(source)
print(asm.dictionary)
