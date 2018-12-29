; *********************************************************************************
; *********************************************************************************
;
;		File:		divide.asm
;		Purpose:	16 bit unsigned divide
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

;	Actually calculates HL / BC

linkHeader:
link0:
    dw link1-link0
 	db "sys.divide",0
	push 	bc
	push 	de
	ex 		de,hl
	ld 		l,c
	ld 		h,b
	call 	DIVDivideMod16
	ex 		de,hl
	pop 	de
	pop 	bc
	ret

;	Actually calculates HL % BC

link1:
    dw link2-link1
 	db "sys.modulus",0
	push 	bc
	push 	de
	ex 		de,hl
	ld 		l,c
	ld 		h,b
	call 	DIVDivideMod16
	pop 	de
	pop 	bc
	ret

; *********************************************************************************
;
;			Calculates DE / HL. On exit DE = result, HL = remainder
;
; *********************************************************************************

DIVDivideMod16:

	push 	bc
	ld 		b,d 				; DE
	ld 		c,e
	ex 		de,hl
	ld 		hl,0
	ld 		a,b
	ld 		b,8
Div16_Loop1:
	rla
	adc 	hl,hl
	sbc 	hl,de
	jr 		nc,Div16_NoAdd1
	add 	hl,de
Div16_NoAdd1:
	djnz 	Div16_Loop1
	rla
	cpl
	ld 		b,a
	ld 		a,c
	ld 		c,b
	ld 		b,8
Div16_Loop2:
	rla
	adc 	hl,hl
	sbc 	hl,de
	jr 		nc,Div16_NoAdd2
	add 	hl,de
Div16_NoAdd2:
	djnz 	Div16_Loop2
	rla
	cpl
	ld 		d,c
	ld 		e,a
	pop 	bc
	ret


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

link2:
    dw link3-link2
 	db "sys.multiply",0
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

link3:
    dw link4-link3
 	db "sys.and",0
		ld 		a,h
		and 	b
		ld 		h,a
		ld 		a,l
		and 	c
		ld 		l,a
		ret

link4:
    dw link5-link4
 	db "sys.xor",0
		ld 		a,h
		xor 	b
		ld 		h,a
		ld 		a,l
		xor 	c
		ld 		l,a
		ret

link5:
    dw link6-link5
 	db "sys.or",0
		ld 		a,h
		or 		b
		ld 		h,a
		ld 		a,l
		or 		c
		ld 		l,a
		ret

; *********************************************************************************
; *********************************************************************************
;
;		File:		screen48k.asm
;		Purpose:	Hardware interface to Spectrum display, standard but with
;					sprites enabled.
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; *********************************************************************************
;
;						Call the SetMode for the Spectrum 48k
;
; *********************************************************************************

GFXInitialise48k:
		push 	af 									; save registers
		push 	bc

		ld 		bc,$123B 							; Layer 2 access port
		ld 		a,0 								; disable Layer 2
		out 	(c),a
		db 		$ED,$91,$15,$3						; Disable LowRes but enable Sprites

		ld 		hl,$4000 							; clear pixel memory
__cs1:	ld 		(hl),0
		inc 	hl
		ld 		a,h
		cp 		$58
		jr 		nz,__cs1
__cs2:	ld 		(hl),$47							; clear attribute memory
		inc 	hl
		ld 		a,h
		cp 		$5B
		jr 		nz,__cs2
		xor 	a 									; border off
		out 	($FE),a
		pop 	bc
		pop 	af
		ld 		hl,$1820 							; H = 24,L = 32, screen extent
		ld 		de,GFXPrintCharacter48k
		ret

; *********************************************************************************
;
;				Write a character E on the screen at HL, in colour D
;
; *********************************************************************************

GFXPrintCharacter48k:
		push 	af 									; save registers
		push 	bc
		push 	de
		push 	hl

		ld 		b,e 								; character in B
		ld 		a,h 								; check range.
		cp 		3
		jr 		nc,__ZXWCExit
;
;		work out attribute position
;
		push 	hl 									; save position.
		ld 		a,h
		add 	$58
		ld 		h,a

		ld 		a,d 								; get current colour
		and 	7  									; mask 0..2
		or 		$40  								; make bright
		ld 		(hl),a 								; store it.
		pop 	hl
;
;		calculate screen position => HL
;
		push 	de
		ex 		de,hl
		ld 		l,e 								; Y5 Y4 Y3 X4 X3 X2 X1 X0
		ld 		a,d
		and 	3
		add 	a,a
		add 	a,a
		add 	a,a
		or 		$40
		ld 		h,a
		pop 	de
;
;		char# 32-127 to font address => DE
;
		push 	hl
		ld 		a,b 								; get character
		and 	$7F 								; bits 0-6 only.
		sub 	32
		ld 		l,a 								; put in HL
		ld 		h,0
		add 	hl,hl 								; x 8
		add 	hl,hl
		add 	hl,hl
		ld 		de,(SIFontBase) 					; add the font base.
		add 	hl,de
		ex 		de,hl 								; put in DE (font address)
		pop 	hl
;
;		copy font data to screen position.
;
		ld 		a,b
		ld 		b,8 								; copy 8 characters
		ld 		c,0 								; XOR value 0
		bit 	7,a 								; is the character reversed
		jr 		z,__ZXWCCopy
		dec 	c 									; C is the XOR mask now $FF
__ZXWCCopy:
		ld 		a,(de)								; get font data
		xor 	c 									; xor with reverse
		ld 		(hl),a 								; write back
		inc 	h 									; bump pointers
		inc 	de
		djnz 	__ZXWCCopy 							; do B times.
__ZXWCExit:
		pop 	hl 									; restore and exit
		pop 	de
		pop 	bc
		pop 	af
		ret
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

link6:
    dw link7-link6
 	db "screen.setmode",1
		jp 		GFXMode

link7:
    dw link8-link7
 	db "screen.write",2
		jp 		GFXWriteCharacter

link8:
    dw link9-link8
 	db "screen.writehex",2
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
; *********************************************************************************
; *********************************************************************************
;
;		File:		screen_layer2.asm
;		Purpose:	Layer 2 console interface, sprites enabled, no shadow.
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; *********************************************************************************
;
;								Clear Layer 2 Display.
;
; *********************************************************************************


GFXInitialiseLayer2:
		push 	af
		push 	bc
		push 	de
		db 		$ED,$91,$15,$3						; Disable LowRes but enable Sprites

		ld 		e,2 								; 3 banks to erase
L2PClear:
		ld 		a,e 								; put bank number in bits 6/7
		rrc 	a
		rrc 	a
		or 		2+1 								; shadow on, visible, enable write paging
		ld 		bc,$123B 							; out to layer 2 port
		out 	(c),a
		ld 		hl,$4000 							; erase the bank to $00
L2PClearBank: 										; assume default palette :)
		dec 	hl
		ld 		(hl),$00
		ld 		a,h
		or 		l
		jr		nz,L2PClearBank
		dec 	e
		jp 		p,L2PClear

		xor 	a
		out 	($FE),a

		pop 	de
		pop 	bc
		pop 	af
		ld 		hl,$1820 							; still 32 x 24
		ld 		de,GFXPrintCharacterLayer2
		ret
;
;		Print Character E, colour D, position HL
;
GFXPrintCharacterLayer2:
		push 	af
		push 	bc
		push 	de
		push 	hl
		push 	ix

		ld 		b,e 								; save A temporarily
		ld 		a,b
		and 	$7F
		cp 		32
		jr 		c,__L2Exit 							; check char in range
		ld 		a,h
		cp 		3
		jr 		nc,__L2Exit 						; check position in range
		ld 		a,b

		push 	af
		xor 	a 									; convert colour in C to palette index
		bit 	0,d 								; (assumes standard palette)
		jr 		z,__L2Not1
		or 		$03
__L2Not1:
		bit 	2,d
		jr 		z,__L2Not2
		or 		$1C
__L2Not2:
		bit 	1,d
		jr 		z,__L2Not3
		or 		$C0
__L2Not3:
		ld 		c,a 								; C is foreground
		ld 		b,0									; B is xor flipper, initially zero
		pop 	af 									; restore char

		push 	hl
		bit 	7,a 								; adjust background bit on bit 7
		jr 		z,__L2NotCursor
		ld 		b,$FF 								; light grey is cursor
__L2NotCursor:
		and 	$7F 								; offset from space
		sub 	$20
		ld 		l,a 								; put into HL
		ld 		h,0
		add 	hl,hl 								; x 8
		add 	hl,hl
		add 	hl,hl

		push 	hl 									; transfer to IX
		pop 	ix
		pop 	hl

		push 	bc 									; add the font base to it.
		ld 		bc,(SIFontBase)
		add 	ix,bc
		pop 	bc
		;
		;		figure out the correct bank.
		;
		push 	bc
		ld  	a,h 								; this is the page number.
		rrc 	a
		rrc 	a
		and 	$C0 								; in bits 6 & 7
		or 		$03 								; shadow on, visible, enable write pagin.
		ld 		bc,$123B 							; out to layer 2 port
		out 	(c),a
		pop 	bc
		;
		; 		now figure out position in bank
		;
		ex 		de,hl
		ld 		l,e
		ld 		h,0
		add 	hl,hl
		add 	hl,hl
		add 	hl,hl
		sla 	h
		sla 	h
		sla 	h

		ld 		e,8 								; do 8 rows
__L2Outer:
		push 	hl 									; save start
		ld 		d,8 								; do 8 columns
		ld 		a,(ix+0) 							; get the bit pattern
		xor 	b 									; maybe flip it ?
		inc 	ix
__L2Loop:
		ld 		(hl),0 								; background
		add 	a,a 								; shift pattern left
		jr 		nc,__L2NotSet
		ld 		(hl),c 								; if MSB was set, overwrite with fgr
__L2NotSet:
		inc 	hl
		dec 	d 									; do a row
		jr 		nz,	__L2Loop
		pop 	hl 									; restore, go 256 bytes down.
		inc 	h
		dec 	e 									; do 8 rows
		jr 		nz,__L2Outer
__L2Exit:
		pop 	ix
		pop 	hl
		pop 	de
		pop 	bc
		pop 	af
		ret
; *********************************************************************************
; *********************************************************************************
;
;		File:		screen_lores.asm
;		Purpose:	LowRes console interface, sprites enabled.
;		Date : 		28th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; *********************************************************************************
;
;								Clear LowRes Display.
;
; *********************************************************************************

GFXInitialiseLowRes:
		push 	af
		push 	bc
		push 	de

		db 		$ED,$91,$15,$83						; Enable LowRes and enable Sprites
		xor 	a 									; layer 2 off.
		ld 		bc,$123B 							; out to layer 2 port
		out 	(c),a

		ld 		hl,$4000 							; erase the bank to $00
		ld 		de,$6000
LowClearScreen: 									; assume default palette :)
		xor 	a
		ld 		(hl),a
		ld 		(de),a
		inc 	hl
		inc 	de
		ld 		a,h
		cp 		$58
		jr		nz,LowClearScreen
		xor 	a
		out 	($FE),a
		pop 	de
		pop 	bc
		pop 	af
		ld 		hl,$0C10 							; resolution is 16x12 chars
		ld 		de,GFXPrintCharacterLowRes
		ret
;
;		Print Character E Colour D @ HL
;
GFXPrintCharacterLowRes:
		push 	af
		push 	bc
		push 	de
		push 	hl
		push 	ix

		ld 		b,e 								; save character in B
		ld 		a,e
		and 	$7F
		cp 		32
		jr 		c,__LPExit

		add 	hl,hl
		add 	hl,hl
		ld	 	a,h 								; check in range 192*4 = 768
		cp 		3
		jr 		nc,__LPExit

		ld 		a,d 								; only lower 3 bits of colour
		and 	7
		ld 		c,a 								; C is foreground

		push 	hl
		ld 		a,b 								; get char back
		ld 		b,0 								; B = no flip colour.
		bit 	7,a
		jr 		z,__LowNotReverse 					; but 7 set, flip is $FF
		dec 	b
__LowNotReverse:
		and 	$7F 								; offset from space
		sub 	$20
		ld 		l,a 								; put into HL
		ld 		h,0
		add 	hl,hl 								; x 8
		add 	hl,hl
		add 	hl,hl

		push 	hl 									; transfer to IX
		pop 	ix

		push 	bc 									; add the font base to it.
		ld 		bc,(SIFontBase)
		add 	ix,bc
		pop 	bc
		pop 	hl
		ex 		de,hl
		ld 		a,e 								; put DE => HL
		and 	192 								; these are part of Y
		ld 		l,a  								; Y multiplied by 4 then 32 = 128
		ld 		h,d
		add 	hl,hl
		add 	hl,hl
		add 	hl,hl
		add 	hl,hl
		set 	6,h 								; put into $4000 range

		ld 		a,15*4 								; mask for X, which has been premultiplied.
		and 	e 									; and with E, gives X position
		add 	a,a 								; now multiplied by 8.
		ld 		e,a 								; DE is x offset.
		ld 		d,0

		add 	hl,de
		ld 		a,h
		cp 		$58 								; need to be shifted to 2nd chunk ?
		jr 		c,__LowNotLower2
		ld 		de,$0800
		add 	hl,de
__LowNotLower2:
		ld 		e,8 								; do 8 rows
__LowOuter:
		push 	hl 									; save start
		ld 		d,8 								; do 8 columns
		ld 		a,(ix+0) 							; get the bit pattern
		xor 	b
		inc 	ix
__LowLoop:
		ld 		(hl),0 								; background
		add 	a,a 								; shift pattern left
		jr 		nc,__LowNotSet
		ld 		(hl),c 								; if MSB was set, overwrite with fgr
__LowNotSet:
		inc 	l
		dec 	d 									; do a row
		jr 		nz,	__LowLoop
		pop 	hl 									; restore, go 256 bytes down.
		push 	de
		ld 		de,128
		add 	hl,de
		pop 	de
		dec 	e 									; do 8 rows
		jr 		nz,__LowOuter
__LPExit:
		pop 	ix
		pop 	hl
		pop 	de
		pop 	bc
		pop 	af
		ret

; *********************************************************************************
; *********************************************************************************
;
;		File:		keyboard.asm
;		Purpose:	Spectrum Keyboard Interface
;		Date : 		27th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

link9:
    dw link10-link9
 	db "inkey",1
		call 	IOScanKeyboard 						; read keyboard
		ld 		(hl),a 								; copy into variable
		inc 	hl
		ld 		(hl),$00	 						; zero upper byte.
		ret

; *********************************************************************************
;
;			Scan the keyboard, return currently pressed key code in A
;
; *********************************************************************************

IOScanKeyboard:
		push 	bc
		push 	de
		push 	hl

		ld 		hl,__kr_no_shift_table 				; firstly identify shift state.

		ld 		c,$FE 								; check CAPS SHIFT (emulator : left shift)
		ld 		b,$FE
		in 		a,(c)
		bit 	0,a
		jr 		nz,__kr1
		ld 		hl,__kr_shift_table
		jr 		__kr2
__kr1:
		ld 		b,$7F 								; check SYMBOL SHIFT (emulator : right shift)
		in 		a,(c)
		bit 	1,a
		jr 		nz,__kr2
		ld 		hl,__kr_symbol_shift_table
__kr2:

		ld 		e,$FE 								; scan pattern.
__kr3:	ld 		a,e 								; work out the mask, so we don't detect shift keys
		ld 		d,$1E 								; $FE row, don't check the least significant bit.
		cp 		$FE
		jr 		z,___kr4
		ld 		d,$01D 								; $7F row, don't check the 2nd least significant bit
		cp 		$7F
		jr 		z,___kr4
		ld 		d,$01F 								; check all bits.
___kr4:
		ld 		b,e 								; scan the keyboard
		ld 		c,$FE
		in 		a,(c)
		cpl 										; make that active high.
		and 	d  									; and with check value.
		jr 		nz,__kr_keypressed 					; exit loop if key pressed.

		inc 	hl 									; next set of keyboard characters
		inc 	hl
		inc 	hl
		inc 	hl
		inc 	hl

		ld 		a,e 								; get pattern
		add 	a,a 								; shift left
		or 		1 									; set bit 1.
		ld 		e,a

		cp 		$FF 								; finished when all 1's.
		jr 		nz,__kr3
		xor 	a
		jr 		__kr_exit 							; no key found, return with zero.
;
__kr_keypressed:
		inc 	hl  								; shift right until carry set
		rra
		jr 		nc,__kr_keypressed
		dec 	hl 									; undo the last inc hl
		ld 		a,(hl) 								; get the character number.
__kr_exit:
		pop 	hl
		pop 	de
		pop 	bc
		ret

; *********************************************************************************
;	 						Keyboard Mapping Tables
; *********************************************************************************
;
;	$FEFE-$7FFE scan, bit 0-4, active low
;
;	3:Abort (Shift+Q) 8:Backspace 13:Return
;	27:Break 32-127: Std ASCII all L/C
;
__kr_no_shift_table:
		db 		0,  'z','x','c','v',			'a','s','d','f','g'
		db 		'q','w','e','r','t',			'1','2','3','4','5'
		db 		'0','9','8','7','6',			'p','o','i','u','y'
		db 		13, 'l','k','j','h',			' ', 0, 'm','n','b'

__kr_shift_table:
__kr_symbol_shift_table:
		db 		 0, ':', 0,  '?','/',			'~','|','\','{','}'
		db 		 3,  0,  0  ,'<','>',			'!','@','#','$','%'
		db 		'_',')','(',"'",'&',			'"',';', 0, ']','['
		db 		27, '=','+','-','^',			' ', 0, '.',',','*'

		db 		0,  ':',0  ,'?','/',			'~','|','\','{','}'
		db 		3,  0,  0  ,'<','>',			16,17,18,19,20
		db 		8, ')',23,  22, 21,				'"',';', 0, ']','['
		db 		27, '=','+','-','^',			' ', 0, '.',',','*'
link10:
    dw 0
