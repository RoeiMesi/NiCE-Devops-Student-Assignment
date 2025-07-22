param(
  [string]$FunctionName = "NiceHomeAssignmentStack-ListObjectsFunctionsE890FF-S6HjLuTHN2zQ"
)

# Invoke the Lambda and suppress CLI output
aws lambda invoke `
  --function-name $FunctionName `
  --cli-binary-format raw-in-base64-out `
  --payload file://tests/event.json `
  response.json | Out-Null

# Print the response
Write-Host "Response from $FunctionName:"
Get-Content response.json
