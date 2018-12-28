from democodegen import *
from nexthla import *

source = """
proc demo(a,b,c):a[1]+b>c>d:4>d[3]:endproc			// comment
proccalc()
1+2-3*4/5%6&7^8|8>$test:endproc
proc $demo2(a)
a[b]>c
if(c=0):calc():endif
demo(4,5,a)
if (a#0):b+1>b:endif
while(c<0):c-1>c:endwhile
0>index
for (42):b+"text">d:endfor
"hello world">$message
endproc""".split("\n")
asm = Assembler(DemoCodeGenerator())
asm.assemble(source)
print(asm.dictionary)
