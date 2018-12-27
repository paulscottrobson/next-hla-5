; *********************************************************************************
; *********************************************************************************
;
;		File:		graphics.asm
;		Purpose:	General screen I/O routines
;		Date : 		27th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; *********************************************************************************
;
;							Clear or Reset Display
;
; *********************************************************************************

@word.ret screen.clear

GFXInitialiseDisplay
		push 	bc
		push 	de
		push 	hl
		call 	GFXInitialise				
		ld 		a,l 								; save screen extent
		ld 		(__DIScreenWidth),a
		ld 		a,h
		ld 		(__DIScreenHeight),a
		pop 	hl
		pop 	de
		pop 	bc

@end

; *********************************************************************************
;
;		Write character D (colour) E (character) to position HL.
;
; *********************************************************************************

@word.ix screen!
		pop 	de
		call 	GFXWriteCharacter
		pop 	hl
@end

GFXWriteCharacter:
		push 	af
		push 	bc
		push 	de
		push 	hl
		call	GFXCharacterHandler
		pop 	hl
		pop 	de
		pop 	bc
		pop 	af
		ret

; *********************************************************************************
;
;						Write hex word DE at position HL
;
; *********************************************************************************

@word.ix screen.hex!
		pop 	de
		call 	GFXWriteHexWord
		pop 	hl
@end

GFXWriteHexWord:
		ld 		a,6 
GFXWriteHexWordA:
		push 	bc
		push 	de
		push 	hl
		ld 		c,a
		ld 		a,d
		push 	de
		call 	__GFXWHByte
		pop 	de
		ld 		a,e
		call	__GFXWHByte
		pop 	hl
		pop 	de
		pop 	bc
		ret

__GFXWHByte:
		push 	af
		rrc 	a
		rrc		a
		rrc 	a
		rrc 	a
		call 	__GFXWHNibble
		pop 	af
__GFXWHNibble:
		ld 		d,c
		and 	15
		cp 		10
		jr 		c,__GFXWHDigit
		add		a,7
__GFXWHDigit:
		add 	a,48
		ld 		e,a
		call 	GFXWriteCharacter
		inc 	hl
		ret

; *********************************************************************************
;
;				For character A, put address of character in DE
;
; *********************************************************************************

GFXGetFontGraphicDE:
		push 	af
		push 	bc
		push 	hl
		and 	$7F 								; bits 0-6 only.
		sub 	32
		ld 		l,a 								; put in HL
		ld 		h,0
		add 	hl,hl 								; x 8
		add 	hl,hl
		add 	hl,hl
		ld 		de,(__DIFontBase) 					; add the font base.
		add 	hl,de
		ex 		de,hl 								; put in DE (font address)
		pop 	hl
		pop 	bc
		pop 	af
		cp 		$7F
		ret 	nz
		ld 		de,__GFXPromptCharacter
		ret

__GFXPromptCharacter:
		db 		$FC,$7E,$3F,$1F
		db 		$1F,$3F,$7E,$FC


