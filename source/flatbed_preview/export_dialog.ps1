param([string]$Path,[string]$Capture)
$ErrorActionPreference='Stop'; . "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
Add-Type '[System.Runtime.InteropServices.DllImport("user32.dll", CharSet=System.Runtime.InteropServices.CharSet.Unicode)] public static extern System.IntPtr FindWindow(string c,string t);' -Name FindExport -Namespace Preview; $h=[Preview.FindExport]::FindWindow($null,"Export"); if($h -eq [IntPtr]::Zero){throw "Export dialog absent"}; [void][U]::SetForegroundWindow($h); Start-Sleep -Milliseconds 500; Assert-Editor; Click 620 645; Send '{END}'; Send '{ENTER}'; Click 516 620; Send '^a'; Paste $Path
Add-Type -AssemblyName System.Drawing; $b=New-Object Drawing.Bitmap 2560,1440; $g=[Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,$b.Size); $b.Save($Capture); $g.Dispose(); $b.Dispose()


