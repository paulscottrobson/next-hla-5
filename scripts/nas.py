from democodegen import *
from nexthla import *

source = """
proc demo(a,b,c)
a+b-c&42>$glbl:c>d:3>e!4:4>e?c
endproc
proc test2(a,b)
a>c:2>d:3>$glbl:4>$demo
"hello" > $return
endproc
""".split("\n")
asm = Assembler(DemoCodeGenerator())
asm.assemble(source)
print(asm.dictionary)
