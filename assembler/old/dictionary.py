# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		dictionary.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		26th December 2018
#		Purpose :	Identifier dictionary
#
# ***************************************************************************************
# ***************************************************************************************

from error import *

# ***************************************************************************************
#									Dictionary Object Classes
# ***************************************************************************************

class Identifier(object):
	def __init__(self,name,value):
		self.name = name.strip().lower()
		self.value = value
	def getName(self):
		return self.name
	def getValue(self):
		return self.value

class VariableIdentifier(Identifier):
	pass

class ProcedureIdentifier(Identifier):
	def __init__(self,name,value,paramBase,paramCount):
		VariableIdentifier.__init__(self,name,value)
		self.paramBase = paramBase
		self.paramCount = paramCount
	def getParameterBase(self):
		return self.paramBase
	def getParameterCount(self):
		return self.paramCount

# ***************************************************************************************
#										Dictionary Class
# ***************************************************************************************

class Dictionary(object):
	def __init__(self):
		self.identifiers = {}
	#
	#		Add an entry
	#
	def add(self,identifier):
		key = identifier.getName()
		if key in self.identifiers:
			raise AssemblerException("Duplicate identifier "+key)
		self.identifiers[key] = identifier
	#
	#		Find an entry
	#
	def find(self,key):
		key = key.strip().lower()
		return self.identifiers[key] if key in self.identifiers else None
