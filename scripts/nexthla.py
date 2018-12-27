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
		#
		#		Join together as one long string, then split by procedure
		#
		source = (":"+Assembler.LINEMARKER+":").join(source)					# one long string
		source = source.replace(" ","").lower() 								# make it all lowercase and no spaces.
		source = self.processIdentifiers(source,True)							# convert all globals.
		#
		#		Subdivide into procedures.
		#
		source = re.split("(proc"+self.rxIdentifier+"\(.*?\))",source)			# split up by procedures.	
		assert not source[0].startswith("proc") and len(source) % 2 != 0		# should be preamble and odd # parts
		AssemblerException.LINE = source[0].count(Assembler.LINEMARKER)			# start line.
		for i in range(1,len(source),2):										# for each pair.
			self.processProcedureHeader(source[i])								# process the header.
			self.assembleProcedureBody(source[i+1])								# assemble the body.
		#
		#		Remove everything except global procedures and $result.
		#
		oldDictionary = self.dictionary 										# remove all that aren't $<name>(
		self.dictionary = {}													# leave $result in also.
		for name in self.dictionary.keys():
			if (name.startswith("$") and name.endswith("(")) or name == "$result":
				self.dictionary[name] = oldDictionary[name]
	#
	#		Process procedure header (e.g. proc<identifier>(<params>)
	#
	def processProcedureHeader(self,header):
		m = re.match("proc("+self.rxIdentifier+"\()(.*)\)",header)				# split into name and parameters.
		if m is None:
			raise AssemblerException("Bad procedure definition")
		#
		oldDictionary = self.dictionary											# remove all local variables.
		self.dictionary = {}													# from the dictionary. 
		for name in oldDictionary.keys():
			if name.startswith("$") or name.endswith("("):
				self.dictionary[name] = oldDictionary[name]
		#
		params = self.processIdentifiers(m.group(2),False).split(",")			# Allocate local variables, get params.
		self.addIdentifier(m.group(1),self.codeGen.getAddress())				# save procedure getAddress
		for i in range(0,len(params)):											# for each parameter.
			if not params[i].startswith(Assembler.VARMARKER):					# check parameters
				raise AssemblerException("Bad parameter")
			self.codeGen.storeParamRegister(i,int(params[i][1:]))				# write parameter to local variable.
	#
	#		Assemble the procedure body
	#
	def assembleProcedureBody(self,body):
		body = self.processIdentifiers(body,False)								# should now only be proc calls as identifiers
		for line in [x for x in body.split(":") if x != ""]:
			if line == Assembler.LINEMARKER:									# is it a line marker ?
				AssemblerException.LINE += 1
			else:																# it's an instruction.
				self.assembleInstruction(line)
	#
	#		Assemble a single intruction
	#
	def assembleInstruction(self,line):
		print("\t\t ------ "+line+" ------")
		if line == "endproc":													# endproc
			self.codeGen.returnSubroutine()
		else:
			self.assembleExpression(line)										# try it as a straight expression.
	#
	#		Assemble an expression. Convert the terms to information groups, then compile it.
	#
	def assembleExpression(self,line):		
		line = [x for x in re.split("([\+\-\*\/\%\&\|\^\>])",line) if x!=""]	# split into operators and terms.
		#
		if len(line) % 2 == 0:													# must be an odd number ; n operators
			raise AssemblerException("Bad expression form")						# means n_1 terms.
		for i in range(0,len(line),2):											# parse for terms.
			term = line[i]
			m = re.match("^(\@?)(\d+)$",term) 									# simple. var/int
			if m is None:
				m = re.match("^(\@?)(\d+)([\!\?])(\@?)(\d+)$",term) 			# complex. var/int[?!]var/int
			if m is None:
				raise CompilerException("Can't understand term "+term)
			line[i] = m.groups()												# put it back in the list.
		#
		self.codeGen.loadDirect(line[0][0] == "",int(line[0][1]))				# the first term.
		#
		for i in range(1,len(line),2):											# do all the other pairs.
			if line[i] == ">":													# assign, special case.
				if line[i+1][0] == "":											# check first bit is identifier.
					raise AssemblerException("Cannot assign to a constant")
				if len(line[i+1]) == 2:											# simple store term ?
					self.codeGen.storeDirect(int(line[i+1][1]))
				else:
					self.codeGen.storeIndirect(line[i+1][2],int(line[i+1][1]),line[i+1][3] == "",int(line[i+1][4]))
			else:
				self.codeGen.binaryOperation(line[i],line[i+1][0] == "",int(line[i+1][1]))
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
	#		Process the identifiers, allocating if necessary. Can do globals only, or all.
	#		Does not touch procedure invocation.
	#
	def processIdentifiers(self,source,globalsOnly):
		idSplit = re.compile("("+self.rxIdentifier+"\(?)")						# splits out all ids.
		parts = idSplit.split(source)											# split out all identifiers.
		for i in range(0,len(parts)):											# scan all bits
			if idSplit.match(parts[i]) and not parts[i].endswith("("):			# if identifier and not a call
				if parts[i] not in self.keywords:								# and not a keywords
					if not globalsOnly or parts[i].startswith("$"):				# doing globals only ?
						if parts[i] not in self.dictionary:						# is it new, if so make space.
							self.addIdentifier(parts[i],self.codeGen.allocSpace(None,parts[i]))
						parts[i] = Assembler.VARMARKER+str(self.dictionary[parts[i]])
		return "".join(parts)													# put it back together
	#
	#		Add an identifier to the dictionary, testing for collision.
	#
	def addIdentifier(self,name,value):
		if name in self.dictionary:												# check doesn't already exist
			raise AssemblerException("Duplicate identifier "+name)
		self.dictionary[name] = value											# update dictionary.

Assembler.LINEMARKER = "~"
Assembler.VARMARKER = "@"

# TODO: Procedure calls
# TODO: Structures and stack.
