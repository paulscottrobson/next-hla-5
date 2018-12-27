; ***************************************************************************************
; ***************************************************************************************
;
;		Name : 		kernel.asm
;		Author :	Paul Robson (paul@robsons.org.uk)
;		Date : 		27th December 2018
;		Purpose :	Flat Forth Kernel
;
; ***************************************************************************************
; ***************************************************************************************

StackTop = $7EFC 									;      -$7EFC Top of stack
DictionaryPage = $20 								; $20 = dictionary page
FirstCodePage = $22 								; $22 = code page.

		opt 	zxnextreg
		org 	$8000 								; $8000 boot.
		jr 		Boot
		org 	$8004 								; $8004 address of sysinfo
		dw 		SystemInformation 
		org 	$8008 								; $8008 3rd parameter register
		dw 		0,0 		
		org 	$8010 								; $8010 address of words list.
		dw 	 	WordListAddress,0

Boot:	ld 		sp,StackTop							; reset Z80 Stack
		di											; disable interrupts
		db 		$ED,$91,7,2							; set turbo port (7) to 2 (14Mhz speed)
	
		ld 		a,(StartAddressPage)				; Switch to start page
		nextreg	$56,a
		inc 	a
		nextreg	$57,a
		dec 	a
		ex 		af,af'								; Set A' to current page.
		ld 		ix,(StartAddress) 					; start running address
		ld 		hl,$0000 							; clear A + B
		ld 		de,$0000
		jp 		(ix) 								; and start

__KernelHalt: 										; if boot address not set.
		jr 		__KernelHalt

AlternateFont:										; nicer font
		include "font.inc" 							; can be $3D00 here to save memory

