<#
.SYNOPSIS
    Start the Code Yaar API (Django) and web app (Next.js) together.

.DESCRIPTION
    Runs Django on -BackendPort inside its own "Code Yaar API" window so the
    verification and password-reset emails printed by the console email backend
    stay readable, waits until /api/health/ answers, then runs `next dev` in this
    window. When the frontend stops, the API process tree is stopped with it.

    Backend CORS and FRONTEND_URL are derived from the actual ports being used,
    so `localhost` and `127.0.0.1` on either side always match and the browser
    never blocks a request as an opaque "Failed to fetch".

.PARAMETER BackendPort
    Port for the Django API. Default 8000.

.PARAMETER FrontendPort
    Port for the Next.js dev server. Default 3000.

.PARAMETER Setup
    Install Python and npm dependencies before starting (first run / after
    pulling dependency changes).

.PARAMETER Force
    Stop whatever already holds the API/app ports — including an orphaned
    'Code Yaar API' window from an earlier run or a server started by hand —
    instead of refusing. Without -Force the launcher only reclaims its own
    orphaned windows and otherwise names the occupying process.

.EXAMPLE
    .\scripts\dev.ps1

.EXAMPLE
    .\scripts\dev.ps1 -Setup

.EXAMPLE
    .\scripts\dev.ps1 -Force

.EXAMPLE
    .\scripts\dev.ps1 -BackendPort 8001 -FrontendPort 3001
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000,
    [switch]$Setup,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot 'backend'
$frontendDir = Join-Path $repoRoot 'frontend'
$apiUrl = "http://localhost:$BackendPort/api"
$appUrl = "http://localhost:$FrontendPort"

function Write-Step([string]$Message) { Write-Host "==> $Message" -ForegroundColor Cyan }
function Write-Note([string]$Message) { Write-Host "    $Message" -ForegroundColor DarkGray }
function Write-Warn([string]$Message) { Write-Host "WARN: $Message" -ForegroundColor Yellow }
function Stop-WithError([string]$Message) {
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

# Runs a native executable and fails loudly instead of silently continuing.
function Invoke-Checked([string]$Executable, [string[]]$Arguments, [string]$What) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { Stop-WithError "$What failed (exit code $LASTEXITCODE)." }
}

# A connect attempt is the reliable "is something listening?" test here;
# Get-NetTCPConnection can report an empty result for a live listener.
function Test-PortOpen([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $pending = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $pending.AsyncWaitHandle.WaitOne(300)) { return $false }
        $client.EndConnect($pending)
        return $true
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

# Describes whatever is listening on a port, or $null when the port is free.
function Get-PortOwner([int]$Port) {
    if (-not (Test-PortOpen $Port)) { return $null }
    $connection = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $connection) { return 'another process' }
    $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
    if (-not $process) { return "pid $($connection.OwningProcess)" }
    return "$($process.ProcessName) (pid $($process.Id))"
}

# The browser needs an Access-Control-Allow-Origin header for the exact app
# origin; without it every request surfaces as an opaque "Failed to fetch".
function Test-CorsOrigin([string]$Origin) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/auth/login/" `
            -Method Options -UseBasicParsing -Headers @{
                Origin                          = $Origin
                'Access-Control-Request-Method' = 'POST'
            }
        return ([string]$response.Headers['Access-Control-Allow-Origin']).Trim() -eq $Origin
    } catch {
        return $false
    }
}

# runserver's autoreloader runs the server in child processes, so stopping it
# must follow the tree and cannot rely on the parent window closing itself.
function Get-ChildProcesses([int]$ProcessId) {
    Get-CimInstance Win32_Process -Filter "ParentProcessId = $ProcessId" -ErrorAction SilentlyContinue
}

function Stop-ProcessTree([int]$ProcessId) {
    foreach ($child in @(Get-ChildProcesses $ProcessId)) {
        Stop-ProcessTree -ProcessId ([int]$child.ProcessId)
    }
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
}

# Walks up from a process to the root of its call chain while each parent is
# part of that same chain (the predicate holds). For Django this lands on the
# outer `manage.py runserver` process: killing anything below it only makes
# the parent re-spawn the child on the port immediately.
function Find-ChainRoot([int]$ProcessId, [scriptblock]$InChain) {
    $current = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
    $depth = 0
    while ($current -and $current.ParentProcessId -and $depth -lt 20) {
        $parent = Get-CimInstance Win32_Process -Filter "ProcessId = $($current.ParentProcessId)" -ErrorAction SilentlyContinue
        if (-not $parent -or -not (& $InChain $parent)) { break }
        $current = $parent
        $depth++
    }
    return $current
}

# One dev.ps1 run is one API window; PIDs are recorded so the finally block
# always reaches it, even if the returned process object went stale.
$script:apiWindowPids = @()

# Stops the 'Code Yaar API' windows an earlier dev.ps1 launched (and a crash
# or a killed terminal left behind): only windows carrying this launcher's
# console title signature are touched. A server started by hand is not.
function Stop-StaleApiWindows {
    $stale = @(Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like '*Code Yaar API*' } |
        Sort-Object ProcessId -Unique)
    foreach ($window in $stale) {
        Write-Note "stopping leftover 'Code Yaar API' window pid $($window.ProcessId)"
        Stop-ProcessTree -ProcessId ([int]$window.ProcessId)
    }
    return ($stale.Count -gt 0)
}

function Wait-ForApi([string]$Url, [int]$TimeoutSeconds = 60) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { return $true }
        } catch {
            # not listening yet
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

# Copies a template env file into place when the real one is missing.
function Initialize-EnvFile([string]$Directory, [string]$Target, [string]$Template) {
    $targetPath = Join-Path $Directory $Target
    $templatePath = Join-Path $Directory $Template
    if (-not (Test-Path $targetPath) -and (Test-Path $templatePath)) {
        Copy-Item $templatePath $targetPath
        Write-Note "created $Target from $Template"
    }
}

# ── Pre-flight: ports ───────────────────────────────────────────────────────
if ($BackendPort -eq $FrontendPort) {
    Stop-WithError 'the API and the app cannot share a port; pass -FrontendPort.'
}
# A dev.ps1 API window that survived a crash blocks the port forever; those
# windows are always reclaimed. With -Force, any other listener (for example a
# hand-started runserver) is stopped too; without it the launcher refuses and
# says who holds the port.
Stop-StaleApiWindows | Out-Null
foreach ($port in @($BackendPort, $FrontendPort)) {
    $owner = Get-PortOwner $port
    if ($owner) {
        if (-not $Force) {
            Stop-WithError "port $port is already in use by $owner. Stop it (Ctrl+C in its window), re-run with -Force, or pass -BackendPort / -FrontendPort."
        }
        Write-Note "-Force: port $port is held by $owner; stopping it"
        $connection = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($connection) {
            $listenerPid = [int]$connection.OwningProcess
            $listener = Get-CimInstance Win32_Process -Filter "ProcessId = $listenerPid" -ErrorAction SilentlyContinue
            if ($listener -and $listener.CommandLine -like '*runserver*') {
                # Stop the outermost runserver of the chain (the autoreloader
                # host), never further; killing a lower level alone makes the
                # parent re-spawn a server on the port immediately.
                $rootServer = Find-ChainRoot -ProcessId $listenerPid -InChain { param($p) $p.CommandLine -like '*runserver*' }
                Stop-ProcessTree -ProcessId ([int]$rootServer.ProcessId)
            } else {
                # Not a Django server we recognise: stop just the listener and
                # its own children, never the owning terminal above it.
                Stop-ProcessTree -ProcessId $listenerPid
            }
        } else {
            # Get-NetTCPConnection can miss a live listener, so fall back to
            # runserver chains that could hold this port: processes binding an
            # explicit port must name it, and a bare 'runserver' defaults to
            # 8000. A server bound to another explicit port is never touched.
            $runserverProcs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue
            $candidates = @($runserverProcs |
                Where-Object { $_.CommandLine -like '*runserver*' } |
                Where-Object {
                    $_.CommandLine -match "runserver\s+\S*:$port(?:\s|$)" -or
                    $_.CommandLine -match 'runserver\s*("?\s|$)'
                })
            $stoppedRoots = @()
            foreach ($candidate in $candidates) {
                $rootServer = Find-ChainRoot -ProcessId ([int]$candidate.ProcessId) -InChain { param($p) $p.CommandLine -like '*runserver*' }
                if ($stoppedRoots -notcontains $rootServer.ProcessId) {
                    $stoppedRoots += $rootServer.ProcessId
                    Stop-ProcessTree -ProcessId ([int]$rootServer.ProcessId)
                }
            }
        }
        # Give the socket a moment to be released before the retry below.
        Start-Sleep -Milliseconds 500
        $owner = Get-PortOwner $port
        if ($owner) {
            Stop-WithError "port $port is still in use by $owner after -Force stopped it. Stop it by hand and rerun."
        }
    }
}

# ── Pre-flight: interpreters, env files, dependencies ───────────────────────
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        Stop-WithError 'Python was not found. Create the virtualenv first: python -m venv .venv'
    }
    $python = $pythonCommand.Source
    Write-Warn 'using the global Python; create .venv to isolate dependencies (python -m venv .venv).'
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCommand) { $npmCommand = Get-Command npm -ErrorAction SilentlyContinue }
if (-not $npmCommand) { Stop-WithError 'npm was not found. Install Node.js and reopen the terminal.' }
$npm = $npmCommand.Source

Initialize-EnvFile $backendDir '.env' '.env.example'
Initialize-EnvFile $frontendDir '.env.local' '.env.example'

if ($Setup) {
    Write-Step 'Installing backend dependencies'
    Invoke-Checked $python @('-m', 'pip', 'install', '-r', (Join-Path $backendDir 'requirements.txt')) 'pip install'
}

if (-not (Test-Path (Join-Path $frontendDir 'node_modules'))) {
    Write-Step 'Installing frontend dependencies'
    Push-Location $frontendDir
    try { Invoke-Checked $npm @('install') 'npm install' } finally { Pop-Location }
}

# The API must be reachable from the exact origin the browser uses. Both
# hostnames are separate origins, so both are allowed.
$env:ALLOWED_ORIGINS = "http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort"
$env:FRONTEND_URL = $appUrl
$env:BACKEND_URL = "http://127.0.0.1:$BackendPort"

$envLocal = Join-Path $frontendDir '.env.local'
$configuredApi = $null
if (Test-Path $envLocal) {
    $apiMatch = Select-String -Path $envLocal -Pattern '^\s*NEXT_PUBLIC_API_URL\s*=\s*(.+)$' -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($apiMatch) { $configuredApi = $apiMatch.Matches[0].Groups[1].Value.Trim() }
}
if (-not $configuredApi) {
    $env:NEXT_PUBLIC_API_URL = $apiUrl
    Write-Note "NEXT_PUBLIC_API_URL not set; using $apiUrl"
} elseif ($configuredApi -notmatch ":$BackendPort(/|$)") {
    Write-Warn ".env.local points the frontend at $configuredApi but the API starts on port $BackendPort."
    Write-Warn "update frontend/.env.local, or run: .\scripts\dev.ps1 -BackendPort <port from $configuredApi>"
}

Write-Step 'Applying database migrations'
Push-Location $backendDir
try {
    Invoke-Checked $python @('manage.py', 'check') 'manage.py check'
    Invoke-Checked $python @('manage.py', 'migrate', '--noinput') 'database migration'
} finally {
    Pop-Location
}

# ── Start the API in its own window ─────────────────────────────────────────
$startedAt = (Get-Date).AddSeconds(-2)
Write-Step "Starting the API on http://127.0.0.1:$BackendPort"
# Kept in a separate console so console-backend emails (verification and reset
# links) are visible, and so a traceback is readable instead of scrolling away.
$apiCommand = "`$Host.UI.RawUI.WindowTitle = 'Code Yaar API'; & '$python' 'manage.py' 'runserver' '127.0.0.1:$BackendPort'"
$apiProcess = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList "-NoLogo -NoExit -Command `"$apiCommand`"" `
    -WorkingDirectory $backendDir -PassThru
$script:apiWindowPids += $apiProcess.Id

try {
    if (-not (Wait-ForApi -Url "http://127.0.0.1:$BackendPort/api/health/")) {
        Stop-WithError "the API did not answer on http://127.0.0.1:$BackendPort/api/health/. Read the 'Code Yaar API' window for the traceback."
    }
    Write-Note 'API healthy'
    foreach ($origin in @("http://localhost:$FrontendPort", "http://127.0.0.1:$FrontendPort")) {
        if (-not (Test-CorsOrigin $origin)) {
            Write-Warn "the API sent no Access-Control-Allow-Origin header for $origin"
            Write-Warn 'requests from the app would fail as "Failed to fetch"; check ALLOWED_ORIGINS in backend/.env'
        }
    }

    Write-Host ''
    Write-Host '  App     ' -NoNewline; Write-Host "$appUrl" -ForegroundColor Green
    Write-Host '  API     ' -NoNewline; Write-Host "$apiUrl/" -ForegroundColor Green
    Write-Host '  Admin   ' -NoNewline; Write-Host "http://127.0.0.1:$BackendPort/admin/" -ForegroundColor Green
    Write-Host '  Health  ' -NoNewline; Write-Host "http://127.0.0.1:$BackendPort/api/health/" -ForegroundColor Green
    Write-Host ''
    Write-Note "verification and reset emails print in the 'Code Yaar API' window"
    Write-Note 'press Ctrl+C here to stop both servers'
    Write-Host ''

    Push-Location $frontendDir
    try {
        & $npm 'run' 'dev' '--' '-p' $FrontendPort
    } finally {
        Pop-Location
    }
} finally {
    Write-Step 'Stopping the API'
    # The window runs with -NoExit and Django's autoreloader re-spawns its
    # server child whenever it is killed alone, so the whole tree of every
    # window this run launched must be stopped, window included.
    foreach ($windowPid in $script:apiWindowPids) {
        Stop-ProcessTree -ProcessId ([int]$windowPid)
    }
    # Ctrl+C does not always unwind a pipeline cleanly in Windows PowerShell,
    # so any window still carrying this run's API title is stopped as well.
    Stop-StaleApiWindows | Out-Null
}
