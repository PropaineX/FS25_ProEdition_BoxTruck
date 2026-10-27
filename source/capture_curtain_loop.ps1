. "$PSScriptRoot/../../Library/_FS25Knowledge/tools/ge10/ui.ps1"
& "$PSScriptRoot/run_shape_editor.ps1"
Add-Type -AssemblyName System.Drawing
$out=Join-Path $PSScriptRoot '../previews/curtain_shape_motion/loop_frames'
New-Item -ItemType Directory -Force -Path $out | Out-Null
for($frame=0;$frame -le 30;$frame++) {
    Assert-Editor
    $amount=($frame/30).ToString('0.000000',[Globalization.CultureInfo]::InvariantCulture)
    $command='for i=0,getNumOfChildren(SHAPE_PREVIEW)-1 do local g=getChildAt(SHAPE_PREVIEW,i); for j=0,getNumOfChildren(g)-1 do setShaderParameter(getChildAt(g,j),"curtainShape",'+$amount+','+$amount+',0,0,false) end end; for i=0,getNumOfChildren(getRootNode())-1 do local n=getChildAt(getRootNode(),i); if getName(n):find("Camera") or getName(n)=="persp" then setVisibility(n,false) end end'
    Click 800 1320
    Send '^a'
    Paste $command
    Send '+{ENTER}'
    Start-Sleep -Milliseconds 200
    $bmp=New-Object System.Drawing.Bitmap 1020,440
    $graphics=[System.Drawing.Graphics]::FromImage($bmp)
    $graphics.CopyFromScreen(700,460,0,0,(New-Object System.Drawing.Size 1020,440))
    $bmp.Save((Join-Path $out ('frame_{0:D3}.png' -f $frame)))
    $graphics.Dispose();$bmp.Dispose()
    if($frame % 10 -eq 0){Write-Output "Captured frame $frame of 30"}
}
& "$PSScriptRoot/finish_shape_editor.ps1"
