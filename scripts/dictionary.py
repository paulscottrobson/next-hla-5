# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		dictionary.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		27th December 2018
#		Purpose :	Next High Level Assembler, dictionary.
#
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
#						Identifiers to store in the dictionary
# ***************************************************************************************

class Identifier(object):
	def __init__(self,name,value):
		self.name = name.strip().lower()
		self.value = value
	def getName(self):
		return self.name
	def getValue(self):
		return self.value
	def isGlobal(self):
		return self.name.startswith("$")

class VariableIdentifier(Identifier):
	pass

class ProcedureIdentifier(Identifier):
	pass

# ***************************************************************************************
#									Dictionary object
# ***************************************************************************************

class Dictionary(object):
	def __init__(self):
		self.identifiers = {}
	#
	#		Add an identifier to the dictionary, testing for collision.
	#
	def addIdentifier(self,ident):
		name = ident.getName()
		if name in self.identifiers:											# check doesn't already exist
			raise AssemblerException("Duplicate identifier "+name)
		self.identifiers[name] = ident											# update dictionary.
	#
	#		Find an identifier
	#
	def find(self,key):
		key = key.strip().lower()
		return None if key not in self.identifiers else self.identifiers[key]
	#
	#		Remove local variables
	#
	def removeLocalVariables(self):
		oldDictionary = self.identifiers										# remove all local variables.
		self.identifiers = {}													# from the dictionary. 
		for name in oldDictionary.keys():
			if oldDictionary[name].isGlobal() or isinstance(oldDictionary[name],ProcedureIdentifier):
				self.identifiers[name] = oldDictionary[name]

	#
	#		Remove everything except global procedures and $return.
	#
	def endModule(self):
		oldDictionary = self.identifiers 										# remove all that aren't $<name>(
		self.identifiers = {}													# leave $return in also.
		for name in oldDictionary.keys():
			if oldDictionary[name].isGlobal() and isinstance(oldDictionary[name],ProcedureIdentifier):		# do we keep it ?
				self.identifiers[name] = oldDictionary[name]
		self.identifiers["$return"] = oldDictionary["$return"]