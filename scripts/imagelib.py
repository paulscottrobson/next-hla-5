# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		imagelib.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		29th December 2018
#		Purpose :	Binary Image Library
#
# ***************************************************************************************
# ***************************************************************************************

class BootImage(object):
	def __init__(self,fileName = "boot.img"):
		self.fileName = fileName
		h = open(fileName,"rb")
		self.image = [x for x in h.read(-1)]
		h.close()
		self.sysInfo = self.read(0,0x8004)+self.read(0,0x8005)*256
		self.currentPage = 	self.read(0,self.sysInfo+2)
		self.currentAddress = self.read(0,self.sysInfo+0)+self.read(0,self.sysInfo+1)*256
		self.echo = True
		self.loadDictionary(self.read(0,0x8008)+self.read(0,0x8009)*256)
	#
	#		Return sys.info address
	#
	def getSysInfo(self):
		return self.sysInfo 
	#
	#		Return current page and address for next free code.
	#
	def getCodePage(self):
		return self.currentPage
	def getCodeAddress(self):
		return self.currentAddress
	#
	#		Convert a page/z80 address to an address in the image
	#
	def address(self,page,address):
		assert address >= 0x8000 and address <= 0xFFFF
		if address < 0xC000:
			return address & 0x3FFF
		else:
			return (page - 0x20) * 0x2000 + 0x4000 + (address & 0x3FFF)
	#
	#		Read byte from image
	#
	def read(self,page,address):
		self.expandImage(page,address)
		return self.image[self.address(page,address)]
	#
	#		Write byte to image
	#
	def write(self,page,address,data,dataType = 2):
		self.expandImage(page,address)
		assert data >= 0 and data < 256
		self.image[self.address(page,address)] = data
		if page >= self.read(0x20,self.sysInfo+4):
			self.write(0x20,self.sysInfo+4,page+2)
	#
	#		Compile byte
	#
	def cByte(self,data):
		if self.echo:
			print("{0:02x}:{1:04x}  {2:02x}".format(self.currentPage,self.currentAddress,data))
		self.write(self.currentPage,self.currentAddress,data)
		self.currentAddress += 1
	#
	#		Compile word
	#
	def cWord(self,data):
		if self.echo:
			print("{0:02x}:{1:04x}  {2:04x}".format(self.currentPage,self.currentAddress,data))
		self.write(self.currentPage,self.currentAddress,data & 0xFF)
		self.write(self.currentPage,self.currentAddress+1,data >> 8)
		self.currentAddress += 2
	#
	#		Expand physical size of image to include given address
	#
	def expandImage(self,page,address):
		required = self.address(page,address)
		while len(self.image) <= required:
			self.image.append(0x00)
	#
	#		Set boot address
	#
	def setBootAddress(self,page,address):
		self.write(0,self.getSysInfo()+12,address & 0xFF)
		self.write(0,self.getSysInfo()+13,address >> 8)
		self.write(0,self.getSysInfo()+14,page)
	#
	#		Allocate page of memory to a specific purpose.
	#
	def findFreePage(self):
		page = self.read(0,self.getSysInfo()+4)
		self.write(0,self.getSysInfo()+4,page+2)
		self.write(page,0xFFFF,0x00)
		return page	
	#
	#		Load the dictionary in the image
	#
	def loadDictionary(self,start):
		self.dictionary = {}
		while self.read(0,start) != 0 or self.read(0,start+1) != 0:
			name = ""
			p = start+2
			while self.read(0,p) >= 32:
				name = name + chr(self.read(0,p))
				p = p + 1
			record = { "name":name,"address":p+1,"parameters":self.read(0,p) }
			assert name not in self.dictionary
			self.dictionary[name] = record
			start = start + self.read(0,start+0)+self.read(0,start+1)*256
		print(self.dictionary)			
	#
	#		Find a word in the dictionary.
	#
	def find(self,word):
		word = word.strip().lower()
		return self.dictionary[word] if word in self.dictionary else None
	#
	#		Write the image file out.
	#
	def save(self,fileName = None):
		self.write(0,self.sysInfo+0,self.currentAddress & 0xFF)
		self.write(0,self.sysInfo+1,self.currentAddress >> 8)
		self.write(0,self.sysInfo+2,self.currentPage)

		fileName = self.fileName if fileName is None else fileName
		h = open(fileName,"wb")
		h.write(bytes(self.image))		
		h.close()

if __name__ == "__main__":
	z = BootImage("standard.lib")
	print(z.findFreePage())
	print(len(z.image))
	print(z.find("sys.modulus"))
	z.save("boot.img")
