@echo off
For %%A in (%1) do (
	set fullpath=%%~fA
	set filename=%%~nA
)

ImageMagick-portable-x64\convert.exe %fullpath% "rsc/Face Images/%2/%filename%.png"