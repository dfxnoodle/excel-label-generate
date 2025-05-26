@echo off
REM Change to the directory where this batch file is located (project root)
cd /D "%~dp0"

REM Execute PowerShell to activate the venv, run the Python script, and then exit PowerShell
REM This ensures that the python command runs within the activated environment and PowerShell closes afterwards.
powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "& { . .\venv\Scripts\Activate.ps1; python .\src\gui.py; exit }"

REM Optional: Pause to see any output if the script window closes quickly
REM pause
