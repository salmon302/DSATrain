param(
  [string[]]$KeysToRedact
)

if (-not $KeysToRedact -or $KeysToRedact.Count -eq 0) {
  Write-Host "Usage: .\make_replace_text.ps1 -KeysToRedact 'sk-abc' 'JSESSIONID=...'"
  exit 1
}

$out = "replace.txt"
Remove-Item -Force -ErrorAction Ignore $out
foreach ($k in $KeysToRedact) {
  # Escape = and other characters by using literal: prefix
  "$k==>REDACTED" | Out-File -FilePath $out -Append -Encoding utf8
}

Write-Host "Wrote $out. Use it with: git filter-repo --replace-text replace.txt"
