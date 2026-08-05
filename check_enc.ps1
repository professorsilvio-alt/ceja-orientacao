# Verificar estado atual do encoding
$filePath = "index.html"
$bytes = [System.IO.File]::ReadAllBytes($filePath)
Write-Host "Tamanho: $($bytes.Length) bytes"
Write-Host "Primeiros 4 bytes: 0x$($bytes[0].ToString('X2')) 0x$($bytes[1].ToString('X2')) 0x$($bytes[2].ToString('X2')) 0x$($bytes[3].ToString('X2'))"

if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "BOM ENCONTRADO! Removendo definitivamente..."
    $cleanBytes = $bytes[3..($bytes.Length - 1)]
    [System.IO.File]::WriteAllBytes($filePath, $cleanBytes)
    Write-Host "BOM removido. Novo tamanho: $($cleanBytes.Length) bytes"
} else {
    Write-Host "Sem BOM."
}

# Verificar a tag meta charset
$text = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)
$idx = $text.IndexOf("charset")
if ($idx -ge 0) {
    Write-Host "Meta charset encontrado: '$($text.Substring($idx-5, 40))'"
} else {
    Write-Host "AVISO: meta charset NAO encontrado!"
}

# Mostrar primeiros 200 chars do arquivo
Write-Host "Inicio do arquivo:"
Write-Host $text.Substring(0, [Math]::Min(200, $text.Length))
