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
from dictionary import *
from democodegen import *
import re

# ***************************************************************************************
#									Assembler Class
# ***************************************************************************************

class Assembler(object):
	def __init__(self,codeGenerator):
		self.codeGenerator = codeGenerator 										# save codegen
		self.dictionary = Dictionary() 											# create a dictionary
		self.rxIdentifier = "\$?[a-z\_][a-z0-9\_\:\.]*" 						# RegEx for an identifier.
		self.rxcIdentifier = re.compile("^"+self.rxIdentifier+"$")				# Compiled identifier test
	#
	#		Assemble a list of strings.
	#
	def assemble(self,source):
		source = self.preProcess(source)										# comments, tabs etc.
		source = self.removeStrings(source)										# remove strings.
		source = ":~:".join(source)												# make a long string with line count marks
		source = source.lower()													# everything now lower case
		rx = "(proc\s+"+self.rxIdentifier+"\(.*?\))"							# definition rx - proc(<ident>)(paramstuff)
		source = re.split(rx,source) 											# split by proc 
		line = 1 																# line number
		pos = 0																	# position in source list
		while pos < len(source):												# work through the whole lot.
			AssemblerException.LINENUMBER = line 								# code forbidden outside proc.
			if source[pos].startswith("proc"):									# found a proc
				self.dictionary.removeLocals()									# remove locals
				self.processDefinition(source[pos][4:].strip())					# process identifier and parameters
				print(">>>",line,source[pos][4:].strip(),":::",source[pos+1])
				line = line + source[pos+1].count("~")							# advance line number
				pos = pos + 2 													# one for proc one for body
			else:
				if  re.match("^[\~\s\:]*$",source[pos]) is None:				# only spaces, : and ~
					raise AssemblerException("Code outside proc definition")
				line = line+source[pos].count("~") 								# advance line position
				pos = pos + 1
	#
	#		Remove comment, edge spaces and tabs
	#
	def preProcess(self,source):
		source = [x if x.find("//") < 0 else x[:x.find("//")] for x in source]	# Remove comments
		source = [x.replace("\t"," ").strip() for x in source]					# Remove tabs and edge spaces
		return source
	#
	#		Remove quoted strings, replace with ID numbers, save for later.
	#
	def removeStrings(self,source):
		rxString = re.compile("(\".*?\")")										# Rips out string constants
		self.stringConstants = []												# known string constants
		for i in range(0,len(source)):											# scan lines
			if source[i].find('"') >= 0:										# if quote mark in lines
				line = rxString.split(source[i])								# split up by "(.*?)"
				for j in range(0,len(line)):									# look at each part
					if line[j].startswith('"'):									# if a quoted string
						id = len(self.stringConstants)							# this is the string id#
						self.stringConstants.append(line[j][1:-1])				# add to the list of string constants
						line[j] = '"'+str(id)									# and replace the string with a ref to it
				source[i] = "".join(line)										# put line back together
		return source
	#
	#		Process procedure definition header. Strip off name, validate the parameters, allocate
	#		space for the static parameters and add definitions for the procedure and the parameters.
	#
	def processDefinition(self,header):
		m = re.match("^("+self.rxIdentifier+")\((.*)\)$",header)				# check it's okay
		assert m is not None
		params = [x.strip() for x in m.group(2).split(",") if x != ""] 			# get the parameters
		procDef = { "name":m.group(1),"type":"p","value":self.codeGenerator.getAddress() }
		procDef["paramcount"] = len(params)										# add parameter information
		if len(params) > 0:
			paramAddr = self.codeGenerator.allocSpace(len(params))				# add parameter static space
			procDef["paramaddr"] = paramAddr
			for p in range(0,len(params)):										# validate the parameters, add if okay
				if self.rxcIdentifier.match(params[p]) is None:
					raise AssemblerException("Bad parameter "+params[p])						
				self.dictionary.add({"name":params[p],"type":"v","value":paramAddr+p*2})
		self.dictionary.add(procDef)											# add the definition

if __name__ == "__main__":
	code = """
//
//				Empty comment lines.
//
proc code.boot()
	0>$total
	1>$count "hello world">d
	$count>c[4] "bad
	c[5]+4>c[9]
endproc

proc $print(n)
	"anumber" >$screen
endproc	
proc pr1.test(a,b,c):b=a+c:endproc		// here's a comment
proc pr2.loop(x)
z=x
while x#0
	print(x)
	x-1>x
	$total+1->$total
endwhile
endproc

""".split("\n")
	Assembler(DemoCodeGenerator()).assemble(code)