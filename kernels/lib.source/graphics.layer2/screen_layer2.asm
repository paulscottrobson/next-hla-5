; *********************************************************************************
; *********************************************************************************
;
;		File:		screen_layer2.asm
;		Purpose:	Layer 2 console interface, sprites enabled, no shadow.
;		Date : 		27th December 2018
;		Author:		paul@robsons.org.uk
;
; *********************************************************************************
; *********************************************************************************

; *********************************************************************************
;
;								Clear Layer 2 Display.
;
; *********************************************************************************


GFXInitialise:
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
		ld 		d,l 								; D = 0, slightly quicker.
L2PClearBank: 										; assume default palette :)
		dec 	hl
		ld 		(hl),d
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
		ret
;
;		Print Character E, colour D, position HL
;
GFXCharacterHandler:
		push 	af
		push 	bc
		push 	de
		push 	hl
		push 	ix

		ld 		b,e 								; save A temporarily
		ld 		a,b

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
		pop 	af 									; restore char

		call 	GFXGetFontGraphicDE 				; font offset in DE
		push 	de 									; transfer to IX
		pop 	ix

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
		inc 	ix
		or 		a
		jr 		z,__L2Blank
__L2Loop:
		ld 		(hl),0 								; background
		add 	a,a 								; shift pattern left
		jr 		nc,__L2NotSet
		ld 		(hl),c 								; if MSB was set, overwrite with fgr
__L2NotSet:
		inc 	hl
		dec 	d 									; do a row
		jr 		nz,	__L2Loop
		jr 		__L2Exit1
__L2Blank:
		xor 	a
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
		inc 	hl
		ld 		(hl),a
__L2Exit1:
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
