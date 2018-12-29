# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		makekernel.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		27th December 2018
#		Purpose :	Builds assembly language file from composite library parts
#					Also has an internal linked list.
#
# ***************************************************************************************
# ***************************************************************************************

import sys,os,re

assert len(sys.argv) >= 2,"Insufficient components"
print("Creating composite assembler file")
hOut = open("temp"+os.sep+"__source.asm","w")									# output file
wordCount = 0																	# used to name labels
for libs in sys.argv[1:]:														# work through all libs
	print("\tImporting from library "+libs)										
	for root,dirs,files in os.walk("lib.source"+os.sep+libs):					# work through all files
		for f in files:
			print("\t\t\tImporting file "+f)
			src = open(root+os.sep+f).readlines()
			for l in src:
				if l.startswith("@word"):										# if found @word
					m = re.match("\@word\s*(.*)\((.*)\)\s*$",l.lower())			# break it up
					assert m is not None,"Bad line "+l
					if wordCount == 0:
						hOut.write("linkHeader:\n")
					hOut.write("link{0}:\n".format(wordCount))					# put link to NEXT entry.
					hOut.write("    dw link{0}-link{1}\n".format(wordCount+1,wordCount))	
					pc = len([x for x in m.group(2).split(",") if x != ""])		# work out # of params
					hOut.write(" 	db \"{0}\",{1}\n".format(m.group(1),pc)) 	# that ends the string
					wordCount += 1								
				else:
					hOut.write(l.rstrip()+"\n")
hOut.write("link{0}:\n".format(wordCount))										# write the last null link.
hOut.write("    dw 0\n")					
hOut.close()
print("Loaded {0} words".format(wordCount))