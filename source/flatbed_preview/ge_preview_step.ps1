param([string]$Lua,[string]$Capture,[string]$Action)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class FindGE { public delegate bool CB(IntPtr h,IntPtr p); [DllImport("user32.dll")] public static extern bool EnumWindows(CB c,IntPtr p); [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h,StringBuilder s,int n); }
"@
$script:geHandle=[IntPtr]::Zero
[FindGE]::EnumWindows({param($h,$p) $t=New-Object Text.StringBuilder 512; [void][FindGE]::GetWindowText($h,$t,512); if($t.ToString() -match '^GIANTS Editor 64bit.*boxTruck'){ $script:geHandle=$h }; return $true},[IntPtr]::Zero) | Out-Null
if($script:geHandle -eq [IntPtr]::Zero){throw 'No scratch truck Editor window'}
[void][U]::ShowWindow($script:geHandle,3); [void][U]::SetForegroundWindow($script:geHandle); Start-Sleep -Seconds 1
Assert-Editor
if($Lua){Click 1000 1320; Send '^a'; Paste ('source("'+$Lua.Replace('\','/')+'")'); Send '+{ENTER}'; Start-Sleep -Seconds 3}
if($Action -eq 'menu'){Click 18 40}
if($Action -eq 'export'){Click 18 40; Click 113 337; Start-Sleep -Seconds 1; Click 620 645; Send '{END}'; Send '{ENTER}'; Click 516 620; Send '^a'; Paste ((Resolve-Path "$PSScriptRoot/../../previews/flatbed_fitted_v1").Path+'/volvo_preview.obj'); Send '{ENTER}'; Start-Sleep -Seconds 5}
if($Capture){Add-Type -AssemblyName System.Drawing; $b=New-Object Drawing.Bitmap 2560,1440; $g=[Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,$b.Size); $b.Save($Capture); $g.Dispose(); $b.Dispose()}






