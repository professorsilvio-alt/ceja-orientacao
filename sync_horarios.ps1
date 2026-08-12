# sync_horarios.ps1
# Sincroniza os horarios dos professores do CEJA a partir da planilha Google Sheets.
# Funciona com PowerShell puro - sem dependencias externas.
#
# COMO USAR:
#   powershell -ExecutionPolicy Bypass -File "sync_horarios.ps1"

param(
    [string]$DadosEscolaPath = (Join-Path $PSScriptRoot "dados_escola.js")
)

$SPREADSHEET_ID = '1a2XewE5KNuadI8zUbi15r5n06roJb-wa'

$ABAS = @(
    @{ Dia = 'Segunda-feira'; GID = '765921185'  }
    @{ Dia = 'Terça-feira';   GID = '222847853'  }
    @{ Dia = 'Quarta-feira';  GID = '349244144'  }
    @{ Dia = 'Quinta-feira';  GID = '642475882'  }
    @{ Dia = 'Sexta-feira';   GID = '1997803226' }
)

$COLUNAS = @(
    @{ Disciplina = 'Matemática';         Local = 'Cabine de Matemática' }
    @{ Disciplina = 'Português';          Local = 'Cabine de Linguagens' }
    @{ Disciplina = 'Inglês';             Local = 'Cabine de Linguagens' }
    @{ Disciplina = 'Espanhol';           Local = 'Cabine de Linguagens' }
    @{ Disciplina = 'Educação Artística'; Local = 'Cabine de Linguagens' }
    @{ Disciplina = 'Educação Física';    Local = 'Cabine de Linguagens' }
    @{ Disciplina = 'Ciências/Biologia';  Local = 'Cabine de Ciências da Natureza' }
    @{ Disciplina = 'Física';             Local = 'Cabine de Ciências da Natureza' }
    @{ Disciplina = 'Química';            Local = 'Cabine de Ciências da Natureza' }
    @{ Disciplina = 'História';           Local = 'Cabine de Ciências Humanas' }
    @{ Disciplina = 'Geografia';          Local = 'Cabine de Ciências Humanas' }
    @{ Disciplina = 'Sociologia';         Local = 'Cabine de Ciências Humanas' }
    @{ Disciplina = 'Filosofia';          Local = 'Cabine de Ciências Humanas' }
)

# Mapeamento de nomes curtos da planilha -> nomes no sistema
$NOMES_MAP = @{
    'Leandro'            = 'Prof. Leandro'
    'Jordan'             = 'Prof. Jordan'
    'Arlindo'            = 'Prof. Arlindo'
    'Vitor'              = 'Prof. Vitor'
    'Sandra'             = 'Prof.ª Sandra'
    'Luciana Cavalcante' = 'Prof.ª Luciana Cavalcante'
    'Luciana'            = 'Prof.ª Luciana'
    'Daniela'            = 'Prof.ª Daniela'
    'Rafael Souza'       = 'Prof. Rafael Souza'
    'Wanderley'          = 'Prof. Wanderley'
    'Thalles'            = 'Prof. Thalles'
    'Eliane'             = 'Prof.ª Eliane'
    'Elaine'             = 'Prof.ª Elaine'
    'Viviane'            = 'Prof.ª Viviane'
    'Marcela'            = 'Prof.ª Marcela'
    'Alessandra'         = 'Prof.ª Alessandra'
    'Delma'              = 'Prof.ª Delma'
    'Elazaro'            = 'Prof. Elazaro'
    'Leonardo'           = 'Prof. Leonardo'
    'Xunei'              = 'Prof. Xunei'
    'Mario'              = 'Prof. Mario'
    'Carlos Laurindo'    = 'Prof. Carlos Laurindo'
    'Fabiane'            = 'Prof.ª Fabiane'
    'Vitor Vasconcelos'  = 'Prof. Vitor Vasconcelos'
    'David'              = 'Prof. David'
    'Jose Carlos'        = 'Prof. Jose Carlos'
    'Rafael Maia'        = 'Prof. Rafael Maia'
    'Fernando'           = 'Prof. Fernando'
    'Rafael'             = 'Prof. Rafael'
}

# ── FUNCOES ───────────────────────────────────────────────────────────────────

function Get-CSV([string]$gid) {
    $url = "https://docs.google.com/spreadsheets/d/$SPREADSHEET_ID/export?format=csv&gid=$gid"
    $req = [System.Net.HttpWebRequest]::Create($url)
    $req.AllowAutoRedirect = $true
    $req.UserAgent = "Mozilla/5.0"
    $resp = $req.GetResponse()
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
    $content = $reader.ReadToEnd()
    $reader.Close()
    $resp.Close()
    return $content
}

function Parse-CSVLine([string]$line) {
    $result = [System.Collections.ArrayList]@()
    $current = [System.Text.StringBuilder]::new()
    $inQuotes = $false
    
    for ($i = 0; $i -lt $line.Length; $i++) {
        $ch = $line[$i]
        if ($ch -eq '"') {
            if ($inQuotes -and ($i + 1) -lt $line.Length -and $line[$i+1] -eq '"') {
                [void]$current.Append('"')
                $i++
            } else {
                $inQuotes = -not $inQuotes
            }
        } elseif ($ch -eq ',' -and -not $inQuotes) {
            [void]$result.Add($current.ToString())
            [void]$current.Clear()
        } else {
            [void]$current.Append($ch)
        }
    }
    [void]$result.Add($current.ToString())
    return @($result)
}

function Remove-Acentos([string]$texto) {
    $normalized = $texto.Normalize([System.Text.NormalizationForm]::FormD)
    $sb = [System.Text.StringBuilder]::new()
    foreach ($ch in $normalized.ToCharArray()) {
        $cat = [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($ch)
        if ($cat -ne [System.Globalization.UnicodeCategory]::NonSpacingMark) {
            [void]$sb.Append($ch)
        }
    }
    return $sb.ToString()
}

function Normalize-Nome([string]$raw) {
    # Remove sufixo numerico tipo "LUCIANA 1", "ARLINDO 2"
    $sem = ($raw -replace '\s+\d+$', '').Trim()
    
    # Sem acentos para lookup
    $semAcento = Remove-Acentos $sem
    
    # Capitaliza
    $cap = ($semAcento.ToLower() -split '\s+' | ForEach-Object {
        if ($_ -in @('de','da','do','dos','das','e')) { $_ }
        elseif ($_.Length -gt 0) { $_.Substring(0,1).ToUpper() + $_.Substring(1) }
    }) -join ' '
    
    if ($NOMES_MAP.ContainsKey($cap)) {
        return $NOMES_MAP[$cap]
    }
    return "Prof. $cap"
}

function Parse-AbaCSV([string]$csvText, [string]$dia) {
    # Normaliza quebras de linha
    $texto = $csvText -replace "`r`n", "`n" -replace "`r", "`n"
    
    # Reagrupa linhas partidas por aspas
    $reagrupadas = [System.Collections.ArrayList]@()
    $buffer = [System.Text.StringBuilder]::new()
    $emAspas = $false
    
    foreach ($linha in ($texto -split "`n")) {
        foreach ($ch in $linha.ToCharArray()) {
            if ($ch -eq '"') { $emAspas = -not $emAspas }
        }
        if ($buffer.Length -gt 0) { [void]$buffer.Append("`n") }
        [void]$buffer.Append($linha)
        if (-not $emAspas) {
            [void]$reagrupadas.Add($buffer.ToString())
            [void]$buffer.Clear()
        }
    }
    if ($buffer.Length -gt 0) { [void]$reagrupadas.Add($buffer.ToString()) }
    
    # Encontra linha de cabecalho (HORARIOS ou HORAR com acento)
    $headerIdx = -1
    for ($i = 0; $i -lt $reagrupadas.Count; $i++) {
        $linhaNorm = Remove-Acentos $reagrupadas[$i]
        if ($linhaNorm -match '^"?HORARIOS') {
            $headerIdx = $i
            break
        }
    }
    
    if ($headerIdx -eq -1) {
        Write-Host "   [AVISO] [$dia] Cabecalho HORARIOS nao encontrado." -ForegroundColor Yellow
        return @()
    }
    
    $entradas = [System.Collections.ArrayList]@()
    
    for ($i = $headerIdx + 1; $i -lt $reagrupadas.Count; $i++) {
        $linha = $reagrupadas[$i].Trim()
        if (-not $linha) { continue }
        
        $cols = Parse-CSVLine $linha
        if ($cols.Count -lt 2) { continue }
        
        $horarioCell = ($cols[0] -replace '"', '' -replace "`n", ' ').Trim()
        
        # Linha de horario: "08:50/ 09:40"
        if ($horarioCell -notmatch '(\d{2}:\d{2})\s*/\s*(\d{2}:\d{2})') { continue }
        $inicio = $Matches[1]
        $fim    = $Matches[2]
        
        for ($c = 1; $c -le 13 -and $c -lt $cols.Count; $c++) {
            $cell = ($cols[$c] -replace '"', '' -replace "`n", ' / ').Trim()
            if (-not $cell -or $cell -eq 'FECHADA') { continue }
            
            $nomes = $cell -split '/' | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -ne 'FECHADA' }
            foreach ($nome in $nomes) {
                if (-not $nome) { continue }
                [void]$entradas.Add([PSCustomObject]@{
                    HorarioInicio = $inicio
                    HorarioFim    = $fim
                    ColIndex      = ($c - 1)
                    NomeProfessor = (Normalize-Nome $nome)
                })
            }
        }
    }
    
    return @($entradas)
}

function Build-HorarioProfessores($todosDados) {
    $mapa = @{}
    
    foreach ($item in $todosDados) {
        foreach ($entrada in $item.Entradas) {
            if ($null -eq $entrada) { continue }
            $ci = $entrada.ColIndex
            if ($ci -lt 0 -or $ci -ge $COLUNAS.Count) { continue }
            $col = $COLUNAS[$ci]
            $chave = "$($entrada.NomeProfessor)|||$($item.Dia)|||$ci"
            
            if (-not $mapa.ContainsKey($chave)) {
                $mapa[$chave] = [PSCustomObject]@{
                    Nome       = $entrada.NomeProfessor
                    Dia        = $item.Dia
                    Local      = $col.Local
                    Disciplina = $col.Disciplina
                    Slots      = [System.Collections.ArrayList]@()
                }
            }
            [void]$mapa[$chave].Slots.Add([PSCustomObject]@{
                Inicio = $entrada.HorarioInicio
                Fim    = $entrada.HorarioFim
            })
        }
    }
    
    $profMap = @{}
    
    foreach ($chave in $mapa.Keys) {
        $item = $mapa[$chave]
        $nome = $item.Nome
        
        if (-not $profMap.ContainsKey($nome)) {
            $profMap[$nome] = [PSCustomObject]@{
                Nome        = $nome
                Disciplinas = [System.Collections.Generic.HashSet[string]]::new()
                Horarios    = [System.Collections.ArrayList]@()
            }
        }
        
        $prof = $profMap[$nome]
        [void]$prof.Disciplinas.Add($item.Disciplina)
        
        $sorted = @($item.Slots | Sort-Object Inicio)
        $inicio = $sorted[0].Inicio
        $fim    = $sorted[-1].Fim
        
        $jaExiste = $prof.Horarios | Where-Object {
            $_.Dia -eq $item.Dia -and $_.Inicio -eq $inicio -and $_.Local -eq $item.Local
        }
        if (-not $jaExiste) {
            [void]$prof.Horarios.Add([PSCustomObject]@{
                Dia    = $item.Dia
                Inicio = $inicio
                Fim    = $fim
                Local  = $item.Local
            })
        }
    }
    
    $ORDEM_DIAS = @('Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira')
    
    $resultado = [System.Collections.ArrayList]@()
    foreach ($nome in ($profMap.Keys | Sort-Object)) {
        $prof = $profMap[$nome]
        $horariosOrdenados = @($prof.Horarios | Sort-Object {
            $idx = $ORDEM_DIAS.IndexOf($_.Dia)
            if ($idx -lt 0) { $idx = 99 }
            "$($idx.ToString('00'))_$($_.Inicio)"
        })
        [void]$resultado.Add([PSCustomObject]@{
            Nome        = $prof.Nome
            Foto        = ''
            Disciplinas = @($prof.Disciplinas)
            Horarios    = $horariosOrdenados
        })
    }
    
    return @($resultado)
}

function ConvertTo-HorarioJS($horarios) {
    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine('[')
    $total = @($horarios).Count
    
    for ($i = 0; $i -lt $total; $i++) {
        $p = $horarios[$i]
        $virgProf = if ($i -lt $total - 1) { ',' } else { '' }
        
        [void]$sb.AppendLine('    {')
        [void]$sb.AppendLine("      nome: `"$($p.Nome)`",")
        [void]$sb.AppendLine("      foto: `"`",")
        
        $discArr = @($p.Disciplinas)
        $discStr = ($discArr | ForEach-Object { "`"$_`"" }) -join ', '
        [void]$sb.AppendLine("      disciplinas: [$discStr],")
        [void]$sb.AppendLine('      horarios: [')
        
        $hArr = @($p.Horarios)
        for ($j = 0; $j -lt $hArr.Count; $j++) {
            $h = $hArr[$j]
            $virgH = if ($j -lt $hArr.Count - 1) { ',' } else { '' }
            [void]$sb.AppendLine("        { dia: `"$($h.Dia)`", inicio: `"$($h.Inicio)`", fim: `"$($h.Fim)`", local: `"$($h.Local)`" }$virgH")
        }
        
        [void]$sb.AppendLine('      ]')
        [void]$sb.AppendLine("    }$virgProf")
    }
    
    [void]$sb.Append('  ]')
    return $sb.ToString()
}

function Get-TextHash([string]$text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hash = $sha.ComputeHash($bytes)
    return [System.BitConverter]::ToString($hash) -replace '-', ''
}

# ── EXECUCAO PRINCIPAL ────────────────────────────────────────────────────────

$dataHora = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CEJA - Sincronizador de Horarios"        -ForegroundColor Cyan
Write-Host " $dataHora"                                -ForegroundColor Gray
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

# 1. Busca CSVs
Write-Host "1) Buscando dados da planilha..." -ForegroundColor Yellow
$todosDados = [System.Collections.ArrayList]@()

foreach ($aba in $ABAS) {
    Write-Host "   -> $($aba.Dia)..." -NoNewline
    try {
        $csv = Get-CSV $aba.GID
        $entradas = @(Parse-AbaCSV $csv $aba.Dia)
        [void]$todosDados.Add([PSCustomObject]@{ Dia = $aba.Dia; Entradas = $entradas })
        Write-Host " OK ($($entradas.Count) entradas)" -ForegroundColor Green
    } catch {
        Write-Host " ERRO: $_" -ForegroundColor Red
        exit 1
    }
}

# 2. Constroi estrutura
Write-Host ""
Write-Host "2) Consolidando horarios..." -ForegroundColor Yellow
$novoHorario = @(Build-HorarioProfessores $todosDados)
Write-Host "   $($novoHorario.Count) professores encontrados." -ForegroundColor Green

# 3. Verifica arquivo atual
Write-Host ""
Write-Host "3) Verificando dados_escola.js..." -ForegroundColor Yellow

if (-not (Test-Path $DadosEscolaPath)) {
    Write-Host "   ERRO: Arquivo nao encontrado: $DadosEscolaPath" -ForegroundColor Red
    exit 1
}

$conteudoAtual = [System.IO.File]::ReadAllText($DadosEscolaPath, [System.Text.Encoding]::UTF8)

# Gera o novo bloco JS
$novoBloco = ConvertTo-HorarioJS $novoHorario
$hashNovo = Get-TextHash $novoBloco

# Extrai bloco atual para comparar
$regexBloco = '(?s)// HORARIOS_SYNC_START.*// HORARIOS_SYNC_END'
$matchAtual = [regex]::Match($conteudoAtual, $regexBloco)
$hashAtual  = if ($matchAtual.Success) { Get-TextHash $matchAtual.Value } else { '' }

$novoBlocoCompleto = "// HORARIOS_SYNC_START`n  horarioProfessores: $novoBloco,`n  // HORARIOS_SYNC_END"

if ($hashAtual -ne '' -and $hashAtual -eq (Get-TextHash $novoBlocoCompleto)) {
    Write-Host "   Sem alteracoes - dados_escola.js ja esta atualizado." -ForegroundColor Green
    Write-Host ""
    exit 0
}

Write-Host "   Alteracoes detectadas! Atualizando..." -ForegroundColor Yellow

if ($matchAtual.Success) {
    $novoConteudo = [regex]::Replace(
        $conteudoAtual,
        $regexBloco,
        $novoBlocoCompleto
    )
} else {
    Write-Host "   ERRO: Marcadores // HORARIOS_SYNC_START e // HORARIOS_SYNC_END nao encontrados em dados_escola.js!" -ForegroundColor Red
    exit 1
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllText($DadosEscolaPath, $novoConteudo, $utf8NoBom)
Write-Host "   dados_escola.js atualizado com sucesso!" -ForegroundColor Green

# 4. Resumo
Write-Host ""
Write-Host "4) Professores sincronizados:" -ForegroundColor Yellow
foreach ($prof in $novoHorario) {
    $discStr = ($prof.Disciplinas -join ', ')
    $nDias   = @($prof.Horarios).Count
    Write-Host "   * $($prof.Nome) | $discStr | $nDias dia(s)"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Grava log
$logPath = Join-Path $PSScriptRoot "sync_horarios.log"
$logMsg  = "[$dataHora] Sync OK. $($novoHorario.Count) professores. Alteracoes: $($hashAtual -ne (Get-TextHash "horarioProfessores: $novoBloco") )"
Add-Content -Path $logPath -Value $logMsg -Encoding UTF8
Write-Host "Log salvo em: $logPath" -ForegroundColor Gray
Write-Host ""
