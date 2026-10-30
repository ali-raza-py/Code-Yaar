try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health/' -UseBasicParsing -TimeoutSec 3
    Write-Host ("HEALTH OK " + $r.StatusCode + " " + $r.Content)
} catch {
    Write-Host ("HEALTH FAIL: " + $_.Exception.Message)
}

Write-Host "--- runserver / python processes ---"
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*runserver*' } |
    ForEach-Object { Write-Host ("PID " + $_.ProcessId + " ppid " + $_.ParentProcessId + " started " + $_.CreationDate + "  " + $_.CommandLine) }

Write-Host "--- api windows ---"
Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*Code Yaar API*' } |
    ForEach-Object { Write-Host ("PID " + $_.ProcessId + " ppid " + $_.ParentProcessId) }

Write-Host "--- dev.ps1 running ---"
Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*dev.ps1*' } |
    ForEach-Object { Write-Host ("PID " + $_.ProcessId + "  " + $_.CommandLine) }

Write-Host "--- port 3000 probe ---"
$client = New-Object System.Net.Sockets.TcpClient
try {
    $pending = $client.BeginConnect('127.0.0.1', 3000, $null, $null)
    if ($pending.AsyncWaitHandle.WaitOne(400)) { Write-Host 'PORT 3000: open' } else { Write-Host 'PORT 3000: closed' }
} catch { Write-Host 'PORT 3000: closed' } finally { $client.Close() }
