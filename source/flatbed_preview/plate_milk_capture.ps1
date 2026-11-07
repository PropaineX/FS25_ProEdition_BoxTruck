$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Sort-Object Id | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_plate_milk_v1").Path
$base=$PSScriptRoot.Replace('\','/')
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Seconds 1
$shots=@(
 @{name='01_plate_position';code="source('$base/plate_milk_v1.lua')"},
 @{name='02_milk_rear34';code="buildMilkReview()"},
 @{name='03_milk_side';code="flatbedView(13,2.7,-.4,0,2.2,-.4,34)"},
 @{name='04_milk_front34';code="flatbedView(9,5,12,0,2.3,-.5,38)"},
 @{name='05_milk_boards';code="flatbedState('boards',false)`nflatbedView(9,5,-13,0,2.3,-.6,38)"},
 @{name='06_stack_close';code="flatbedView(4,3.3,-4,0,2.7,-2,34)`nmeasureMilkReview()"}
)
foreach($shot in $shots){
 $lua=Join-Path $out ($shot.name+'_script.lua'); Set-Content $lua $shot.code
 if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
 Click 1000 1320; Send '^a'; Paste ('source("'+$lua.Replace('\','/')+'")'); Send '+{ENTER}'; Start-Sleep -Seconds 2
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ($shot.name+'.png'))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
& 'C:/Users/groov/AppData/Local/Programs/Microsoft VS Code/bin/code.cmd' -r (Join-Path $out '01_plate_position.png') (Join-Path $out '02_milk_rear34.png')
