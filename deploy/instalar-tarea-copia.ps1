<#
.SYNOPSIS
    Registra (o quita) la tarea programada de Windows que baja cada dia la copia de Ebisu (P6). La lanza el propietario.

.DESCRIPTION
    Como la de Ploutos: para TU usuario y solo con la sesion iniciada (asi no se guarda ninguna contrasenya y el SSH ve
    tu clave). A las $At, cada hora hasta medianoche, al iniciar sesion y al desbloquear, siempre con -SoloSiFalta.

.EXAMPLE
    .\deploy\instalar-tarea-copia.ps1
    .\deploy\instalar-tarea-copia.ps1 -Remove
#>

[CmdletBinding()]
param([string] $At = '12:00', [string] $Target = 'ploutos', [string] $TargetAlternativo = 'ploutos-ts', [switch] $Remove)

$ErrorActionPreference = 'Stop'
$taskName = 'Ebisu - copia de seguridad diaria'

if ($Remove) {
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false; Write-Output "Tarea eliminada: $taskName"
    } else { Write-Output "No existe la tarea: $taskName" }
    exit 0
}

$repo = Split-Path -Parent $PSScriptRoot
$script = Join-Path $PSScriptRoot 'copia-diaria.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -WorkingDirectory $repo `
    -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$script`" -Target $Target -TargetAlternativo $TargetAlternativo -SoloSiFalta -Desde $At"
$usuario = "$env:USERDOMAIN\$env:USERNAME"
$diaria = New-ScheduledTaskTrigger -Daily -At $At
$horas = 24 - [datetime]::ParseExact($At, 'HH:mm', $null).Hour
$diaria.Repetition = (New-ScheduledTaskTrigger -Once -At $At -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Hours $horas -Minutes -1)).Repetition
$alEntrar = New-ScheduledTaskTrigger -AtLogOn -User $usuario
$clase = Get-CimClass -Namespace 'Root/Microsoft/Windows/TaskScheduler' -ClassName 'MSFT_TaskSessionStateChangeTrigger'
$alDesbloquear = New-CimInstance -CimClass $clase -ClientOnly -Property @{ StateChange = 8; UserId = $usuario }
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $usuario -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($diaria, $alEntrar, $alDesbloquear) `
    -Settings $settings -Principal $principal -Force `
    -Description 'Baja la copia diaria del bot en papel de Ebisu desde el VPS, comprueba que se abre y guarda 7 dias.' | Out-Null
Write-Output "Tarea registrada: $taskName (a las $At, cada hora hasta medianoche; solo si la de hoy aun no salio bien)"
Write-Output "Registro: var\copia-ebisu.log. Probarla: Start-ScheduledTask -TaskName '$taskName'"
