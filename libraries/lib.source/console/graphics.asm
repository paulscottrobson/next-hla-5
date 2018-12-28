; *********************************************************************************
; *********************************************************************************
;
;		File:		graphics.asm
;		Purpose:	General screen I/O routines
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

@word screen.setmode(hl)
		jp 		GFXMode

@word screen.write(hl,de)
		jp 		GFXWriteCharacter

@word screen.writehex(hl,de)
		jp 		GFXWriteHexWord

; *********************************************************************************
;
;								Set Graphics Mode to L
;
; *********************************************************************************

GFXMode:
		push 	bc
		push 	de
		push 	hl
		dec 	l 									; L = 1 mode layer2
		jr 		z,__GFXLayer2
		dec 	l
		jr 		z,__GFXLowRes 						; L = 2 mode lowres

		call 	GFXInitialise48k					; L = 0 or anything else, 48k mode.
		jr 		__GFXConfigure

__GFXLayer2:
		call 	GFXInitialiseLayer2
		jr 		__GFXConfigure

__GFXLowRes:
		call 	GFXInitialiseLowRes

__GFXConfigure:
		ld 		a,l 								; save screen size
		ld 		(SIScreenWidth),a
		ld 		a,h
		ld 		(SIScreenHeight),a
		ex 		de,hl 								; save driver
		ld 		(SIScreenDriver),hl

		ld 		l,d 								; put sizes in HL DE
		ld 		h,0
		ld 		d,0
		call 	MULTMultiply16 						; multiply to get size and store.
		ld 		(SIScreenSize),hl

		pop 	hl
		pop 	de
		pop 	bc
		ret

; *********************************************************************************
;
;		Write character D (colour) E (character) to position HL.
;
; *********************************************************************************

GFXWriteCharacter:
		push 	af
		push 	bc
		push 	de
		push 	hl
		ld 		bc,__GFXWCExit
		push 	bc
		ld 		bc,(SIScreenDriver)
		push 	bc
		ret
__GFXWCExit:
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

GFXWriteHexWord:
		ld 		a,5
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
