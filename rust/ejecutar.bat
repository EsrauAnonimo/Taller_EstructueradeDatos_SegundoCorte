@echo off
title PEA-i (Rust Consola)
cd /d "%~dp0\pea_i"
set "PATH=%USERPROFILE%\.cargo\bin;%LOCALAPPDATA%\Microsoft\WinGet\Packages\MartinStorsjo.LLVM-MinGW.MSVCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\llvm-mingw-20261006-msvcrt-x86_64\bin;%PATH%"

if exist "target\debug\pea_i.exe" (
    target\debug\pea_i.exe
) else (
    cargo run
)
pause
