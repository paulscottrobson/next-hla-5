; *********************************************************************************
; *********************************************************************************
;
;		File:		multiply.asm
;		Purpose:	16 bit unsigned multiply
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; 	calculate HL = HL * BC

@word 	sys.multiply()
		push 	de
		ld 		d,b
		ld 		e,c
		call 	MULTMultiply16
		pop 	de
		ret
		
; *********************************************************************************
;
;								Does HL = HL * DE
;
; *********************************************************************************

MULTMultiply16:
		push 	bc
		push 	de
		ld 		b,h 							; get multipliers in DE/BC
		ld 		c,l
		ld 		hl,0 							; zero total
__Core__Mult_Loop:
		bit 	0,c 							; lsb of shifter is non-zero
		jr 		z,__Core__Mult_Shift
		add 	hl,de 							; add adder to total
__Core__Mult_Shift:
		srl 	b 								; shift BC right.
		rr 		c
		ex 		de,hl 							; shift DE left
		add 	hl,hl
		ex 		de,hl
		ld 		a,b 							; loop back if BC is nonzero
		or 		c
		jr 		nz,__Core__Mult_Loop
		pop 	de
		pop 	bc
		ret
