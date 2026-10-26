param([long]$WindowHandle=1521800)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$handle=[IntPtr]$WindowHandle
[void][U]::ShowWindow($handle,3)
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void keybd_event(byte b, byte s, uint f, UIntPtr e);' -Name GatherKey -Namespace Win
for ($attempt=0; $attempt -lt 8 -and (Foreground-Title) -notmatch '^GIANTS Editor'; $attempt++) {
    [Win.GatherKey]::keybd_event(0x12,0,0,[UIntPtr]::Zero)
    [Win.GatherKey]::keybd_event(0x12,0,2,[UIntPtr]::Zero)
    [void][U]::ShowWindow($handle,9)
    [void][U]::SetForegroundWindow($handle)
    Start-Sleep -Milliseconds 500
}
Assert-Editor
if ((Foreground-Title) -match '^Open File') { Click 1130 725; Start-Sleep -Milliseconds 500 }
$title=Foreground-Title
if ($title -notmatch '^GIANTS Editor') { throw "Editor modal still active: $title" }
$root=(Resolve-Path "$PSScriptRoot/..").Path -replace '\\','/'
$fresh="$root/previews/gathered_integration/engine_$([Guid]::NewGuid().ToString('N')).lua"
Copy-Item -LiteralPath "$root/source/preview_gathered_engine.lua" -Destination $fresh
$lua='GATHERED_ASSET="'+$root+'/gatheredCurtains.i3d"; source("'+$fresh+'")'
Click 1000 1320
Send '^a'
Paste $lua
Send '+{ENTER}'
Start-Sleep -Seconds 5
& "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" "$root/previews/gathered_integration/engine_pro_edition.png"
[void][U]::ShowWindow($handle,6)
