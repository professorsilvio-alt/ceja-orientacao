# Un-double-encoding: corrige UTF-8 duplamente codificado
# O arquivo foi lido como Latin-1/CP1252 e re-salvo como UTF-8, criando double-encoding
# Solucao: ler como UTF-8, re-codificar como CP1252 (desfaz o segundo passo), decodificar como UTF-8

$filePath = "index.html"

# Verificar estado antes
$bytesBefore = [System.IO.File]::ReadAllBytes($filePath)
Write-Host "Tamanho antes: $($bytesBefore.Length) bytes"
Write-Host "Primeiros bytes: 0x$($bytesBefore[0].ToString('X2')) 0x$($bytesBefore[1].ToString('X2')) 0x$($bytesBefore[2].ToString('X2'))"

# Ler o arquivo como UTF-8 (obtemos chars double-encoded como Ã, §, µ etc.)
$doubleEncoded = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)

# Re-codificar como Windows-1252 para obter de volta os bytes UTF-8 originais
# Ã (U+00C3) → 0xC3 em CP1252, § (U+00A7) → 0xA7 em CP1252
# Isso desfaz o passo que PowerShell fez ao ler Latin-1 como se fosse chars Unicode
$cp1252 = [System.Text.Encoding]::GetEncoding(1252)
$originalUtf8Bytes = $cp1252.GetBytes($doubleEncoded)

# Decodificar esses bytes como UTF-8 para obter o texto correto
$fixedText = [System.Text.Encoding]::UTF8.GetString($originalUtf8Bytes)

# Salvar como UTF-8 SEM BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($filePath, $fixedText, $utf8NoBom)

# Verificar resultado
$bytesAfter = [System.IO.File]::ReadAllBytes($filePath)
Write-Host "Tamanho depois: $($bytesAfter.Length) bytes"
Write-Host "Primeiros bytes: 0x$($bytesAfter[0].ToString('X2')) 0x$($bytesAfter[1].ToString('X2')) 0x$($bytesAfter[2].ToString('X2'))"

# Verificar se "opcoes" agora está correto: deve ser C3 B5 para õ
$searchBytes = @(0x6F, 0x70)  # "op"
for ($i = 0; $i -lt $bytesAfter.Length - 6; $i++) {
    if ($bytesAfter[$i] -eq 0x6F -and $bytesAfter[$i+1] -eq 0x70) {
        if ($bytesAfter[$i+2] -eq 0xC3) {
            $hex = ($bytesAfter[$i..($i+9)] | ForEach-Object { $_.ToString("X2") }) -join " "
            Write-Host "Sequencia 'op' (offset $i): $hex"
            if ($bytesAfter[$i+2] -eq 0xC3 -and $bytesAfter[$i+3] -eq 0xA7) {
                Write-Host "  -> 'opções' CORRETO! (C3 A7 = ç em UTF-8)"
            } elseif ($bytesAfter[$i+2] -eq 0xC3 -and $bytesAfter[$i+3] -eq 0x83) {
                Write-Host "  -> AINDA ERRADO! (C3 83 = double-encoded)"
            }
            break
        }
    }
}

# Mostrar amostra do texto corrigido
$sample = $fixedText.Substring(3000, [Math]::Min(200, $fixedText.Length - 3000))
Write-Host "Amostra do texto corrigido: $sample"

Write-Host "CONCLUIDO!"
