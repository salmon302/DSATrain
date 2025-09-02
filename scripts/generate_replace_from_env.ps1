<#
Usage (PowerShell):
  $env:REDACT_OPENAI = 'sk-...'
  $env:REDACT_OPENROUTER = 'sk-or-...'
  $env:REDACT_CF_COOKIE = 'JSESSIONID=...; cf_clearance=...'
  .\generate_replace_from_env.ps1

This will create a local `replace.txt` in the current directory. Do NOT commit it.
#>

$out = Join-Path -Path (Get-Location) -ChildPath 'replace.txt'
if (Test-Path $out) { Remove-Item -Force $out }


function Add-IfEnv {
    param(
        [string]$EnvName,
        [string]$Label
    )

    $value = ${env:$EnvName}
    if ($null -ne $value -and $value -ne '') {
        $literal = $value
        "literal:$literal==>REDACTED_$Label" | Out-File -FilePath $out -Append -Encoding utf8
        Write-Host "Added $EnvName -> REDACTED_$Label"
    }
}

Add-IfEnv -EnvName 'REDACT_OPENAI' -Label 'OPENAI_KEY'
Add-IfEnv -EnvName 'REDACT_OPENROUTER' -Label 'OPENROUTER_KEY'
Add-IfEnv -EnvName 'REDACT_CF_COOKIE' -Label 'CF_COOKIE'

Write-Host "Wrote replace.txt (local). Do NOT commit this file. Use: git filter-repo --replace-text replace.txt"
