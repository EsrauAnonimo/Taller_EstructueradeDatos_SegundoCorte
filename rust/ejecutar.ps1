Set-Location "$PSScriptRoot\pea_i"
$llvmBin = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\MartinStorsjo.LLVM-MinGW.MSVCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\llvm-mingw-20261006-msvcrt-x86_64\bin"
$env:PATH = "$env:USERPROFILE\.cargo\bin;$llvmBin;$env:PATH"

if (Test-Path "target\debug\pea_i.exe") {
    & ".\target\debug\pea_i.exe"
} else {
    cargo run
}
