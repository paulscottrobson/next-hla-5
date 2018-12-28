@echo off
python ..\scripts\makecore.py core graphics.layer2
..\bin\snasm __core.asm boot.img


