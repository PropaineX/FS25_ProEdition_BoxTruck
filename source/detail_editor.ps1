param([string]$Code, [string]$Capture, [long]$WindowHandle=0, [switch]$DismissStartup, [string]$OpenFile, [switch]$Integrate, [switch]$Save, [switch]$Preview, [switch]$ReloadStage, [switch]$Before)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Select-Object -First 1
$editorHandle=if($WindowHandle){[IntPtr]$WindowHandle}else{$p.MainWindowHandle}
[void][U]::ShowWindow($editorHandle,3)
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void keybd_event(byte b, byte s, uint f, UIntPtr e);' -Name KeyDetail -Namespace Win
[Win.KeyDetail]::keybd_event(0x12,0,0,[UIntPtr]::Zero)
[Win.KeyDetail]::keybd_event(0x12,0,2,[UIntPtr]::Zero)
for ($i=0; $i -lt 8 -and (Foreground-Title) -notmatch '^GIANTS Editor'; $i++) {
    [void][U]::ShowWindow($editorHandle,9)
    [Win.KeyDetail]::keybd_event(0x12,0,0,[UIntPtr]::Zero)
    [Win.KeyDetail]::keybd_event(0x12,0,2,[UIntPtr]::Zero)
    [void][U]::SetForegroundWindow($editorHandle)
    Start-Sleep -Milliseconds 700
}
Assert-Editor
if ($DismissStartup) { Send '{ESC}'; Start-Sleep -Seconds 1 }
if ($ReloadStage) { $OpenFile=(Resolve-Path "$PSScriptRoot/../previews/detail_v1/work/boxTruck.i3d").Path }
if ($Before) { $OpenFile=(Resolve-Path "$PSScriptRoot/../previews/detail_v1/before/boxTruck.i3d").Path }
if ($OpenFile) { Click 700 450; Send '^o'; Start-Sleep -Seconds 1; Send '%n'; Paste $OpenFile; Send '{ENTER}'; Start-Sleep -Seconds 8 }
if ($Integrate) {
    $stagePath=((Resolve-Path "$PSScriptRoot/../previews/detail_v1/work").Path -replace '\\','/')
    $luaPath=($PSScriptRoot -replace '\\','/')
    $fresh=Join-Path (Split-Path $stagePath) ('integrate_'+[Guid]::NewGuid().ToString('N')+'.lua')
    Copy-Item -LiteralPath "$PSScriptRoot/integrate_body_detail.lua" -Destination $fresh
    $Code='BODY_DETAIL_SOURCE="'+$stagePath+'/bodyDetail.i3d"; source("'+($fresh -replace '\\','/')+'")'
}
if ($Preview) {
    $previewPath=(Resolve-Path "$PSScriptRoot/../previews/detail_v1").Path
    $previewFile=Join-Path $previewPath ('preview_'+[Guid]::NewGuid().ToString('N')+'.lua')
    Copy-Item -LiteralPath "$PSScriptRoot/preview_body_detail.lua" -Destination $previewFile
    $wheelCode=Get-Content -LiteralPath "$PSScriptRoot/preview_body_wheels.lua" -Raw
    $viewCode=Get-Content -LiteralPath $previewFile -Raw
    Set-Content -LiteralPath $previewFile -Value ($wheelCode+"`n"+$viewCode) -Encoding UTF8
    $Code='source("'+($previewFile -replace '\\','/')+'")'
}
if ($Code) {
    Click 1000 1320; Send '^a'; Paste $Code; Send '+{ENTER}'
    Start-Sleep -Seconds 3
}
if ($Save) { Click 700 450; Send '^s'; Start-Sleep -Seconds 4 }
if ($Capture) {
    & "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1" $Capture
}
[void][U]::ShowWindow($editorHandle,6)
