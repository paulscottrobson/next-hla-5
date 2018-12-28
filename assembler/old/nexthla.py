# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		nexthla.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		27th December 2018
#		Purpose :	Next High Level Assembler, main program.
#					(no codegenerator)
#
# ***************************************************************************************
# ***************************************************************************************

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
		self.dictionary = { "$return":self.codeGen.allocSpace(None,"$return") } # dictionary, ident to address mapping.
		self.keywords = "if,endif,while,endwhile,for,endfor,endproc".split(",")
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
			self.addIdentifier(p,self.codeGen.allocSpace(None,p))				# create the local if okay
		#
		#		Find everything that is assigned to directly (e.g. >xx not >xx[4]) and create if required.
		#
		parts = re.split("(\>"+self.rxIdentifier+"\[?)",body)					# split up to find assignments to direct store
		for pn in range(0,len(parts)):											# check assignments exist.
			if parts[pn].startswith(">") and not parts[pn].endswith("["):		# exclude indirection.
				if parts[pn][1:] not in self.dictionary: 						# create if needed
					self.addIdentifier(parts[pn][1:],self.codeGen.allocSpace(None,parts[pn][1:]))
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
		if line == "endproc":													# procedure exit
			self.codeGen.returnSubroutine()
		elif line.startswith("if") or line.startswith("while"):					# if and while are very similar
			self.startIfWhile(line)												# there's just a jump back in while
		elif line == "endif" or line == "endwhile":
			self.endIfWhile(line)
		elif line.startswith("for"):											# for
			self.startFor(line)
		elif line == "endfor":													# endfor
			self.endFor(line)
		elif re.match("^"+self.rxIdentifier+"\(",line) is not None:				# <procedure>(parameters)
			self.procedureCall(line)
		else:	
			self.processExpression(line)										# failing that, an expression.
	#
	#		Assemble a procedure invocation
	#
	def procedureCall(self,line):
		m = re.match("^("+self.rxIdentifier+"\()(.*)\)$",line)					# split it up
		if m is None:
			raise AssemblerException("Syntax error in procedure call")
		parameters = [x for x in m.group(2).split(",") if x != ""]				# work through parameters
		for i in range(0,len(parameters)):
			term = self.parseTerm(parameters[i],False)							# get the term.			
			self.codeGen.loadParamRegister(i,term[0],term[1])		
		if m.group(1) not in self.dictionary:									# check we know the procedure
			raise AssemblerException("Unknown procedure "+m.group(1)+")")
		self.codeGen.callSubroutine(self.dictionary[m.group(1)])				# compile call.
	#
	#		Assemble code for if/while structure. While is an If which loops to the test :)
	#
	def startIfWhile(self,line):
		m = re.match("^(while|if)\((.*)([\#\=\<])0\)$",line)					# decode it.
		if m is None:															# couldn't
			raise AssemblerException("Structure syntax error")
		info = [ m.group(1), self.codeGen.getAddress() ]						# structure, loop address
		test = { "#":"z","=":"nz","<":"p" }[m.group(3)]							# this is the *fail* test
		info.append(test)
		self.processExpression(m.group(2))										# do the expression part
		info.append(self.codeGen.getAddress())									# struct,loop,toptest,testaddr
		self.codeGen.jumpInstruction(test,0)									# jump to afterwards on fail.
		self.structureStack.append(info)										# put on stack

	def endIfWhile(self,line):
		info = self.structureStack.pop()										# get top structure.
		if "end"+info[0] != line:												# is it not matching ?
			raise AssemblerException("Structure imbalance")
		if line == "endwhile":													# if while loop back before test.
			self.codeGen.jumpInstruction("",info[1])
		self.codeGen.jumpInstruction(info[2],self.codeGen.getAddress(),info[3])	# overwrite the jump.
	#
	#		Assemble code for for/endfor
	#
	def startFor(self,line):
		m = re.match("^for\((.*)\)$",line)										# split it up
		if m is None:															# check format.
			raise AssemblerException("Poorly formatted for")
		self.processExpression(m.group(1))										# compile the loop count value
		self.structureStack.append(["for",self.codeGen.getAddress()])			# push on the stack.
		self.codeGen.forCode()													# generate the for code.
		if "index" in self.dictionary:											# save index if it exists
			self.codeGen.storeDirect(self.dictionary["index"])
	#
	def endFor(self,line):
		info = self.structureStack.pop()										# get the element off the stack
		if info[0] != "for":													# check it is correct.
			raise AssemblerException("endfor without for")
		self.codeGen.endForCode(info[1])										# generate code for endfor/next
	#
	#		Convert an expression into code.
	#
	def processExpression(self,line):
		line = [x for x in re.split("([\+\-\*\/\%\&\|\^\>])",line) if x != ""]	# split into terms and operators.
		if len(line) % 2 == 0:													# must be n+1 terms, n operators
			raise AssemblerException("Syntax Error")
		operators = "+-*/&|^>"													# operators.
		firstTerm = self.parseTerm(line[0],True)								# first term, which can be extended
		self.codeGen.loadDirect(firstTerm[0],firstTerm[1])						# first part
		if len(firstTerm) > 2:													# first term indexed ?
			self.codeGen.binaryOperation("+",firstTerm[2],firstTerm[3])			# calculate the address
			self.codeGen.loadIndirect()
		for p in range(1,len(line),2):
			if line[p] == '>':													# assignment special case.
				target = self.parseTerm(line[p+1],True)							# term can be indirection type.
				if len(target) == 2:											# store to a specific address
					if target[0]:												# must be a variable
						raise AssemblerException("Cannot store to a constant")
					self.codeGen.storeDirect(int(target[1]))
				else:															# indirect store.
					self.codeGen.storeIndirect(target[1],target[2],target[3])
			else:																# all other operators
				nextTerm = self.parseTerm(line[p+1],False)
				self.codeGen.binaryOperation(line[p],nextTerm[0],nextTerm[1])
	#
	#		Parse a term from text. If can be @var or a number. If extended is true, it
	#		can also be @var[@var] or @var[@number]
	#
	def parseTerm(self,term,extended):
		if extended:															# can parse out @nnn[<@>nnn] ?
			m = re.match("^\@(\d+)\[(\@?)(\d+)\]$",term)						# if so try
			if m is not None:													# and if match return that.
				return [False,int(m.group(1)),m.group(2) == "",int(m.group(3))]

		m = re.match("^(\@?)(\d+)$",term)										# otherwise just <@>nnn
		if m is None:
			raise AssemblerException("Bad term "+term)
		return [m.group(1) == "",int(m.group(2))]
		print(term,m.groups() if m is not None else None)		

