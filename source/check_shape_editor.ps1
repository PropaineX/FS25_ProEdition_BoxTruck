. "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
$p=Get-Process editor | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -Last 1
[void][U]::ShowWindow($p.MainWindowHandle,3)
[void][U]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 700
Add-Type -AssemblyName System.Drawing
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size)
$bmp.Save("$env:TEMP/boxtruck_full.png")
$g.Dispose();$bmp.Dispose()
