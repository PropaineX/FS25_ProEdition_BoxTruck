# Prepare generated editor files when starting from a fresh checkout.
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot '../previews/curtain_shape_motion/binary.i3d'))) {
    python -I "$PSScriptRoot/prepare_curtain_preview.py"
    if ($LASTEXITCODE -ne 0) { throw 'Preview preparation failed' }
}
. "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -Last 1
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void keybd_event(byte b, byte s, uint f, UIntPtr e);' -Name ShapeKey -Namespace Win
for ($attempt=0; $attempt -lt 8 -and (Foreground-Title) -notmatch '^GIANTS Editor'; $attempt++) {
 [Win.ShapeKey]::keybd_event(0x12,0,0,[UIntPtr]::Zero)
 [Win.ShapeKey]::keybd_event(0x12,0,2,[UIntPtr]::Zero)
 [void][U]::ShowWindow($p.MainWindowHandle,9)
 [void][U]::SetForegroundWindow($p.MainWindowHandle)
 Start-Sleep -Milliseconds 400
}
Start-Sleep -Milliseconds 400
Assert-Editor
Click 800 1320
Send '^a'
$script=(Resolve-Path "$PSScriptRoot/../previews/curtain_shape_motion/check.lua").Path -replace '\\','/'
$asset=(Resolve-Path "$PSScriptRoot/../previews/curtain_shape_motion/binary.i3d").Path -replace '\\','/'
Paste ('SHAPE_ASSET="'+$asset+'"; source("'+$script+'")')
Send '+{ENTER}'
Start-Sleep -Seconds 3
