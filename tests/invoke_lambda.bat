@echo off
set FUNCTION_NAME=NiceHomeAssignmentStack-ListObjectsFunctionsE890FF-S6HjLuTHN2zQ

aws lambda invoke ^
  --function-name %FUNCTION_NAME% ^
  --cli-binary-format raw-in-base64-out ^
  --payload file://event.json ^
  output.json >nul

type output.json