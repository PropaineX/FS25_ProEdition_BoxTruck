$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Sort-Object Id | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_plate_milk_v1").Path
$base=$PSScriptRoot.Replace('\','/')
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Seconds 1
$shots=@(
 @{name='07_clear_spacing_side';code="source('$base/milk_clear_spacing_v1.lua')"},
 @{name='08_clear_spacing_rear34';code="flatbedView(9,5,-13,0,2.3,-.6,38)"},
 @{name='09_clear_spacing_close';code="flatbedView(4,3.3,-4,0,2.7,-2,34)"}
)
foreach($shot in $shots){
 $lua=Join-Path $out ($shot.name+'_script.lua'); Set-Content $lua $shot.code
 if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
 Click 1000 1320; Send '^a'; Paste ('source("'+$lua.Replace('\','/')+'")'); Send '+{ENTER}'; Start-Sleep -Seconds 2
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ($shot.name+'.png'))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
& 'C:/Users/groov/AppData/Local/Programs/Microsoft VS Code/bin/code.cmd' -r (Join-Path $out '07_clear_spacing_side.png') (Join-Path $out '08_clear_spacing_rear34.png')

