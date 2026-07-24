[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPptx,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [ValidateRange(320, 7680)]
    [int]$Width = 1600,

    [ValidateRange(240, 4320)]
    [int]$Height = 900
)

$ErrorActionPreference = "Stop"
$inputPath = (Resolve-Path -LiteralPath $InputPptx).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputDir)
if ([System.IO.Path]::GetExtension($inputPath).ToLowerInvariant() -notin @(".pptx", ".pptm", ".ppt")) {
    throw "Input is not a PowerPoint presentation: $inputPath"
}
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null

$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Open($inputPath, $true, $false, $false)
    for ($index = 1; $index -le $presentation.Slides.Count; $index++) {
        $filename = "slide_{0:D3}.png" -f $index
        $target = Join-Path -Path $outputPath -ChildPath $filename
        $presentation.Slides.Item($index).Export($target, "PNG", $Width, $Height)
    }
    Write-Output ("Rendered {0} slides to {1}" -f $presentation.Slides.Count, $outputPath)
}
finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($null -ne $powerPoint) {
        $powerPoint.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
