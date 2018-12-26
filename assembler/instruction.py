# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		instruction.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		26th December 2018
#		Purpose :	Instruction handler class
#
# ***************************************************************************************
# ***************************************************************************************

from error import *
from dictionary import *
from democodegen import *

# ***************************************************************************************
#		  Helper class Responsible for code generation of single instructions
# ***************************************************************************************

class InstructionHandler(object):
	def __init__(self,dictionary,codeGenerator):
		self.dictionary = dictionary
		self.codeGenerator = codeGenerator
		self.structureStack = []

	def assemble(self,line):
		print("======= {0:3}:{1:32} ======".format(AssemblerException.LINENUMBER,line))

	def complete(self):
		if len(self.structureStack) != 0:
			raise AssemblerException("Structure not closed in procedure")