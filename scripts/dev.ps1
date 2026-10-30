<#
.SYNOPSIS
    Start the Code Yaar API (Django) and web app (Next.js) together.

.DESCRIPTION
    Runs Django on -BackendPort inside its own "Code Yaar API" window so
    tracebacks, mail warnings and — when the console email backend is configured
    — the verification and password-reset emails stay readable, waits until
    /api/health/ answers, then runs `next dev` in this window. When the frontend
    stops, the API process tree is stopped with it.

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

# PID of the process listening on a port, or 0. Get-NetTCPConnection can
# return nothing for a live listener, so netstat is the second opinion.
function Get-PortOwnerPid([int]$Port) {
    $connection = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($connection) { return [int]$connection.OwningProcess }
    $line = netstat -ano -p tcp |
        Where-Object { $_ -match "^\s*TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$" } |
        Select-Object -First 1
    if ($line -and $line -match "LISTENING\s+(\d+)") { return [int]$Matches[1] }
    return 0
}

# Describes whatever is listening on a port, or $null when the port is free.
function Get-PortOwner([int]$Port) {
    if (-not (Test-PortOpen $Port)) { return $null }
    $ownerPid = Get-PortOwnerPid $Port
    if ($ownerPid -eq 0) { return 'another process' }
    $process = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
    if (-not $process) { return "pid $ownerPid" }
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

# The banner used to promise that verification emails appear in the API window.
# That is only true for the console backend; with SMTP configured the mail
# leaves the machine and the window shows nothing, so the hint reports the
# transport backend/.env actually resolves to. Never echo the password.
function Get-MailDeliveryHint {
    $envFile = Join-Path $backendDir '.env'
    $values = @{}
    if (Test-Path $envFile) {
        foreach ($line in @(Get-Content $envFile -ErrorAction SilentlyContinue)) {
            if ($line -match '^\s*([A-Z0-9_]+)\s*=\s*(.*)$') {
                $values[$Matches[1]] = $Matches[2].Trim().Trim('"').Trim("'")
            }
        }
    }
    $backend = $values['EMAIL_BACKEND']
    if (-not $backend) { return 'EMAIL_BACKEND is unset in backend/.env; auth emails will not send' }
    if ($backend -match 'console') {
        return "verification and reset emails print in the 'Code Yaar API' window (console backend; nothing is delivered)"
    }
    if ($backend -match 'smtp') {
        if (-not $values['EMAIL_HOST_PASSWORD']) {
            return 'SMTP is selected but EMAIL_HOST_PASSWORD is empty in backend/.env; no email can be sent'
        }
        # PS 5.1 has no null-coalescing operator, so pick the sender explicitly.
        $sender = $values['DEFAULT_FROM_EMAIL']
        if (-not $sender) { $sender = $values['EMAIL_HOST_USER'] }
        if (-not $sender) { $sender = 'the configured sender' }
        return "verification and reset emails are sent over SMTP as $sender; test with: python manage.py mail_check <address>"
    }
    return "auth emails use $backend"
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
# always reaches it, even if Start-Process's returned process went stale.
$script:apiWindowPids = @()

# The API window records the PID of the dev.ps1 run that spawned it, so a later
# run can tell its own orphaned windows (launcher gone: safe to stop, otherwise
# the port stays blocked) from the window of a launcher that is still running
# (never touched - that session is simply in use, and the port check says so).
function Get-WindowLauncherPid($Window) {
    $match = [regex]::Match([string]$Window.CommandLine, "CODE_YAAR_LAUNCHER\s*=\s*'?([0-9]+)'?")
    if (-not $match.Success) { return 0 }
    return [int]$match.Groups[1].Value
}

# Stops the API windows this launcher tagged and waits until the sockets are
# free: Windows can hold a listening socket for a moment after the owner dies,
# and a killed server's autoreloader can re-spawn a worker in between, so the
# sweep repeats until the port answers nothing or the deadline passes.
function Stop-TaggedApiWindows([int]$LauncherPid) {
    $deadline = (Get-Date).AddSeconds(10)
    while ((Get-Date) -lt $deadline) {
        $windows = @(Get-LaunchedApiWindows -LauncherPid $LauncherPid)
        $portOpen = (Test-PortOpen $BackendPort) -or (Test-PortOpen $FrontendPort)
        if ($windows.Count -eq 0 -and -not $portOpen) { return }
        foreach ($window in $windows) {
            Stop-ProcessTree -ProcessId ([int]$window.ProcessId)
        }
        Start-Sleep -Milliseconds 250
    }
}

# All windows tagged by *this* launcher, used by the finally block: the
# launcher is still alive there, so 'launcher dead' alone would miss them.
function Get-LaunchedApiWindows([int]$LauncherPid) {
    Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like '*WindowTitle*' -and (Get-WindowLauncherPid $_) -eq $LauncherPid }
}

# Stops the API windows left behind by launchers that are no longer running
# (a crash or a closed terminal): their port would otherwise stay blocked.
function Stop-OrphanedApiWindows {
    $orphans = @()
    $windows = Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" -ErrorAction SilentlyContinue
    foreach ($window in @($windows | Where-Object { $_.CommandLine -like '*WindowTitle*' })) {
        $launcherPid = Get-WindowLauncherPid $window
        if ($launcherPid -eq 0) { continue }
        if (Get-Process -Id $launcherPid -ErrorAction SilentlyContinue) { continue }
        $orphans += $window
    }
    foreach ($launcherPid in @($orphans | ForEach-Object { Get-WindowLauncherPid $_ } | Sort-Object -Unique)) {
        Write-Note "stopping orphaned 'Code Yaar API' window of dead launcher $launcherPid"
        Stop-TaggedApiWindows -LauncherPid ([int]$launcherPid)
    }
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

# All ancestors of this launcher. -Force may stop a listener, but never one
# that is a child of this very terminal: stopping that tree would kill the
# session the user is typing in, so such a server must be stopped by hand.
$script:launcherChain = @($PID)
$ancestor = Get-CimInstance Win32_Process -Filter "ProcessId = $PID" -ErrorAction SilentlyContinue
while ($ancestor -and $ancestor.ParentProcessId -and $ancestor.ParentProcessId -ne 0) {
    $ancestor = Get-CimInstance Win32_Process -Filter "ProcessId = $($ancestor.ParentProcessId)" -ErrorAction SilentlyContinue
    if (-not $ancestor) { break }
    $script:launcherChain += [int]$ancestor.ProcessId
    if ($script:launcherChain.Count -gt 20) { break }
}

# True when the process is this launcher or one of its parents.
function Test-OwnedByLauncher([int]$ProcessId) {
    return ($script:launcherChain -contains $ProcessId)
}

# ── Pre-flight: ports ───────────────────────────────────────────────────────
if ($BackendPort -eq $FrontendPort) {
    Stop-WithError 'the API and the app cannot share a port; pass -FrontendPort.'
}
# A dev.ps1 API window whose launcher died blocks the port forever; those
# orphans are always reclaimed. A window whose launcher is still running is
# another active session and is never killed. With -Force, any other listener
# (for example a hand-started runserver) is stopped too; without it the
# launcher refuses and names what holds the port.
Stop-OrphanedApiWindows
foreach ($port in @($BackendPort, $FrontendPort)) {
    $owner = Get-PortOwner $port
    if ($owner) {
        if (-not $Force) {
            if ($owner -like '*powershell*') {
                Stop-WithError "port $port is held by $owner from another dev.ps1 run whose window is still open. Press Ctrl+C in that window, or pass -BackendPort / -FrontendPort."
            }
            Stop-WithError "port $port is already in use by $owner. Stop it (Ctrl+C in its window), re-run with -Force, or pass -BackendPort / -FrontendPort."
        }
        Write-Note "-Force: port $port is held by $owner; stopping it"
        $ownerPid = Get-PortOwnerPid $port
        if ($ownerPid -ne 0 -and (Test-OwnedByLauncher $ownerPid)) {
            Stop-WithError "port $port is served by this same terminal ($owner), so -Force will not kill the window you are typing in. Press Ctrl+C there to stop that server, then rerun, or pass a free -BackendPort / -FrontendPort."
        }
        if ($ownerPid -ne 0) {
            $listenerPid = $ownerPid
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
                if ((Test-OwnedByLauncher ([int]$candidate.ProcessId)) -or (Test-OwnedByLauncher ([int]$rootServer.ProcessId))) {
                    Stop-WithError "port $port is served by this same terminal, so -Force will not kill the window you are typing in. Press Ctrl+C there to stop that server, then rerun, or pass a free -BackendPort / -FrontendPort."
                }
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
Write-Step "Starting the API on http://127.0.0.1:$BackendPort"
# Kept in a separate console so console-backend emails (verification and reset
# links) are visible, and so a traceback is readable instead of scrolling away.
# The launcher PID is written into the window's command line as a literal value
# (outer quotes, backslash-escaped) so it survives the -Command quoting; a later
# run reads it back to tell this run's orphaned windows from live sessions'.
$apiCommand = "$([char]34)`$Host.UI.RawUI.WindowTitle = 'Code Yaar API'; `$env:CODE_YAAR_LAUNCHER = '$PID'; & '$python' 'manage.py' 'runserver' '127.0.0.1:$BackendPort'$([char]34)"
$apiProcess = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList "-NoLogo -NoExit -Command $apiCommand" `
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
    Write-Note (Get-MailDeliveryHint)
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
    # window this run launched is stopped, window included. Windows are looked
    # up by this launcher's PID, not by title, so another live dev.ps1 session
    # on a different port keeps its own API window. The sweep repeats until the
    # sockets are free, so a worker re-spawned between checks is caught too.
    Stop-TaggedApiWindows -LauncherPid $PID
    foreach ($windowPid in $script:apiWindowPids) {
        Stop-ProcessTree -ProcessId ([int]$windowPid)
    }
    # Ctrl+C does not always unwind a pipeline cleanly in Windows PowerShell,
    # so a tagged window that had already dropped out of the list above is
    # reclaimed here as well. Windows of other live launchers are not touched.
    Stop-OrphanedApiWindows
}
