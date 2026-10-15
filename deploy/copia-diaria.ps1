<#
.SYNOPSIS
    Baja al portatil la copia diaria del bot en papel de Ebisu (P6) y guarda solo las de los ultimos 7 dias.

.DESCRIPTION
    Adaptado de deploy/daily-backup.ps1 de Ploutos (solo lectura de Ploutos):
      * por SSH (sin preguntar nunca: BatchMode) desde el alias de ~/.ssh/config; si no conecta, el alias alternativo
        (Tailscale). Ninguna IP en este fichero: el repositorio es publico;
      * comprueba que la copia se abre (tar -tzf) antes de darla por buena;
      * borra las de mas de 7 dias (decision del propietario, 15/10/2026);
      * un fallo se avisa por Telegram UNA vez al dia (lee TELEGRAM_TOKEN y TELEGRAM_CHAT_ID del .env de Ebisu del
        portatil; nunca escribe el token en el registro);
      * con -SoloSiFalta no hace nada si la de hoy ya salio bien o si aun no es la hora (la tarea se lanza cada hora).

.EXAMPLE
    .\deploy\copia-diaria.ps1 -Target ploutos -TargetAlternativo ploutos-ts
#>

[CmdletBinding()]
param(
    [string] $Target = 'ploutos',
    [string] $TargetAlternativo = 'ploutos-ts',
    [switch] $SoloSiFalta,
    [string] $Desde = '12:00',
    [int] $Dias = 7
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$destino = Join-Path $repo 'var\copias-ebisu'
$log = Join-Path $repo 'var\copia-ebisu.log'
$ultimaOk = Join-Path $repo 'var\copia-ebisu-ultima-ok.txt'
$avisoFallo = Join-Path $repo 'var\copia-ebisu-aviso-fallo.txt'
New-Item -ItemType Directory -Force -Path $destino | Out-Null
$hoy = (Get-Date).ToString('yyyy-MM-dd')

function Read-Primera([string] $Path) { if (Test-Path $Path) { return (Get-Content $Path -TotalCount 1) } return $null }

if ($SoloSiFalta) {
    if ((Get-Date) -lt [datetime]::ParseExact($Desde, 'HH:mm', $null)) { exit 0 }
    if ((Read-Primera $ultimaOk) -eq $hoy) { exit 0 }
}

function Write-Log([string] $Message) {
    $line = "$((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')) $Message"
    Add-Content -Path $log -Value $line -Encoding utf8
    Write-Output $line
}

function Read-Env([string] $Name) {
    $envFile = Join-Path $repo '.env'
    if (-not (Test-Path $envFile)) { return $null }
    foreach ($line in Get-Content $envFile) { if ($line -match "^\s*$Name\s*=\s*(.+?)\s*$") { return $Matches[1] } }
    return $null
}

function Send-Fallo([string] $Text) {
    if ((Read-Primera $avisoFallo) -eq $hoy) { Write-Log '(fallo ya avisado hoy)'; return }
    Set-Content -Path $avisoFallo -Value $hoy -Encoding ascii
    $token = Read-Env 'TELEGRAM_TOKEN'; $chat = Read-Env 'TELEGRAM_CHAT_ID'
    if (-not $token -or -not $chat) { Write-Log 'AVISO: sin Telegram en .env'; return }
    try {
        Invoke-RestMethod -Method Post -Uri "https://api.telegram.org/bot$token/sendMessage" `
            -Body @{ chat_id = $chat; text = $Text } -TimeoutSec 15 | Out-Null
    } catch { Write-Log "AVISO: no se pudo avisar por Telegram ($($_.Exception.Message -replace [regex]::Escape($token), '***'))" }
}

$ssh = 'C:\Windows\System32\OpenSSH\ssh.exe'; $scp = 'C:\Windows\System32\OpenSSH\scp.exe'  # el que ve el agente
$opts = @('-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')

function Get-Copia([string] $Host_) {
    $ErrorActionPreference = 'Continue'
    $nombre = (& $ssh @opts $Host_ "ls -1t /var/backups/ebisu/ebisu-*.tar.gz 2>/dev/null | head -1" 2>&1 | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0 -or -not ("$nombre" -match 'ebisu-\d{4}-\d{2}-\d{2}\.tar\.gz$')) { return $null }
    $local = Join-Path $destino (Split-Path -Leaf "$nombre")
    & $scp -q @opts "${Host_}:$nombre" $local 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { return $null }
    return $local
}

Write-Log "--- copia de Ebisu ---"
try {
    $copia = Get-Copia $Target
    if (-not $copia -and $TargetAlternativo) { Write-Log "(sin copia por '$Target'; se prueba '$TargetAlternativo')"; $copia = Get-Copia $TargetAlternativo }
    if (-not $copia) { throw 'no se pudo bajar la copia (SSH o no hay copias en el VPS)' }
    & tar -tzf $copia | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "la copia $copia no se abre" }
    $fecha = [datetime]::ParseExact(([regex]::Match($copia, '\d{4}-\d{2}-\d{2}')).Value, 'yyyy-MM-dd', $null)
    if (((Get-Date) - $fecha).TotalDays -gt 2) { throw "la copia mas reciente del VPS es del $($fecha.ToString('dd/MM/yyyy'))" }
    Get-ChildItem $destino -Filter 'ebisu-*.tar.gz' | Sort-Object Name -Descending | Select-Object -Skip $Dias | Remove-Item -Force
    Set-Content -Path $ultimaOk -Value $hoy -Encoding ascii
    Write-Log "OK: $(Split-Path -Leaf $copia); se guardan las de los ultimos $Dias dias"
    exit 0
} catch {
    Write-Log "FALLO: $($_.Exception.Message)"
    Send-Fallo "Ebisu: la copia de seguridad diaria ha FALLADO: $($_.Exception.Message). Se reintenta cada hora."
    exit 1
}
