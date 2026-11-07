$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Sort-Object Id | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_stake_motion_v1").Path
$setup=@"
assert(type(flatbedView)=='function','Fitted scene required')
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
local function hideGate(n)
 if getName(n)=='Tailgate_30cm_proposal' then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideGate(getChildAt(n,i)) end
end
hideGate(getRootNode())
flatbedState('stakes',false)
flatbedView(12,3.4,-.5,0,2,-.5,34)
print('[STAKE_MOTION] native XML channels sampled; 0.7s full travel')
"@
$lua=Join-Path $out 'setup_motion_v1.lua';Set-Content $lua $setup
[void][U]::ShowWindow($p.MainWindowHandle,3);[void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep -Seconds 1
if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
Click 1000 1320;Send '^a';Paste ('source("'+$lua.Replace('\','/')+'")');Send '+{ENTER}';Start-Sleep -Seconds 1
for($frame=0;$frame -le 14;$frame++){
 if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
 $lua=Join-Path $out ('frame_{0:00}.lua' -f $frame)
 Click 1000 1320;Send '^a';Paste ('source("'+$lua.Replace('\','/')+'")');Send '+{ENTER}';Start-Sleep -Milliseconds 150
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ('frame_{0:00}.png' -f $frame))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
