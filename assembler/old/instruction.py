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
import re

# ***************************************************************************************
#		  Helper class Responsible for code generation of single instructions
# ***************************************************************************************

class InstructionHandler(object):
	def __init__(self,dictionary,codeGenerator,identifierRx):
		self.dictionary = dictionary
		self.codeGenerator = codeGenerator
		self.identifierRx = identifierRx
		self.structureStack = []

	def assemble(self,line):
		print("\t\t======= {0:3}:{1:32} ======".format(AssemblerException.LINENUMBER,line))
		if line == "endproc":
			self.codeGenerator.returnSubroutine()
		elif line.startswith("if") or line == "endif":
			pass
		elif line.startswith("while") or line == "endwhile":
			pass
		elif line.startswith("for") or line == "endfor":
			pass	
		elif line.startswith("@") and line.find("=") >= 0:
			self.assignmentStatement(line)
		elif re.match("^"+self.identifierRx+"\(",line) is not None:
			pass
		else:
			raise AssemblerException("Syntax Error")

	def assignmentStatement(self,line):
		m = re.match("^(\@\d+)\=(.*)$",line)
		if m is not None:
			print(m.groups())
			self.assembleExpression(m.group(2))
			self.codeGenerator.storeDirect(int(m.group(1)[1:]))
		else:
			m = re.match("^(\@\d+)([\!\?])(\@?)(\d+)\=(.*)$",line)
			if m is None:
				raise AssemblerException("Bad assignment statement")
			print(m.groups())
			self.assembleExpression(m.group(5))
			self.codeGenerator.copyResultToTemp()
			self.codeGenerator.loadDirect(False,int(m.group(1)[1:]))
			self.codeGenerator.binaryOperation("+",m.group(3) == "",int(m.group(4)))
			self.codeGenerator.storeIndirect(m.group(2))

	def assembleExpression(self,expr):
			expr = [x for x in re.split("([\+\-\*\/\%\!\?\!\^\&])",expr) if x != ""]
			m = re.match("^(\@?)(\d+)$",expr[0])
			if m is None or len(expr) % 2 != 1:
				raise AssemblerException("Bad first term in expression")
			self.codeGenerator.loadDirect(m.group(1) == "",int(m.group(2)))
			for p in range(1,len(expr),2):
				m = re.match("^(\@?)(\d+)$",expr[p+1])
				if m is None:
					raise AssemblerException("Bad term in expression")
				self.codeGenerator.binaryOperation(expr[p],m.group(1) == "",int(m.group(2)))

	def complete(self):
		if len(self.structureStack) != 0:
			raise AssemblerException("Structure not closed in procedure")