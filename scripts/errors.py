# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		errors.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		27th December 2018
#		Purpose :	Exceptions
#
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
#									Exception for HLA
# ***************************************************************************************

class AssemblerException(Exception):
	def __init__(self,message):
		Exception.__init__(self)
		self.message = message
		print(message,AssemblerException.LINE)

