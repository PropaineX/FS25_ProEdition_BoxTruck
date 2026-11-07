$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowTitle -like '*boxTruck.i3d*'} | Sort-Object Id | Select-Object -First 1
if(-not $p){throw 'Scratch editor absent'}
$out=(Resolve-Path "$PSScriptRoot/../../previews/flatbed_underrun_stripes_v2").Path
$base=$PSScriptRoot.Replace('\','/')
$setup=@"
assert(type(flatbedView)=='function','Fitted scene required')
local function hideOld(n)
 if string.find(getName(n),'Reflective safety band') then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideOld(getChildAt(n,i)) end
end
hideOld(getRootNode())
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
flatbedState('boards',false)
flatbedView(2,1.5,-9,0,.95,-5.3,30)
"@
$apply=@"
local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end
end
local comp=find(getRootNode(),'fh16_main_component1')
local bands=loadI3DFile('$($out.Replace('\','/'))/reflectiveBands.i3d',false,false,false)
assert(bands~=0,'Stripe asset failed to load');link(comp,bands)
print('[UNDERRUN_STRIPES] two0.48m red-white diagonal bands fitted; center plain; reflective behavior UNTESTED')
"@
$shots=@(
 @{name='01_before_plain';code=$setup},
 @{name='02_after_stripes';code=$apply},
 @{name='03_rear_straight';code='flatbedView(0,1.25,-9,0,.95,-5.3,32)'}
)
[void][U]::ShowWindow($p.MainWindowHandle,3);[void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep -Seconds 1
foreach($shot in $shots){
 $lua=Join-Path $out ($shot.name+'_v2.lua');Set-Content $lua $shot.code
 if((Foreground-Title) -notmatch '^GIANTS Editor'){throw 'Main viewport must be foreground'}
 Click 1000 1320;Send '^a';Paste ('source("'+$lua.Replace('\','/')+'")');Send '+{ENTER}';Start-Sleep -Seconds 2
 & "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" (Join-Path $out ($shot.name+'.png'))
}
[void][U]::ShowWindow($p.MainWindowHandle,6)
& 'C:/Users/groov/AppData/Local/Programs/Microsoft VS Code/bin/code.cmd' -r (Join-Path $out '02_after_stripes.png') (Join-Path $out '03_rear_straight.png')

