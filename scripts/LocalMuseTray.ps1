Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$projectRoot = Split-Path -Parent $PSScriptRoot
$logRoot = Join-Path $projectRoot 'outputs\localmuse_logs'
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$servicePids = @()
$env:LOCALMUSE_TRAY_PID = [string]$PID

function Start-LocalMuseService([string]$title, [string]$command, [string]$logName) {
    $logPath = Join-Path $logRoot $logName
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("Set-Location -LiteralPath '$projectRoot'; & cmd.exe /c '$command' 2>&1 | Tee-Object -FilePath '$logPath'"))
    $process = Start-Process powershell.exe -WindowStyle Hidden -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encoded -PassThru
    $script:servicePids += $process.Id
}

Start-LocalMuseService 'Forge API' "call '$PSScriptRoot\start_forge_api.bat'" 'forge.log'
Start-LocalMuseService 'LocalMuse UI' "call '$PSScriptRoot\start_localmuse_ui.bat'" 'ui.log'

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
$stop.Add_Click({ $servicePids | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }; $notify.Visible = $false; $notify.Dispose(); [System.Windows.Forms.Application]::Exit() })
$notify.ContextMenuStrip = $menu
$notify.Add_DoubleClick({ Start-Process 'http://127.0.0.1:7861' })

[System.Windows.Forms.Application]::Run()
