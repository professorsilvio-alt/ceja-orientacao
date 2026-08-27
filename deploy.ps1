# deploy.ps1
# Script auxiliar para fazer Git Add, Commit, Push e disparar o Deploy Automatico

param(
    [string]$Mensagem = "Atualizacao automatica - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 🚀 CEJA - Deploy e Sincronizacao"       -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Git Add
Write-Host "1) Adicionando alteracoes (git add .)..." -ForegroundColor Yellow
git add .

# 2. Git Commit
Write-Host "2) Criando commit..." -ForegroundColor Yellow
git commit -m "$Mensagem"

# 3. Git Pull
Write-Host "3) Verificando atualizacoes no GitHub (git pull)..." -ForegroundColor Yellow
git pull origin main --rebase

# 4. Git Push
Write-Host "4) Enviando para o GitHub (git push origin main)..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " ✅ Push concluido com sucesso!"          -ForegroundColor Green
Write-Host " O GitHub Actions iniciara o Deploy automatico." -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
