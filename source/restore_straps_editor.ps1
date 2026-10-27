Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class StrapWindows {
 public delegate bool EnumProc(IntPtr h, IntPtr p);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int command);
 public static void Restore(uint pid){EnumWindows((h,p)=>{uint owner;GetWindowThreadProcessId(h,out owner); if(owner==pid){var s=new StringBuilder(512);GetWindowText(h,s,512);if(s.ToString().StartsWith("GIANTS Editor 64bit")){ShowWindow(h,3);System.Console.WriteLine(h.ToString()+" "+s.ToString());}} return true;},IntPtr.Zero);}
}
"@
Get-Process editor | Sort-Object StartTime -Descending | Select-Object -First 1 | ForEach-Object {[StrapWindows]::Restore([uint32]$_.Id)}
Start-Sleep -Milliseconds 600
Get-Process editor | Select-Object Id,MainWindowHandle,MainWindowTitle
