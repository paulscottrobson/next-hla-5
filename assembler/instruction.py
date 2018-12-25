# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		instruction.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		24th December 2018
#		Purpose :	Instruction handler class
#
# ***************************************************************************************
# ***************************************************************************************

from error import *
from dictionary import *
from democodegen import *

class InstructionHandler(object):
	def __init__(self,dictionary,codeGenerator,stringConstants):
		self.dictionary = dictionary
		self.codeGenerator = codeGenerator
		self.stringConstants = stringConstants
		self.structureStack = []

	def assemble(self,line):
		print(AssemblerException.LINENUMBER,line)

	def complete(self):
		if len(self.structureStack) != 0:
			raise AssemblerException("Structure not closed in procedure")