$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Sort-Object Id | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_round_underrun_v1").Path
$base=$PSScriptRoot.Replace('\','/')
$setup=@"
if type(flatbedState)~='function' then source('$base/boot_v1.lua') end
source('$base/hide_donor_lamps_v2.lua')
flatbedState('boards',false)
flatbedView(4,2.2,-10,0,1.1,-4.5,36)
"@
$change=@"
local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name); if r then return r end end
end
local old=find(getRootNode(),'Rear underrun beam')
assert(old,'Original underrun beam not found')
local comp=find(getRootNode(),'fh16_main_component1')
local tube=loadI3DFile('$($out.Replace('\','/'))/roundTube.i3d',false,false,false)
assert(tube~=0,'Tube asset not loaded')
link(comp,tube); setVisibility(old,false)
print('[FLATBED_TUBE] round tube fitted; old rectangular beam hidden')
"@
Set-Content (Join-Path $out 'setup_round_v2.lua') $setup
Set-Content (Join-Path $out 'apply_round_v2.lua') $change
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Seconds 1
foreach($step in @(@{lua='setup_round_v2.lua';png='before_rectangular_v2.png'},@{lua='apply_round_v2.lua';png='after_round_tube_v2.png'})){
 if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
 Click 1000 1320; Send '^a'; Paste ('source("'+(Join-Path $out $step.lua).Replace('\','/')+'")'); Send '+{ENTER}'; Start-Sleep -Seconds 2
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out $step.png)
}
[void][U]::ShowWindow($p.MainWindowHandle,6)

