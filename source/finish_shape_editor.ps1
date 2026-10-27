. "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
Get-Process editor | Where-Object {$_.MainWindowHandle -ne 0} | ForEach-Object { [void][U]::ShowWindow($_.MainWindowHandle,6) }
