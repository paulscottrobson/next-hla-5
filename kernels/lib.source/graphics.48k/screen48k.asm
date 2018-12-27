; *********************************************************************************
; *********************************************************************************
;
;		File:		screen48k.asm
;		Purpose:	Hardware interface to Spectrum display, standard but with
;					sprites enabled. 	
;		Date : 		27th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; *********************************************************************************
;
;						Call the SetMode for the Spectrum 48k 
;
; *********************************************************************************

GFXInitialise:
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
		ret

; *********************************************************************************
;
;				Write a character E on the screen at HL, in colour D
;
; *********************************************************************************

GFXCharacterHandler:
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
		ld 		a,b 								; get character
		call 	GFXGetFontGraphicDE
;
;		copy font data to screen position.
;
		ld 		a,b
		ld 		b,8 								; copy 8 characters
		ld 		c,0 								; XOR value 0
__ZXWCCopy:
		ld 		a,(de)								; get font data
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

