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
from errors import *
from dictionary import *

# ***************************************************************************************
#									Main Assembler class
# ***************************************************************************************

class Assembler(object):
	def __init__(self,codeGenerator):
		self.codeGen = codeGenerator 											# save the code generator
		self.dictionary = Dictionary() 											# dictionary, ident to address mapping.
		result = self.codeGen.allocSpace(None,"$return")						# $return global
		self.dictionary.addIdentifier(VariableIdentifier("$return",result))
		self.keywords = "if,endif,while,endwhile,for,endfor,endproc".split(",")
		self.rxIdentifier = "[\$\_a-z][a-z0-9\.\_]*"							# rx matching identifier
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
		self.dictionary.endModule()												# only leave global procs.
	#
	#		Process procedure header (e.g. proc<identifier>(<params>)
	#
	def processProcedureHeader(self,header):
		m = re.match("proc("+self.rxIdentifier+"\()(.*)\)",header)				# split into name and parameters.
		if m is None:
			raise AssemblerException("Bad procedure definition")

		self.dictionary.removeLocalVariables()									# remove all locals.
		params = self.processIdentifiers(m.group(2),False)						# Allocate local variables, get params.
		params = [x for x in params.split(",") if x != ""]						# split into a list.
		procID = ProcedureIdentifier(m.group(1),self.codeGen.getAddress())
		self.dictionary.addIdentifier(procID)									# save procedure getAddress
		for i in range(0,len(params)):											# for each parameter.
			if not params[i].startswith(Assembler.VARMARKER):					# check parameters
				raise AssemblerException("Bad parameter")
			self.codeGen.storeParamRegister(i,int(params[i][1:]))				# write parameter to local variable.
	#
	#		Assemble the procedure body
	#
	def assembleProcedureBody(self,body):
		body = self.processIdentifiers(body,False)								# should now only be proc calls as identifiers
		self.structureStack = [ "Marker" ]										# In case over popping.
		for line in [x for x in body.split(":") if x != ""]:
			if line == Assembler.LINEMARKER:									# is it a line marker ?
				AssemblerException.LINE += 1
			else:																# it's an instruction.
				self.assembleInstruction(line)
		if len(self.structureStack) != 1:
			raise AssemblerException("Structure imbalance")
	#
	#		Assemble a single intruction
	#
	def assembleInstruction(self,line):
		print("\t\t ------ "+line+" ------")
		if line == "endproc":													# endproc
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
			self.assembleExpression(line)										# try it as a straight expression.
	#
	#		Assemble a procedure invocation
	#
	def procedureCall(self,line):
		m = re.match("^("+self.rxIdentifier+"\()(.*)\)$",line)					# split it up
		if m is None:
			raise AssemblerException("Syntax error in procedure call")
		parameters = [x for x in m.group(2).split(",") if x != ""]				# work through parameters
		for i in range(0,len(parameters)):
			mp = re.match("^(\@?)(\d+)$",parameters[i]) 						# simple. var/int only supported.
			if mp is None:														# not matched
				raise AssemblerException("Bad parameter")
			self.codeGen.loadParamRegister(i,mp.group(1) == "",int(mp.group(2)))
		procInfo = self.dictionary.find(m.group(1))								# get proc info
		if procInfo is None:													# check we know the procedure
			raise AssemblerException("Unknown procedure "+m.group(1)+")")
		self.codeGen.callSubroutine(procInfo.getValue())						# compile call.
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
		self.assembleExpression(m.group(2))										# do the expression part
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
		self.assembleExpression(m.group(1))										# compile the loop count value
		self.structureStack.append(["for",self.codeGen.getAddress()])			# push on the stack.
		self.codeGen.forCode()													# generate the for code.
		indexInfo = self.dictionary.find("index")								# index defined ?
		if indexInfo is not None:												# save index if it exists
			self.codeGen.storeDirect(indexInfo.getValue())
	#
	def endFor(self,line):
		info = self.structureStack.pop()										# get the element off the stack
		if info[0] != "for":													# check it is correct.
			raise AssemblerException("endfor without for")
		self.codeGen.endForCode(info[1])		#
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
						info = self.dictionary.find(parts[i])					# look it up.
						if info is None:										# is it new, if so make space.
							info = VariableIdentifier(parts[i],self.codeGen.allocSpace(None,parts[i]))
							self.dictionary.addIdentifier(info)
						parts[i] = Assembler.VARMARKER+str(info.getValue())
		return "".join(parts)													# put it back together

Assembler.LINEMARKER = "~"
Assembler.VARMARKER = "@"

