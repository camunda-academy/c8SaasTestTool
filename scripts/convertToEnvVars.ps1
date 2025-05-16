param (
    [string]$inputFilePath
)

# Check if exactly one input file is provided
if (-not $inputFilePath) {
    Write-Host "Usage: .\convertFromLinuxToWinEnvVar.ps1 -inputFilePath <path_to_input_file>"
    exit 1
}

# Check if the input file exists
if (-not (Test-Path $inputFilePath)) {
    Write-Host "Input file not found: $inputFilePath"
    exit 1
}

$outputFilePath = "envVars.txt"

# Read the content of the Linux env file
$content = Get-Content -Path $inputFilePath

# Convert the file content to Windows format
$windowsFormat = foreach ($line in $content) {
    if ($line -like "export *") {
        # Remove 'export ' and quotes
        $line = $line -replace '^export\s+', ''
        $line = $line -replace "'|`"", ''
        $line
    }
}

# Write the converted content to the output file
$windowsFormat | Set-Content -Path $outputFilePath
