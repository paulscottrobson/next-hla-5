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
	#
	#		Assemble a list of strings.
	#
	def assemble(self,source):
		source = self.preProcess(source)
		grouped = self.groupCode(source)
		print(self.groupPrint(grouped))
	#
	#		Remove comment, right space, and tabs to 4 spaces.
	#
	def preProcess(self,source):
		source = [x if x.find("#") < 0 else x[:x.find("#")] for x in source]			
		source = [x.rstrip().replace("\t","    ") for x in source]
		return source
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
		return currentGroup
	#
	#		Recursive printer of code grouped by level.
	#
	def groupPrint(self,group,level = 0):
		for e in group:
			if type(e) is list:
				self.groupPrint(e,level+1)
			else:
				print("{0}{1}".format("-"*(level*4),e))

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
		c = 4
	d = 3
	if b=0:
		x=x+y+z+5
		z=z+1
		demo1.func(1,2,3)

global van,wagon	

""".split("\n")
	Assembler(DemoCodeGenerator()).assemble(code)