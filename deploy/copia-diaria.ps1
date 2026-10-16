<#
.SYNOPSIS
    Baja al portatil la copia diaria del bot en papel de Ebisu (P6) y guarda solo las de los ultimos 7 dias.

.DESCRIPTION
    Adaptado de deploy/daily-backup.ps1 de Ploutos (solo lectura de Ploutos):
      * por SSH (sin preguntar nunca: BatchMode) desde el alias de ~/.ssh/config; si no conecta, el alias alternativo
        (Tailscale). Ninguna IP en este fichero: el repositorio es publico;
      * comprueba que la copia se abre (tar -tzf) antes de darla por buena;
      * borra las de mas de 7 dias (decision del propietario, 15/10/2026);
      * si falla, lo reintenta 3 veces con 1 minuto entre intento e intento (el portatil puede despertarse sin red);
      * un fallo suelto NO avisa (decision del propietario, 16/10/2026: nada de falsos avisos): queda en el registro y la
        tarea lo reintenta cada hora. Solo en el ultimo intento del dia (desde -UltimaHora, 23:00) avisa por Telegram,
        UNA vez (lee TELEGRAM_TOKEN y TELEGRAM_CHAT_ID del .env de Ebisu del portatil; nunca escribe el token);
      * latido a Healthchecks solo cuando sale bien (comprobacion ebisu-copia-portatil, HEALTHCHECK_EBISU_COPIA_PORTATIL,
        la UNICA URL de Healthchecks del .env del portatil): si en dos dias no hay copia buena, avisa Healthchecks
        aunque el portatil este apagado;
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
    [string] $UltimaHora = '23:00',
    [int] $Intentos = 3,
    [int] $EsperaSegundos = 60,
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

# El latido de la copia del portatil. La URL es secreta (quien la tenga puede tapar una caida).
function Send-Latido {
    $url = Read-Env 'HEALTHCHECK_EBISU_COPIA_PORTATIL'
    if (-not $url) { Write-Log '(sin HEALTHCHECK_EBISU_COPIA_PORTATIL en .env: no se late)'; return }
    try { Invoke-RestMethod -Method Get -Uri $url -TimeoutSec 10 | Out-Null; Write-Log 'latido enviado a Healthchecks' }
    catch { Write-Log 'AVISO: no se pudo latir a Healthchecks' }
}

$ssh = 'C:\Windows\System32\OpenSSH\ssh.exe'; $scp = 'C:\Windows\System32\OpenSSH\scp.exe'  # el que ve el agente
$opts = @('-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')

function Get-Copia([string] $Host_) {
    $ErrorActionPreference = 'Continue'
    # Toda la salida primero y despues el nombre: con `| Select-Object -First 1` PowerShell cortaba ssh en cuanto llegaba
    # la primera linea y, a veces, ssh salia con error aunque la copia estuviera (fallo intermitente, 16/10/2026).
    $salida = @(& $ssh @opts $Host_ "ls -1t /var/backups/ebisu/ebisu-*.tar.gz 2>/dev/null | head -1" 2>&1)
    if ($LASTEXITCODE -ne 0) { return $null }
    $nombre = $salida | ForEach-Object { "$_".Trim() } | Where-Object { $_ -match '^/var/backups/ebisu/ebisu-\d{4}-\d{2}-\d{2}\.tar\.gz$' } |
        Select-Object -First 1
    if (-not $nombre) { return $null }
    $local = Join-Path $destino (Split-Path -Leaf "$nombre")
    & $scp -q @opts "${Host_}:$nombre" $local 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { return $null }
    return $local
}

Write-Log "--- copia de Ebisu ---"
try {
    $copia = $null
    for ($i = 1; $i -le $Intentos -and -not $copia; $i++) {
        if ($i -gt 1) { Write-Log "(intento $i de $Intentos dentro de $EsperaSegundos s)"; Start-Sleep -Seconds $EsperaSegundos }
        $copia = Get-Copia $Target
        if (-not $copia -and $TargetAlternativo) { Write-Log "(sin copia por '$Target'; se prueba '$TargetAlternativo')"; $copia = Get-Copia $TargetAlternativo }
    }
    if (-not $copia) { throw 'no se pudo bajar la copia (SSH o no hay copias en el VPS)' }
    & tar -tzf $copia | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "la copia $copia no se abre" }
    $fecha = [datetime]::ParseExact(([regex]::Match($copia, '\d{4}-\d{2}-\d{2}')).Value, 'yyyy-MM-dd', $null)
    if (((Get-Date) - $fecha).TotalDays -gt 2) { throw "la copia mas reciente del VPS es del $($fecha.ToString('dd/MM/yyyy'))" }
    Get-ChildItem $destino -Filter 'ebisu-*.tar.gz' | Sort-Object Name -Descending | Select-Object -Skip $Dias | Remove-Item -Force
    Set-Content -Path $ultimaOk -Value $hoy -Encoding ascii
    Write-Log "OK: $(Split-Path -Leaf $copia); se guardan las de los ultimos $Dias dias"
    Send-Latido
    exit 0
} catch {
    Write-Log "FALLO: $($_.Exception.Message)"
    if ((Get-Date) -ge [datetime]::ParseExact($UltimaHora, 'HH:mm', $null)) {
        Send-Fallo "Ebisu: hoy no se ha podido bajar la copia de seguridad diaria al portatil: $($_.Exception.Message). Manyana se vuelve a intentar desde las $Desde."
    } else { Write-Log '(sin avisar: la tarea lo reintenta cada hora; solo avisa el ultimo intento del dia)' }
    exit 1
}
