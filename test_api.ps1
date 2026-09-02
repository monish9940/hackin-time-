# CareBridge AI - Final API Acceptance Tests
$ErrorActionPreference = "Continue"

# Test 1: API Health
Write-Host '=== TEST 1: API Health ===' -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri 'http://localhost:8000/' -Method GET
    Write-Host 'PASS: API is up -' $health.message -ForegroundColor Green
} catch {
    Write-Host 'FAIL: API health check -' $_.Exception.Message -ForegroundColor Red
}

# Test 2: Register new user
Write-Host ''
Write-Host '=== TEST 2: Register New User ===' -ForegroundColor Cyan
$registerBody = @{
    full_name = 'Dr. Test Clinician'
    email = 'testclinician@carebridge.com'
    password = 'TestPassword123!'
    confirm_password = 'TestPassword123!'
    organization = 'Test Hospital'
    specialization = 'Cardiology'
    role = 'Clinician'
} | ConvertTo-Json

try {
    $registerResp = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/register' -Method POST -Body $registerBody -ContentType 'application/json'
    Write-Host 'PASS: User registered successfully' -ForegroundColor Green
    Write-Host '  ID:' $registerResp.id
    Write-Host '  Name:' $registerResp.full_name
    Write-Host '  Email:' $registerResp.email
    Write-Host '  Role:' $registerResp.role
    Write-Host '  Organization:' $registerResp.organization
} catch {
    $errBody = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($errBody.detail -like '*already registered*') {
        Write-Host 'INFO: User already registered (acceptable - continuing to login test)' -ForegroundColor Yellow
    } else {
        Write-Host 'FAIL: Registration -' $_.Exception.Message -ForegroundColor Red
        Write-Host '  Detail:' $errBody.detail
    }
}

# Test 3: Login
Write-Host ''
Write-Host '=== TEST 3: Login with Real User ===' -ForegroundColor Cyan
$loginBody = @{
    email = 'testclinician@carebridge.com'
    password = 'TestPassword123!'
} | ConvertTo-Json

$token = $null
try {
    $loginResp = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' -Method POST -Body $loginBody -ContentType 'application/json'
    Write-Host 'PASS: Login successful' -ForegroundColor Green
    Write-Host '  Token type:' $loginResp.token_type
    $tokenPreview = $loginResp.access_token.Substring(0, [Math]::Min(40, $loginResp.access_token.Length))
    Write-Host '  Token (preview):' "$tokenPreview..."
    Write-Host '  User name:' $loginResp.user.full_name
    $token = $loginResp.access_token
} catch {
    Write-Host 'FAIL: Login -' $_.Exception.Message -ForegroundColor Red
}

# Test 4: Protected route (GET /me with token)
Write-Host ''
Write-Host '=== TEST 4: Protected Route (/api/auth/me with JWT) ===' -ForegroundColor Cyan
if ($token) {
    try {
        $headers = @{ Authorization = "Bearer $token" }
        $me = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/me' -Method GET -Headers $headers
        Write-Host 'PASS: Protected endpoint returns user data' -ForegroundColor Green
        Write-Host '  Email:' $me.email
        Write-Host '  Full Name:' $me.full_name
    } catch {
        Write-Host 'FAIL: Protected route -' $_.Exception.Message -ForegroundColor Red
    }
} else {
    Write-Host 'SKIP: No token (login failed)' -ForegroundColor Yellow
}

# Test 5: Wrong password (should fail 401)
Write-Host ''
Write-Host '=== TEST 5: Wrong Password Should Return 401 ===' -ForegroundColor Cyan
$wrongBody = @{ email = 'testclinician@carebridge.com'; password = 'wrongpassword' } | ConvertTo-Json
try {
    $wrong = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' -Method POST -Body $wrongBody -ContentType 'application/json'
    Write-Host 'FAIL: Should have returned 401 but got 200' -ForegroundColor Red
} catch {
    $status = $_.Exception.Response.StatusCode
    if ($status -eq 401) {
        Write-Host 'PASS: Wrong password correctly rejected with 401' -ForegroundColor Green
    } else {
        Write-Host "INFO: Got status $status" -ForegroundColor Yellow
    }
}

# Test 6: Unauthenticated access to patients (should fail 401)
Write-Host ''
Write-Host '=== TEST 6: Unauthenticated Access to /api/patients/ ===' -ForegroundColor Cyan
try {
    $pats = Invoke-RestMethod -Uri 'http://localhost:8000/api/patients/' -Method GET
    Write-Host 'FAIL: Should have returned 401 but got 200' -ForegroundColor Red
} catch {
    $status = $_.Exception.Response.StatusCode
    if ($status -eq 401) {
        Write-Host 'PASS: Unauthenticated access correctly rejected with 401' -ForegroundColor Green
    } else {
        Write-Host "INFO: Got status $status" -ForegroundColor Yellow
    }
}

# Test 7: Authenticated patients list
Write-Host ''
Write-Host '=== TEST 7: Authenticated Access to /api/patients/ ===' -ForegroundColor Cyan
if ($token) {
    try {
        $authHeaders = @{ Authorization = "Bearer $token" }
        $patients = Invoke-RestMethod -Uri 'http://localhost:8000/api/patients/?skip=0&limit=10' -Method GET -Headers $authHeaders
        Write-Host 'PASS: Patients endpoint accessible with valid JWT' -ForegroundColor Green
        Write-Host '  Patient count:' $patients.Count
    } catch {
        Write-Host 'FAIL: Patients endpoint -' $_.Exception.Message -ForegroundColor Red
    }
} else {
    Write-Host 'SKIP: No token (login failed)' -ForegroundColor Yellow
}

Write-Host ''
Write-Host '==========================================' -ForegroundColor Cyan
Write-Host '=== ALL ACCEPTANCE TESTS COMPLETE ===' -ForegroundColor Cyan
Write-Host '==========================================' -ForegroundColor Cyan
