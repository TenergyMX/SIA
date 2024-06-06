@echo off
@echo off
title Information about your pc
color 0A

echo.
echo    .d8888b. 8888888        d8888 
echo   d88P  Y88b  888         d88888 
echo   Y88b.       888        d88P888 
echo    "Y888b.    888       d88P 888 
echo       "Y88b.  888      d88P  888 
echo         "888  888     d88P   888 
echo   Y88b  d88P  888    d8888888888 
echo    "Y8888P" 8888888 d88P     888 
echo.
echo ==================================
echo   Obtener info de la computadora
echo ==================================
echo.

for /f "tokens=2 delims==" %%a in ('wmic computersystem get name /value') do set name=%%a
echo [ Nombre ]: %name%

for /f "tokens=2 delims==" %%a in ('wmic computersystem get manufacturer /value') do set brand=%%a
echo [ Marca ]: %brand%

for /f "tokens=2 delims==" %%a in ('wmic csproduct get name /value') do set model=%%a
echo [ Modelo ]: %model%

echo.
for /f "tokens=2 delims==" %%a in ('wmic cpu get name /value') do set cpu=%%a
echo [ Procesador ]: %cpu%

:: Obtener el número de núcleos del procesador
for /f "tokens=2 delims==" %%a in ('wmic cpu get NumberOfCores /value') do set numberOfCores=%%a
echo [ Procesador ][ nucleos ]: %numberOfCores%


rem Obtener la velocidad máxima del procesador en MHz
for /f "tokens=2 delims==" %%a in ('wmic cpu get MaxClockSpeed /value') do set clockSpeed=%%a

rem Convertir de MHz a GHz manualmente y formatear a 2 decimales
set /a ghzWholePart=clockSpeed / 1000
set /a mhzRemainder=clockSpeed %% 1000
set ghzFractionPart=%mhzRemainder:~0,1%

rem Formatear el resultado
set ghz=%ghzWholePart%.%ghzFractionPart%

rem Mostrar la velocidad en GHz
echo [ Procesador ][ Velocidad ]: %ghz% GHz


echo.
:: Obtener la memoria RAM total del sistema
for /f "tokens=2 delims==" %%a in ('wmic os get TotalVisibleMemorySize /value') do set totalMemory=%%a
set /a totalMemoryMB=totalMemory/1024
echo [ RAM ]: %totalMemory% KB - (aproximadamente %totalMemoryMB% MB)
for /f "tokens=2 delims==" %%a in ('wmic memorychip get partnumber /value ^| findstr /r /v "^$"') do (
    set "partnumber=%%a"
    goto :break
)
:break
if "%partnumber%"=="0" (
    echo [ RAM ][ Tipo ]: No se pudo obtener el tipo de memoria RAM.
) else (
    echo [ RAM ][ Tipo ]: %partnumber%
)

:: Obtener la velocidad de la memoria RAM desde PowerShell
for /f "delims=" %%a in ('powershell -command "(Get-WmiObject -Class Win32_PhysicalMemory | Select-Object -ExpandProperty Speed)[0]"') do set speed=%%a
echo [ RAM ][ Velocidad ]: %speed% MHz

echo.
for /f "tokens=2 delims==" %%a in ('wmic os get caption /value') do set caption=%%a
for /f "tokens=2 delims==" %%a in ('wmic os get version /value') do set version=%%a
echo [ SO ]: %caption%
echo [ SO ][ Version ]: %version%


echo.
echo.
pause
