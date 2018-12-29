; ***************************************************************************************
; ***************************************************************************************
;
;		Name : 		data.asm
;		Author :	Paul Robson (paul@robsons.org.uk)
;		Date : 		27th December 2018
;		Purpose :	Data area
;
; ***************************************************************************************
; ***************************************************************************************

; ***************************************************************************************
;
;								System Information
;
; ***************************************************************************************

SystemInformation:

Here:												; +0 	Here 
		dw 		FreeMemory
HerePage: 											; +2	Here.Page
		db 		FirstCodePage,0
NextFreePage: 										; +4 	Next available code page (2 8k pages/page)
		db 		FirstCodePage+2,0,0,0
DisplayInfo: 										; +8 	Display information
		dw 		DisplayInformation,0		
StartAddress: 										; +12 	Start Address
		dw 		__KernelHalt
StartAddressPage: 									; +14 	Start Page
		db 		FirstCodePage,0

; ***************************************************************************************
;
;							 Display system information
;
; ***************************************************************************************

DisplayInformation:

SIScreenWidth: 										; +0 	screen width
		db 		0,0,0,0
SIScreenHeight:										; +4 	screen height
		db 		0,0,0,0
SIScreenSize:										; +8 	screen size
		db 		0,0,0,0
SIFontBase:											; +12 	font in use
		dw 		AlternateFont,0
SIScreenDriver:										; +16 	currently selected screen driver
		dw 		0,0

FreeMemory:		
