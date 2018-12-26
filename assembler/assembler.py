# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		assembler.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		26th December 2018
#		Purpose :	Assembler Class
#
# ***************************************************************************************
# ***************************************************************************************

from error import *
from dictionary import *
from democodegen import *
from instruction import *
import re

# ***************************************************************************************
#									Assembler Class
# ***************************************************************************************

class Assembler(object):
	def __init__(self,codeGenerator):
		self.codeGenerator = codeGenerator 										# save codegen
		self.dictionary = Dictionary() 											# create a dictionary
		self.rxIdentifier = "\$?[a-z\_][a-z0-9\_\.]*" 							# RegEx for an identifier.
		self.rxcIdentifier = re.compile("^"+self.rxIdentifier+"$")				# Compiled identifier test
		self.keywords = {}														# keyword hash.
		for kw in "endproc,if,while,for,endwhile,endfor,endif".split(","):
			self.keywords[kw] = kw
	#
	#		Assemble a list of strings.
	#
	def assemble(self,source):
		source = self.preProcess(source)										# comments, tabs etc.
		source = self.assembleStringConstants(source)							# assemble and replace string constants
		procedures = self.joinAndSplit(source)									# convert into seperate procedure chunks
		for proc in procedures:													# assemble them all.
			self.assembleProcedure(proc)					
	#
	#		Remove comment, edge spaces and tabs
	#
	def preProcess(self,source):
		source = [x if x.find("//") < 0 else x[:x.find("//")] for x in source]	# Remove comments
		source = [x.replace("\t"," ").strip() for x in source]					# Remove tabs and edge spaces
		return source
	#
	#		Scan for quoted strings. Compile them and replace by addreses.
	#
	def assembleStringConstants(self,source):
		rxString = re.compile("(\".*?\")")										# dividing regext.
		for i in range(0,len(source)):											# each line of source
			if source[i].find('"') >= 0:										# if it has at least one quote mark.
				parts = rxString.split(source[i])								# divide it up.
				#print(source[i],parts)
				for pn in range(0,len(parts)):									# look for string constants in there
					ps = parts[pn]
					if len(ps) >= 2 and ps[0] == '"' and ps[-1] == '"':			# if its a string constant replace it
						addr = self.codeGenerator.createStringConstant(ps[1:-1])# with the constant which is the address
						parts[pn] = str(addr)									# of the string in memory.
				source[i] = "".join(parts)										# put command back together.
		return source
	#
	#		Glue the parts together with line markers, removing spaces, subdivide into procedures.
	#
	def joinAndSplit(self,source):
		source = ":~:".join(source)												# one long string.
		source = source.replace(" ","").lower()									# remove all spaces, make l/c
		procedures = []
		parts = re.split("(proc"+self.rxIdentifier+"\(.*?\))",source)			# split around definition.
		line = 1 																# starting line #															
		section = 0																# work through.
		while section < len(parts):
			AssemblerException.LINENUMBER = line
			if parts[section].startswith("proc"):								# is it a procedure ?
				procedures.append(self.createProcedureRecord(parts[section],parts[section+1],line))
				line = line + parts[section+1].count("~")						# make line position correct
				section += 2 													# procedure and body
			else:	 															# should be empty space.
				linesInGap = parts[section].count("~")							# this many lines in empty space
				if parts[section].replace(":","").replace("~","") != "":		# check only ~ and : in there
					raise AssemblerException("Code out of procedure")
				line = line + linesInGap
				section += 1
		return procedures
	#
	#		Create a hash which has all the information about the procedure - name, parameters, body and
	#		position in source code.
	#
	def createProcedureRecord(self,header,body,startLine):
		procdef = { "line":startLine,"body":body }								# build procedure definition.
		m = re.match("^proc("+self.rxIdentifier+")\((.*?)\)$",header)			# analyse the header			
		assert m is not None 													# internal error.
		procdef["name"] = m.group(1)											# get name and parameters.
		procdef["parameters"] = [x for x in m.group(2).split(",") if x != ""]
		procdef["paramcount"] = len(procdef["parameters"])
		for p in procdef["parameters"]:											# validate the parameters
			if self.rxcIdentifier.match(p) is None:								# as legal identifiers.
				raise AssemblerException("Bad parameter")
		return procdef
	#
	#		Assemble a procedure
	#
	def assembleProcedure(self,procDef):
		AssemblerException.LINENUMBER = procDef["line"]							# cover errors before code generation
		body = procDef["body"]
		self.extractIdentifiers(body,procDef["parameters"])						# identify new identifiers, allocate memory
		body = self.replaceIdentifiers(body)									# replace all variable identifiers. All that's
																				# left is keywords and procedure names.

		paramCount = len(procDef["parameters"])									# get count of params and base address
		paramBase = 0
		if paramCount > 0:														# get address of first parameter.							
			paramBase = self.locals[procDef["parameters"][0]]
		procAddress = self.codeGenerator.getAddress()							# get execution address

																				# this is the code generator
		ihandler = InstructionHandler(self.dictionary,self.codeGenerator,self.rxIdentifier)		
		for cmd in body.split(":"):												# assemble every element
			if cmd == "~":														# new line marker.
				AssemblerException.LINENUMBER += 1
			else:
				if cmd != "":													# instruction if present
					ihandler.assemble(cmd)
		ihandler.complete()														# finished, check structures closed.

																				# add definition after can't recurse
		self.dictionary.add(ProcedureIdentifier(procDef["name"],procAddress,paramBase,paramCount))
	#
	#		Extract identifiers, locals and globals, that are assigned to.
	#
	def extractIdentifiers(self,body,parameters):
		self.locals = {} 														# first locals are parameters
		if len(parameters) != 0:
			paramMemory = self.codeGenerator.allocSpace(len(parameters))		# parameter memory contiguous
			for i in range(0,len(parameters)):
				self.locals[parameters[i]] = paramMemory + i * self.codeGenerator.getWordSize()

		assign = re.split("(\:"+self.rxIdentifier+"\=)",body)					# split out any assignments
		assign = [x[1:-1] for x in assign if x.startswith(":") and x.endswith("=")]
		for var in assign:
			if var.startswith("$"):												# is it a global
				newvar = VariableIdentifier(var,self.codeGenerator.allocSpace(1))
				self.dictionary.add(newvar)
			else:
				if var not in self.locals:										# if not already defined.
					self.locals[var] = self.codeGenerator.allocSpace(1)			# add to the locals list.
	#
	#		Replace all identifiers except procedure calls and keywords with address references.
	#
	def replaceIdentifiers(self,body):
		parts = re.split("("+self.rxIdentifier+"\(?)",body)						# split on identifier, with ( if present
		for i in range(0,len(parts)): 											# work through them
			if self.rxcIdentifier.match(parts[i]) is not None:					# match occurs, not proc calls.
				if parts[i] not in self.keywords:								# not a keyword
					if parts[i] in self.locals:									# is it a local ?
						parts[i] = "@"+str(self.locals[parts[i]]) 				# replace that.
					else:
						info = self.dictionary.find(parts[i])					# else check the dictionary
						if info is None or not isinstance(info,VariableIdentifier):	# can't find/not variable.
							raise AssemblerException("Cannot find identifier "+parts[i])
						parts[i] = "@"+str(info.getValue())						# replace it.
		return "".join(parts)

if __name__ == "__main__":
	code = """
//
//		A comment
//
proc param0()
endproc

proc param2(red,green)
	$count = red+green
endproc

proc code.boot(a,b,c)
	a = $count
	a?1 = 1 : a!2 = 2+a
	a?b = 3+b*c
	a!c = 4?b
	if (a=0)
		c=c+"fred"
	endif
	while (a<0)
		c = c + 1
	endwhile
	for (42)
		c = c + 1
	endfor
	param2(a,2)
	param0()
endproc

""".split("\n")
	Assembler(DemoCodeGenerator()).assemble(code)