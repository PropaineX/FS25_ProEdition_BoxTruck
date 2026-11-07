$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*flatbedTruck_check.i3d*'} | Select-Object -First 1
if(-not $p){throw 'Runtime-check scratch editor not ready'}
$out=(Resolve-Path "$PSScriptRoot/verify").Path
[void][U]::ShowWindow($p.MainWindowHandle,3);[void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep -Seconds 1
$shots=@(
 @{name='01_runtime_boards';code="source('$($out.Replace('\','/'))/check_runtime.lua')"},
 @{name='02_runtime_stakes_closed';code='runtimePose(true,0,0)'},
 @{name='03_runtime_stakes_open';code='runtimePose(true,1,0)'},
 @{name='04_runtime_boards_half';code='runtimePose(false,.5,.5)'},
 @{name='05_runtime_boards_open';code='runtimePose(false,1,1)'}
)
foreach($shot in $shots){
 $lua=Join-Path $out ($shot.name+'.lua');Set-Content $lua $shot.code
 if((Foreground-Title) -notmatch '^GIANTS Editor.*flatbedTruck_check'){throw 'Runtime scratch main viewport must be foreground'}
 Click 1000 1320;Send '^a';Paste ('source("'+$lua.Replace('\','/')+'")');Send '+{ENTER}';Start-Sleep -Seconds 2
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ($shot.name+'.png'))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
& 'C:/Users/groov/AppData/Local/Programs/Microsoft VS Code/bin/code.cmd' -r (Join-Path $out '01_runtime_boards.png') (Join-Path $out '05_runtime_boards_open.png')
