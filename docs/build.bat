@echo off
REM Example batch file that converts Markdown files to HTML
REM using PANDOC (must be present in the system) and its default HTML template.

SET PANDOC=pandoc --standalone --variable=maxwidth:50em

%PANDOC% .\manual_eng.md -o  .\manual_eng.html --metadata title="Tixel"
%PANDOC% .\manual_esp.md -o  .\manual_esp.html --metadata title="Tixel"

@echo on
