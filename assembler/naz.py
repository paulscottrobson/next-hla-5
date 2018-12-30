from imagelib import *
from z80codegen import *
from nexthla import *

source = """
proc $demo.boot():endproc
//proc demo(a,b,c)
//a+b-c&42>$glbl:c>d:3>e!4:4>e?c
//endproc
//proc test2(a,b)
//a>c:2>d:3>$glbl:4>$demo
//"hello" > $return
//endproc
//proc $test.boot():endproc
//proc test()
//	demo(1,2,3)
//	test2(a,b)
//	demo(4,2,96)
//endproc
//proc $test3.boot(a,b)
//	if (a#0):test():endif
//	while (a<0):test():endwhile
//	0>index
//	for(a):test():endfor
//	0x7ffe > a
//	@$return > a
//endproc
""".split("\n")
img = BootImage("../libraries/standard.lib")
img.echo = True
asm = Assembler(Z80CodeGenerator(img))
asm.assemble(source)
#print(asm.dictionary.getBootProcedures())
print("Main at {0:06x}".format(asm.createMain()))
print(asm.dictionary.identifiers)
