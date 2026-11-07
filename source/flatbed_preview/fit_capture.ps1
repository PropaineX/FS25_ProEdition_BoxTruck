param([string]$Capture)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Select-Object -First 1
if(-not $p){throw 'Scratch editor not ready'}
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Seconds 1
Assert-Editor
if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main Editor must be foreground'}
Click 1000 1320; Send '^a'; Paste ('source("'+$PSScriptRoot.Replace('\','/')+'/boot_v1.lua")'); Send '+{ENTER}'; Start-Sleep -Seconds 3
if($Capture){& "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" $Capture}
[void][U]::ShowWindow($p.MainWindowHandle,6)

