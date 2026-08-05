# Ler o arquivo como bytes brutos (sem interpretar encoding)
$filePath = "index.html"
$rawBytes = [System.IO.File]::ReadAllBytes($filePath)

Write-Host "Tamanho do arquivo: $($rawBytes.Length) bytes"

# Verificar uma sequência suspeita - "opções" em UTF-8 correto seria:
# o=6F p=70 ç=C3A7 õ=C3B5 e=65 s=73
# Verificar se está double-encoded:
# ç double-encoded = C3 seria C3 83, A7 seria C2 A7

# Encontrar a string "op" seguida de bytes suspeitos
$searchStart = 0
$foundAt = -1
for ($i = 0; $i -lt $rawBytes.Length - 6; $i++) {
    if ($rawBytes[$i] -eq 0x6F -and $rawBytes[$i+1] -eq 0x70) {
        # Verificar se próximos bytes são C3 seguidos de algo
        if ($rawBytes[$i+2] -eq 0xC3) {
            $hex = ($rawBytes[$i..($i+9)] | ForEach-Object { $_.ToString("X2") }) -join " "
            Write-Host "Sequencia em op (offset $i): $hex"
            $foundAt = $i
            break
        }
    }
}

# Verificar se o arquivo é UTF-8 válido
$utf8 = [System.Text.Encoding]::UTF8
$isValid = $true
try {
    $decoded = $utf8.GetString($rawBytes)
    Write-Host "Arquivo decodificado como UTF-8 sem erros"
    # Mostrar sample de "opções" contexto
    $idx = $decoded.IndexOf("op")
    while ($idx -ge 0 -and $idx -lt $decoded.Length - 10) {
        $ctx = $decoded.Substring($idx, 10)
        if ($ctx -match '[^\x00-\x7F]') {
            Write-Host "Sample com acento: '$ctx'"
            break
        }
        $idx = $decoded.IndexOf("op", $idx + 1)
    }
} catch {
    Write-Host "ERRO ao decodificar como UTF-8: $_"
    $isValid = $false
}

# Verificar padrão double-encoding: ç em UTF-8 é C3A7
# Se double-encoded: C3 vira C383, A7 vira C2A7
# Contar ocorrências de C3 83 (sinal de double-encoding)
$doubleCount = 0
for ($i = 0; $i -lt $rawBytes.Length - 1; $i++) {
    if ($rawBytes[$i] -eq 0xC3 -and $rawBytes[$i+1] -eq 0x83) {
        $doubleCount++
    }
}
Write-Host "Ocorrencias de C3 83 (Ã em UTF-8 = sinal de double-encoding): $doubleCount"

$latimCount = 0
for ($i = 0; $i -lt $rawBytes.Length - 1; $i++) {
    if ($rawBytes[$i] -eq 0xC3 -and ($rawBytes[$i+1] -ge 0xA0 -and $rawBytes[$i+1] -le 0xBF)) {
        $latimCount++
    }
}
Write-Host "Ocorrencias de caracteres PT corretos (C3 A0-BF): $latimCount"
