$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Sort-Object Id | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_tailgate_v3").Path
$setup=@"
assert(type(flatbedView)=='function','Fitted scene required')
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
local function hideOld(n)
 if getName(n)=='Tailgate_30cm_proposal' then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideOld(getChildAt(n,i)) end
end
hideOld(getRootNode())
flatbedState('boards',false)
flatbedView(3,2.7,-9,0,1.65,-4.7,36)
"@
$apply=@"
local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end
end
local comp=find(getRootNode(),'fh16_main_component1')
local gate=loadI3DFile('$($out.Replace('\','/'))/tailgatePreview.i3d',false,false,false)
assert(gate~=0,'Tailgate asset failed to load');link(comp,gate);TAILGATEREVIEW=gate
print('[TAILGATE] stainless diamond pattern, width2.37m height0.30m; side-wall configuration only')
"@
$shots=@(
 @{name='01_before_open_rear';code=$setup},
 @{name='02_boards_tailgate_detail';code=$apply},
 @{name='03_boards_rear34';code='flatbedView(7,3.8,-11,0,1.9,-.7,38)'},
 @{name='04_stakes_rear34';code="setVisibility(TAILGATEREVIEW,false)
flatbedState('stakes',false)`nflatbedView(7,3.8,-11,0,1.9,-.7,38)"},
 @{name='05_diamond_pattern_close';code="setVisibility(TAILGATEREVIEW,true)`nflatbedState('boards',false)`nflatbedView(1,2.3,-7,0,1.8,-5.37,45)"},
 @{name='06_tailgate_rear';code='flatbedView(0,2.6,-10,0,1.8,-3,32)'}
)
[void][U]::ShowWindow($p.MainWindowHandle,3);[void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep -Seconds 1
foreach($shot in $shots){
 $lua=Join-Path $out ($shot.name+'_v3.lua');Set-Content $lua $shot.code
 if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
 Click 1000 1320;Send '^a';Paste ('source("'+$lua.Replace('\','/')+'")');Send '+{ENTER}';Start-Sleep -Seconds 2
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ($shot.name+'.png'))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
& 'C:/Users/groov/AppData/Local/Programs/Microsoft VS Code/bin/code.cmd' -r (Join-Path $out '03_boards_rear34.png') (Join-Path $out '04_stakes_rear34.png')


