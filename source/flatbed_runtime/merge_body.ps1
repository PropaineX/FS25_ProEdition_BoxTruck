$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*flatbedTruck_work.i3d*'} | Select-Object -First 1
if(-not $p){throw 'New scratch flatbed window not ready'}
[void][U]::ShowWindow($p.MainWindowHandle,3);[void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep -Seconds 1
if((Foreground-Title) -notmatch '^GIANTS Editor.*flatbedTruck_work'){throw 'Scratch flatbed main window must be foreground'}
Click 1000 1320;Send '^a';Paste ('source("'+$PSScriptRoot.Replace('\','/')+'/merge_body.lua")');Send '+{ENTER}';Start-Sleep -Seconds 3
Click 800 700;Send '^s';Start-Sleep -Seconds 4
& "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" "$PSScriptRoot/build/merged_runtime_initial.png"
[void][U]::ShowWindow($p.MainWindowHandle,6)
