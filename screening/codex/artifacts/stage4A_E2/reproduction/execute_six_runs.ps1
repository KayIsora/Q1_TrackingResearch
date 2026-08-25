$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$SourceRoot = 'E:\Robot_Backup\tmp\stage4A_R_official_source'
$Q1Root = 'E:\Robot_Backup\Embodied-Tracking-Problem-Research'
$Inventory = Join-Path $Q1Root 'screening\codex\2026-08-25_stage4A_E2_slice_inventory.csv'
$Python = 'E:\Robot_Backup\tmp\stage2B_spiketrack_env\Scripts\python.exe'
$Checkpoint = 'E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar'
$Config = Join-Path $SourceRoot 'experiments\spiketrack\spiketrack_s256_t1.yaml'
$E2Root = 'F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1'
$AcquiredRoot = Join-Path $E2Root 'extracted\OTB2015'
$ResultBase = Join-Path $E2Root 'stage4a_e2_results'
$MiniRoot = Join-Path $ResultBase 'evaluator_otb3'
$Support = Join-Path $ResultBase 'runner_support'
$RunBase = Join-Path $ResultBase 'runs'
$Logs = Join-Path $ResultBase 'logs'
$ContractPath = Join-Path $Support 'predeclared_six_run_contract.csv'
$InitialContract = Join-Path $Support 'predeclared_six_run_contract.initial.csv'
$PreconditionsPath = Join-Path $Support 'run_preconditions.csv'
$RunManifestPath = Join-Path $Support 'run_execution_manifest.csv'
$SourceLocal = Join-Path $SourceRoot 'lib\test\evaluation\local.py'
$StagedLocal = Join-Path $Support 'local.py'
$PreservedLocal = Join-Path $Support 'preserved_stage4A_R_source_local.py'
$DeterministicRoot = Join-Path $Support 'deterministic'
$SiteCustomize = Join-Path $DeterministicRoot 'sitecustomize.py'

$PinnedCommit = '1537db51a1cc9f6e30cce469fba3e51f5721b3d0'
$InventorySha = '8cd2ab115a361fb99afd24a1aa6e1bc1931c48de3ed050fb3f53893d2a32bcc6'
$ConfigSha = '9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8'
$CheckpointSha = 'cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df'
$OriginalLocalSha = 'e76f5713bac3f31b3b587f4fe869aea25aeceeab5cb45b2800c46a76d7aff6fb'
$StagedLocalSha = '0406f9c440acdb0e572f20fc951a5d1f50dd49c0c851f43658db2e41f9bdd493'
$SiteCustomizeSha = '56284cd8e1fd12ec564f460714f787dcd71c91a1550fb616be34da457aabaee1'
$ExpectedRows = @{ Deer = 71; Crossing = 120; Couple = 140 }
$ExpectedOrder = @(
    'official_default|Deer',
    'official_default|Crossing',
    'official_default|Couple',
    'deterministic|Deer',
    'deterministic|Crossing',
    'deterministic|Couple'
)
$GroundTruthSha = @{
    Deer = 'f22bd21c55d23f24371993e4e5f36b09b744a204953a7de4654e99358900ad59'
    Crossing = '3588d1821b80f8bc7f88645cbfca32454d474135d7841f85b304615fecf54ac4'
    Couple = '43c6d304f9f65b28940389429dfdbd33e544075c6b8d3c00e0c72558dac55d10'
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Write-Rows([string]$Path, [System.Collections.ArrayList]$Rows) {
    if ($Rows.Count -eq 0) { return }
    $Rows | Export-Csv -LiteralPath $Path -NoTypeInformation -Encoding utf8
}

# Revalidate the independent inventory gate before touching runtime state.
if ((Get-Sha256 $Inventory) -ne $InventorySha) { throw 'Inventory SHA-256 changed after blind gate' }
$InventoryRows = @(Import-Csv -LiteralPath $Inventory)
if ($InventoryRows.Count -ne 100) { throw 'Inventory does not contain exactly 100 records' }
if (@($InventoryRows.sequence | Sort-Object -Unique).Count -ne 100) { throw 'Inventory sequence names are not unique' }
if (@($InventoryRows | Where-Object { $_.manager_review_status -ne 'PENDING' }).Count -ne 0) { throw 'Inventory review status is not uniformly PENDING' }

if ((git -C $SourceRoot rev-parse HEAD) -ne $PinnedCommit) { throw 'Pinned source HEAD mismatch' }
git -C $SourceRoot diff --quiet
if ($LASTEXITCODE -ne 0) { throw 'Pinned source has a tracked diff' }
if ((Get-Sha256 $Config) -ne $ConfigSha) { throw 'Config SHA-256 mismatch' }
if ((Get-Sha256 $Checkpoint) -ne $CheckpointSha) { throw 'Checkpoint SHA-256 mismatch' }
if ((Get-Sha256 $SourceLocal) -ne $OriginalLocalSha) { throw 'Existing source local.py mismatch' }
if ((Get-Sha256 $PreservedLocal) -ne $OriginalLocalSha) { throw 'Preserved local.py mismatch' }
if ((Get-Sha256 $StagedLocal) -ne $StagedLocalSha) { throw 'Staged E2 local.py mismatch' }
if ((Get-Sha256 $SiteCustomize) -ne $SiteCustomizeSha) { throw 'Deterministic sitecustomize mismatch' }

$CopyVerification = @(Import-Csv -LiteralPath (Join-Path $Support 'real_copy_verification.csv'))
if ($CopyVerification.Count -ne 3) { throw 'Copy verification does not contain three records' }
if (@($CopyVerification | Where-Object { $_.verification_status -ne 'PASS' -or $_.all_file_sha256_identical -ne 'True' }).Count -ne 0) { throw 'Acquired-to-staged byte-copy verification failed' }
$MiniManifest = @(Import-Csv -LiteralPath (Join-Path $Support 'mini_root_manifest.csv'))
if ($MiniManifest.Count -ne 100) { throw 'Mini-root manifest does not contain 100 records' }
$RealMini = @($MiniManifest | Where-Object { [int]$_.real_image_count -gt 0 })
if ((($RealMini.sequence | Sort-Object) -join '|') -ne 'Couple|Crossing|Deer') { throw 'Mini-root real-image boundary failed' }

$Contract = @(Import-Csv -LiteralPath $ContractPath)
if ($Contract.Count -ne 6) { throw 'Run contract is not six rows' }
for ($i = 0; $i -lt 6; $i++) {
    if (("$($Contract[$i].mode)|$($Contract[$i].sequence)") -ne $ExpectedOrder[$i]) {
        throw "Run contract order mismatch at row $($i + 1)"
    }
    if ($Contract[$i].execution_status -ne 'PENDING_SECOND_AUTHORIZATION') {
        throw "Run contract was already used at row $($i + 1)"
    }
    if (Test-Path -LiteralPath $Contract[$i].save_root) {
        throw "HARD REFUSE silent reuse: $($Contract[$i].save_root)"
    }
}
if (Test-Path -LiteralPath $InitialContract) { throw 'Initial contract preservation file already exists' }
Copy-Item -LiteralPath $ContractPath -Destination $InitialContract

$Preconditions = [System.Collections.ArrayList]::new()
$ExecutionRows = [System.Collections.ArrayList]::new()
$RunFailure = $null

Copy-Item -LiteralPath $StagedLocal -Destination $SourceLocal -Force
if ((Get-Sha256 $SourceLocal) -ne $StagedLocalSha) { throw 'E2 local.py installation verification failed' }
git -C $SourceRoot diff --quiet
if ($LASTEXITCODE -ne 0) { throw 'Installing untracked local.py changed tracked source' }

try {
    foreach ($row in $Contract) {
        $mode = $row.mode
        $sequence = $row.sequence
        $runRoot = $row.save_root
        $resultPath = $row.prediction_path
        $timingPath = $row.timing_path
        $logPath = $row.log_path
        if (Test-Path -LiteralPath $runRoot) { throw "HARD REFUSE silent reuse: $runRoot" }
        New-Item -ItemType Directory -Path $runRoot | Out-Null

        $env:SPIKETRACK_STAGE4A_E2_OTB_ROOT = $MiniRoot
        $env:SPIKETRACK_STAGE4A_E2_SAVE_ROOT = $runRoot
        $env:PYTHONDONTWRITEBYTECODE = '1'
        Remove-Item Env:SPIKETRACK_STAGE4A_R_SAVE_ROOT -ErrorAction SilentlyContinue
        if ($mode -eq 'official_default') {
            Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
            Remove-Item Env:PYTHONHASHSEED -ErrorAction SilentlyContinue
            Remove-Item Env:CUBLAS_WORKSPACE_CONFIG -ErrorAction SilentlyContinue
            $runtimeContract = 'OFFICIAL_PROCESS_DEFAULTS_NO_FORCED_SEED'
        } else {
            $env:PYTHONPATH = $DeterministicRoot
            $env:PYTHONHASHSEED = '20260825'
            $env:CUBLAS_WORKSPACE_CONFIG = ':4096:8'
            $runtimeContract = 'LOCKED_SEED_20260825_DETERMINISTIC_SITE_CUSTOMIZE'
        }

        [void]$Preconditions.Add([pscustomobject]@{
            run_id = $row.run_id
            mode = $mode
            sequence = $sequence
            recorded_before_process_utc = (Get-Date).ToUniversalTime().ToString('o')
            source_head = (git -C $SourceRoot rev-parse HEAD)
            source_tracked_diff = 'CLEAN'
            source_dataset_path = (Join-Path $AcquiredRoot $sequence)
            staged_dataset_path = (Join-Path $MiniRoot $sequence)
            ground_truth_sha256 = $GroundTruthSha[$sequence]
            config_path = $Config
            config_sha256 = $ConfigSha
            checkpoint_path = $Checkpoint
            checkpoint_sha256 = $CheckpointSha
            python = $Python
            runtime_contract = $runtimeContract
            pythonpath = $(if ($null -eq $env:PYTHONPATH) { 'REMOVED' } else { $env:PYTHONPATH })
            pythonhashseed = $(if ($null -eq $env:PYTHONHASHSEED) { 'REMOVED' } else { $env:PYTHONHASHSEED })
            cublas_workspace_config = $(if ($null -eq $env:CUBLAS_WORKSPACE_CONFIG) { 'REMOVED' } else { $env:CUBLAS_WORKSPACE_CONFIG })
            command = $row.command
            save_root = $runRoot
            prediction_path = $resultPath
            timing_path = $timingPath
            log_path = $logPath
        })
        Write-Rows $PreconditionsPath $Preconditions
        $row.execution_status = 'RUNNING'
        $Contract | Export-Csv -LiteralPath $ContractPath -NoTypeInformation -Encoding utf8

        $start = (Get-Date).ToUniversalTime()
        Push-Location $SourceRoot
        try {
            & $Python -B .\tracking\test.py spiketrack spiketrack_s256_t1 `
                --dataset_name otb `
                --sequence $sequence `
                --debug 0 `
                --threads 0 `
                --num_gpus 1 `
                --checkpoint_path $Checkpoint `
                --inference_mode True `
                --save_sfr False 2>&1 | Tee-Object -FilePath $logPath
            $exitCode = $LASTEXITCODE
        } finally {
            Pop-Location
        }
        $end = (Get-Date).ToUniversalTime()
        if ($exitCode -ne 0) { throw "$mode/$sequence exited $exitCode" }
        if (-not (Test-Path -LiteralPath $resultPath)) { throw "$mode/$sequence result missing" }
        if (-not (Test-Path -LiteralPath $timingPath)) { throw "$mode/$sequence time file missing" }
        $resultRows = @(Get-Content -LiteralPath $resultPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
        $timeRows = @(Get-Content -LiteralPath $timingPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
        if ($resultRows -ne $ExpectedRows[$sequence]) { throw "$mode/$sequence result rows $resultRows" }
        if ($timeRows -ne $ExpectedRows[$sequence]) { throw "$mode/$sequence time rows $timeRows" }

        [void]$ExecutionRows.Add([pscustomobject]@{
            run_id = $row.run_id
            mode = $mode
            sequence = $sequence
            start_utc = $start.ToString('o')
            end_utc = $end.ToString('o')
            exit_code = $exitCode
            prediction_path = $resultPath
            prediction_sha256 = Get-Sha256 $resultPath
            prediction_rows = $resultRows
            timing_path = $timingPath
            timing_rows = $timeRows
            validation_status = 'PASS'
            interpretation_boundary = 'TIMING_RETAINED_EXTERNALLY_NOT_A_SPEED_CLAIM'
        })
        Write-Rows $RunManifestPath $ExecutionRows
        $row.execution_status = 'COMPLETE_VALIDATED'
        $Contract | Export-Csv -LiteralPath $ContractPath -NoTypeInformation -Encoding utf8
        Write-Output "E2_RUN_COMPLETE $mode $sequence rows=$resultRows"
    }
} catch {
    $RunFailure = $_
    throw
} finally {
    Copy-Item -LiteralPath $PreservedLocal -Destination $SourceLocal -Force
    $restoredHash = Get-Sha256 $SourceLocal
    if ($restoredHash -ne $OriginalLocalSha) {
        Write-Error "FATAL: source local.py restore hash $restoredHash"
    }
    git -C $SourceRoot diff --quiet
    if ($LASTEXITCODE -ne 0) { Write-Error 'FATAL: tracked source diff after restore' }
    Remove-Item Env:SPIKETRACK_STAGE4A_E2_OTB_ROOT -ErrorAction SilentlyContinue
    Remove-Item Env:SPIKETRACK_STAGE4A_E2_SAVE_ROOT -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONHASHSEED -ErrorAction SilentlyContinue
    Remove-Item Env:CUBLAS_WORKSPACE_CONFIG -ErrorAction SilentlyContinue
    Write-Output "SOURCE_LOCAL_RESTORED sha256=$restoredHash"
}

Write-Output 'E2_SIX_RUN_EXECUTION=PASS'
