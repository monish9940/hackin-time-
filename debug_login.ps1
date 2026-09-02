$body = '{"email": "testclinician@carebridge.com", "password": "TestPassword123!"}';
try {
    $resp = Invoke-WebRequest -Uri 'http://localhost:8000/api/auth/login' -Method POST -Body $body -ContentType 'application/json'
    Write-Host 'Status:' $resp.StatusCode
    Write-Host 'Body:' $resp.Content
} catch {
    Write-Host 'Status:' $_.Exception.Response.StatusCode.value__
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.BaseStream.Position = 0
    $reader.DiscardBufferedData()
    Write-Host 'Body:' $reader.ReadToEnd()
}
