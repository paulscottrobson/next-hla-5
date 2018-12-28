; *********************************************************************************
; *********************************************************************************
;
;		File:		bitwise.asm
;		Purpose:	16 bit bitwise operations
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

@word 	system.and
		ld 		a,h
		and 	b
		ld 		h,a
		ld 		a,l
		and 	c
		ld 		l,a
		ret

@word 	system.xor
		ld 		a,h
		xor 	b
		ld 		h,a
		ld 		a,l
		xor 	c
		ld 		l,a
		ret
		
@word 	system.and
		ld 		a,h
		or 		b
		ld 		h,a
		ld 		a,l
		or 		c
		ld 		l,a
		ret
		
