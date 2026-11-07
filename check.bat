@echo off
cd src

IF "%1"=="--notest" (
    call mypy .
) ELSE (
    call mypy .
    call python3 -m unittest -b
)

cd ..
@echo on
