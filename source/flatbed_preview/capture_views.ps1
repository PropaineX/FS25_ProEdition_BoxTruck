param([string]$Batch='boards')
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Seconds 1
if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_fitted_v1").Path
$cleanup=Join-Path $PSScriptRoot 'hide_donor_lamps_v2.lua'
Click 1000 1320; Send '^a'; Paste ('source("'+$cleanup.Replace('\','/')+'")'); Send '+{ENTER}'
$views=@(
 @{name='closed_side'; opened='false'; view='12,2.3,-.4,0,2,-.4,32'},
 @{name='open_side'; opened='true'; view='12,2.3,-.4,0,2,-.4,32'},
 @{name='open_rear34'; opened='true'; view='8,4,-12,0,1.9,-.7,36'},
 @{name='closed_rear34'; opened='false'; view='8,4,-12,0,1.9,-.7,36'},
 @{name='closed_front34'; opened='false'; view='8,4,10,0,1.9,-.4,38'},
 @{name='closed_rear'; opened='false'; view='0,2.6,-13,0,1.9,-2,30'}
)
foreach($view in $views){
 $lua=Join-Path $out ($Batch+'_'+$view.name+'_v2_view.lua')
 $code="flatbedState('$Batch',$($view.opened))`nflatbedView($($view.view))"
 Set-Content -LiteralPath $lua -Value $code
 Click 1000 1320; Send '^a'; Paste ('source("'+$lua.Replace('\','/')+'")'); Send '+{ENTER}'; Start-Sleep -Seconds 1
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ($Batch+'_'+$view.name+'_v2_fitted.png'))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
& 'C:/Users/groov/AppData/Local/Programs/Microsoft VS Code/bin/code.cmd' -r (Join-Path $out ($Batch+'_closed_front34_v2_fitted.png')) (Join-Path $out ($Batch+'_open_rear34_v2_fitted.png'))
