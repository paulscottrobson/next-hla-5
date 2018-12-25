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
	#
	#		Assemble a list of strings.
	#
	def assemble(self,source):
		source = self.preProcess(source)										# comments, tabs etc.
		source = self.removeStrings(source)										# remove strings.
		source = ":~:".join(source)												# make a long string with line count marks
		rx = "(proc\s+"+self.rxIdentifier+"\(.*?\))"							# definition rx - proc(<ident>)(paramstuff)
		source = re.split(rx,source) 											# split by proc 
		line = 1 																# line number
		pos = 0																	# position in source list
		while pos < len(source):												# work through the whole lot.
			if source[pos].startswith("proc"):									# found a proc
				print(">>>",line,source[pos][4:].strip(),":::",source[pos+1])
				line = line + source[pos+1].count("~")							# advance line number
				pos = pos + 2 													# one for proc one for body
			else:
				if  re.match("^[\~\s\:]*$",source[pos]) is None:				# only spaces, : and ~
					AssemblerException.LINENUMBER = line 						# code forbidden outside proc.
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