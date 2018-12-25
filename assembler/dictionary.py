# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		dictionary.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		24th December 2018
#		Purpose :	Identifier dictionary
#
# ***************************************************************************************
# ***************************************************************************************

from error import *

class Dictionary(object):
	def __init__(self):
		self.identifiers = {}
	#
	#		Add an entry
	#
	def add(self,info):
		#print("adding:",info)
		key = info["name"].strip().lower()
		if key in self.identifiers:
			raise AssemblerException("Duplicate identifier "+key)
		self.identifiers[key] = info
	#
	#		Find an entry
	#
	def find(self,key):
		key = key.strip().lower()
		return self.identifiers[key] if key in self.identifiers else None
	#
	#		Delete all locals
	#
	def removeLocals(self):
		idents = self.identifiers
		self.identifiers = {}
		for k in idents.keys():
			if k[0] == '$':
				self.identifiers[k] = idents[k]
