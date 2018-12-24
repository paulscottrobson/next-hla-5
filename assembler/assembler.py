# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		assembler.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		24th December 2018
#		Purpose :	Assembler Class
#
# ***************************************************************************************
# ***************************************************************************************

from error import *
from democodegen import *
import re

# ***************************************************************************************
#									Assembler Class
# ***************************************************************************************

class Assembler(object):
	def __init__(self,codeGenerator):
		self.codeGenerator = codeGenerator
		self.rx_Identifier = "[a-z\_][a-z0-9\_\:\.]*"
		self.rxc_Identifier = re.compile("^"+self.rx_Identifier+"$")
		self.globals = {}
		self.locals = {}
	#
	#		Assemble a list of strings.
	#
	def assemble(self,source):
		source = self.preProcess(source)											# Comments/Tabs
		source = self.globalsAndConstants(source)									# Remove global and const 
		grouped = self.groupCode(source)											# arrange into groups using nesting
		self.groupPrint(grouped)
		self.assembleGroups(grouped)												# assemble all those groups.
		print(self.globals)
	#
	#		Remove comment, right spaces, and convert tabs to 4 spaces for each line.
	#
	def preProcess(self,source):
		source = [x if x.find("#") < 0 else x[:x.find("#")] for x in source]		# Remove comment
		source = [x.rstrip().replace("\t","    ") for x in source]					# Tabs to 4 spaces
		return source
	#
	#		Look for globals (global <id>,<id>,<id> or const <id>=<nnnn>), check them
	#		add them to the global identifiers with appropriate values.
	#
	def globalsAndConstants(self,source):
		for i in range(0,len(source)):												# scan source
			if source[i].startswith("global"): 										# look for globals.
				for ident in [x.strip() for x in source[i].lower()[6:].split(",") if x.strip() != ""]:
					self.add({"name":ident,"type":"v","value":self.codeGenerator.allocSpace(1)},False)
				source[i] = ""
			if source[i].startswith("const"):										# look for const <id> = <int>
				m = re.match("^const\s+("+self.rx_Identifier+")\s*\=\s*(\d+)\s*$",source[i])
				if m is None:														# doesn't match up
					raise AssemblerException("Bad Constant definition "+source[i])
				self.add({"name":m.group(1).lower(),"type":"c","value":int(m.group(2))},False)
				source[i] = ""
		return source
	#
	#		Assemble the preprocessed source, which has been arranged into groups.
	#
	def assembleGroups(self,grouped):
		line = 0 																	# track through
		while line < len(grouped):													# until done the whole lot.
			AssemblerException.LINENUMBER = line+1									# update line number.
			if grouped[line] != "": 												# non blank lines must be def<fn>
				if grouped[line].startswith("def "):								# a quick check.
					self.assembleProcedure(line,grouped[line],grouped[line+1])		# the next one is the body
					line = line + 2													# grab two elements per def.
				else:																# error otherwise.
					raise AssemblerException("Syntax Error")
			else:																	# skip blank line.
				line = line + 1
	#
	#		Assemble a procedure. Check the definition syntax, check the parameters and
	#		build an information structure which is added to the globals.
	#		Scan the code for new locals and generate the code, then zap the locals.
	#
	def assembleProcedure(self,lineNumber,definition,body):
		m = re.match("^def\s*("+self.rx_Identifier+")\((.*)\)\:$",definition)		# check definition syntax
		if m is None:
			raise AssemblerException("Bad definition")
		procDef = { "name":m.group(1).lower(),"type":"p","value":self.codeGenerator.getAddress() }
		parameters = [x.strip() for x in m.group(2).split(",") if x.strip() != ""]	# Get parameters
		procDef["paramcount"] = len(parameters)										# save how many para,s
		if len(parameters) > 0: 													# allocate space if any.
			pMem = self.codeGenerator.allocSpace(len(parameters))
			procDef["paramaddress"] = pMem
		self.add(procDef,False)														# add procedure as a global.
		for p in range(0,len(parameters)):											# now add each parameter.
			pName = parameters[p].lower()											# get each parameter
			if not self.rxc_Identifier.match(pName): 								# check it.
				raise AssemblerException("Bad Parameter "+pName)
			self.add({"name":pName,"type":"v","value":pMem+p*2},True)				# add each one.
		#
		#	TODO: Scan for locals
		# 	TODO: Generate code
		#
		self.codeGenerator.returnSubroutine()										# generate end of func code.
		print("LOCAL",self.locals)
		self.clearLocals()															# forget all locals
	#
	#		Group code so its each level has code at that level + arrays at sub levels.
	#
	def groupCode(self,source):
		self.pos = 0 																# current pos
		self.source = source														# current code.
		group = self.groupBuild() 													# build a group at base level
		return group
	#
	#		Recursive call, builds a base at this level.
	#
	def groupBuild(self):
		currentDepth = len(self.source[self.pos])-len(self.source[self.pos].lstrip())
		currentGroup = []															# lines at this depth
		depth = currentDepth														# start at this depth
		while depth >= currentDepth and self.pos < len(self.source):				# while at the same depth or more and not done
			if depth == currentDepth:												# if at same depth
				line = self.source[self.pos].strip()								# add line at this depth.
				currentGroup.append(line)
				self.pos += 1														# and advance
			else:
				currentGroup.append(self.groupBuild())								# if more, build at next level.
			if self.pos < len(self.source):											# get depth of next line.
				depth = len(self.source[self.pos])- len(self.source[self.pos].lstrip())
				if self.source[self.pos] == "":										# blank line special case
					depth = currentDepth 											# always at current depth.

		return currentGroup
	#
	#		Simple Recursive printer of code grouped by level.
	#
	def groupPrint(self,group,level = 0):
		for e in group:
			if type(e) is list:
				self.groupPrint(e,level+1)
			else:
				print("{0}{1}".format("-"*(level*4),e))
	#
	#		Add an identifier to global or locals.
	#
	def add(self,item,isLocal = False):
		name = item["name"].strip().lower()											# name of item to be added
		target = self.locals if isLocal else self.globals 							# which dictionary it's going to
		if self.rxc_Identifier.match(name) is None:									# validate the name
			raise AssemblerException("Bad identifier "+name)
		if name in target:															# check not a duplicate.
			raise AssemblerException("Duplicate identifier "+name)
		target[name] = item															# add it.
	#
	#		Erase locals
	#
	def clearLocals(self):
		self.locals = {}
	#
	#		Find identifier, return information or None if can't find it.
	#
	def find(self,name):
		name = name.lower().strip()													# name to be searched
		if name in self.locals:														# if in locals, return that
			return self.locals[name]												# locals override globals
		return self.globals[name] if name in self.globals else None 				# otherwise look in globals


if __name__ == "__main__":
	code = """
	
global x,y,z		# some globals.
const test.value = 3	# a constant
#
#		Another constant
#
def demo1.func(a,b,c):
	test = a+b+c
def demo2(a,b):
	if a-b=0:
		a=a+1		
		c!3 = 4
		a?b = 5
	d = 3
	if b:
		x=x+y+z+5
		z=z+1
		demo1.func(1,2,3)
	if x<0:
		x=0
def nowt:func():
	x = 0
global van,wagon	

""".split("\n")
	Assembler(DemoCodeGenerator()).assemble(code)