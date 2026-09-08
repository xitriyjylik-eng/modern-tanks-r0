@echo off
if "%GDK_WIN%"=="" (
  echo ERROR: GDK_WIN is not set to the SGDK root.
  exit /b 2
)
if not exist "%GDK_WIN%\makefile.gen" (
  echo ERROR: %GDK_WIN%\makefile.gen not found.
  exit /b 2
)
cd /d "%~dp0"
"%GDK_WIN%\bin\make" -f "%GDK_WIN%\makefile.gen" clean || exit /b 1
"%GDK_WIN%\bin\make" -f "%GDK_WIN%\makefile.gen" || exit /b 1
if not exist "out\rom.bin" exit /b 1
echo R0 build complete: out\rom.bin
