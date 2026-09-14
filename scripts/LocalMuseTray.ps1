Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class LocalMuseJob {
  [StructLayout(LayoutKind.Sequential)] public struct JOBOBJECT_BASIC_LIMIT_INFORMATION { public long PerProcessUserTimeLimit; public long PerJobUserTimeLimit; public uint LimitFlags; public UIntPtr MinimumWorkingSetSize; public UIntPtr MaximumWorkingSetSize; public uint ActiveProcessLimit; public UIntPtr Affinity; public uint PriorityClass; public uint SchedulingClass; }
  [StructLayout(LayoutKind.Sequential)] public struct IO_COUNTERS { public ulong ReadOperationCount, WriteOperationCount, OtherOperationCount, ReadTransferCount, WriteTransferCount, OtherTransferCount; }
  [StructLayout(LayoutKind.Sequential)] public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION { public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation; public IO_COUNTERS IoInfo; public UIntPtr ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemoryUsed, PeakJobMemoryUsed; }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] static extern IntPtr CreateJobObject(IntPtr a, string n);
  [DllImport("kernel32.dll", SetLastError=true)] static extern bool SetInformationJobObject(IntPtr h, int c, ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION i, uint l);
  [DllImport("kernel32.dll", SetLastError=true)] public static extern bool AssignProcessToJobObject(IntPtr h, IntPtr p);
  [DllImport("kernel32.dll", SetLastError=true)] public static extern bool CloseHandle(IntPtr h);
  public static IntPtr CreateKillOnClose() { var h=CreateJobObject(IntPtr.Zero,null); var i=new JOBOBJECT_EXTENDED_LIMIT_INFORMATION(); i.BasicLimitInformation.LimitFlags=0x2000; SetInformationJobObject(h,9,ref i,(uint)Marshal.SizeOf(i)); return h; }
}
'@

$projectRoot = Split-Path -Parent $PSScriptRoot
$logRoot = Join-Path $projectRoot 'outputs\localmuse_logs'
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$servicePids = @()
$env:LOCALMUSE_TRAY_PID = [string]$PID
$jobHandle = [LocalMuseJob]::CreateKillOnClose()

function Start-LocalMuseService([string]$title, [string]$command, [string]$logName) {
    $logPath = Join-Path $logRoot $logName
    $process = Start-Process cmd.exe -WindowStyle Hidden -WorkingDirectory $projectRoot -ArgumentList '/d', '/c', "$command > `"$logPath`" 2>&1" -PassThru
    [LocalMuseJob]::AssignProcessToJobObject($jobHandle, $process.Handle) | Out-Null
    $script:servicePids += $process.Id
}

function Stop-LocalMuseTree([int]$processId) {
    & taskkill.exe /PID $processId /T /F 2>$null | Out-Null
}

function Test-Endpoint([string]$url) {
    try { Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing | Out-Null; return $true }
    catch { return $_.Exception.Response -ne $null }
}

function Test-Listening([int]$port) {
    return $null -ne (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}

function Wait-Endpoint([string]$url, [int]$seconds = 60) {
    for ($i = 0; $i -lt $seconds; $i++) {
        if (Test-Endpoint $url) { return $true }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Stop-PortOwner([int]$port) {
    Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-LocalMuseTree $_ }
}

if ((Test-Listening 7860) -and -not (Test-Endpoint 'http://127.0.0.1:7860/sdapi/v1/options')) {
    Stop-PortOwner 7860
}
if (-not (Test-Listening 7860)) {
    Start-LocalMuseService 'Forge API' "call `"$PSScriptRoot\start_forge_api.bat`"" 'forge.log'
}
if ((Test-Listening 7861) -and -not (Test-Endpoint 'http://127.0.0.1:7861/api/health')) {
    Stop-PortOwner 7861
}
if (-not (Test-Listening 7861)) {
    Start-LocalMuseService 'LocalMuse UI' "call `"$PSScriptRoot\start_localmuse_ui.bat`"" 'ui.log'
}

Wait-Endpoint 'http://127.0.0.1:7861/api/health' 90 | Out-Null
Start-Process 'http://127.0.0.1:7861'

$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Application
$notify.Text = 'LocalMuse is running'
$notify.Visible = $true
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$open = $menu.Items.Add('Open LocalMuse')
$open.Add_Click({ Start-Process 'http://127.0.0.1:7861' })
$logs = $menu.Items.Add('Open logs')
$logs.Add_Click({ Start-Process explorer.exe $logRoot })
$menu.Items.Add('-') | Out-Null
$stop = $menu.Items.Add('Stop LocalMuse services')
$stop.Add_Click({ $servicePids | ForEach-Object { Stop-LocalMuseTree $_ }; [LocalMuseJob]::CloseHandle($jobHandle) | Out-Null; $notify.Visible = $false; $notify.Dispose(); [System.Windows.Forms.Application]::Exit() })
$notify.ContextMenuStrip = $menu
$notify.Add_DoubleClick({ Start-Process 'http://127.0.0.1:7861' })

[System.Windows.Forms.Application]::Run()
