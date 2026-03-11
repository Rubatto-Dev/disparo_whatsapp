param(
    [string]$CsvPath = "C:\Users\Guilherme - Hogar\Desktop\agents\disparo_whatsapp\saida\planilha_mestre_segmentada.csv",
    [string]$XlsxPath = "C:\Users\Guilherme - Hogar\Desktop\agents\disparo_whatsapp\saida\planilha_mestre_segmentada_visual.xlsx"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $CsvPath)) {
    throw "CSV nao encontrado: $CsvPath"
}

$rows = Import-Csv -Path $CsvPath -Delimiter ","
if ($rows.Count -eq 0) {
    throw "CSV sem dados: $CsvPath"
}

$headers = @($rows[0].PSObject.Properties.Name)
$colCount = $headers.Count
$dataCount = $rows.Count
$totalRows = $dataCount + 1

if ($colCount -lt 2) {
    throw "CSV parece mal estruturado (menos de 2 colunas detectadas)."
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.ScreenUpdating = $false

$workbook = $null
$worksheet = $null

function Get-ColumnIndex {
    param(
        [object]$Sheet,
        [string]$Header
    )

    $used = $Sheet.UsedRange
    $cols = $used.Columns.Count

    for ($c = 1; $c -le $cols; $c++) {
        $val = [string]$Sheet.Cells.Item(1, $c).Value2
        if ($val -eq $Header) {
            return $c
        }
    }

    return 0
}

try {
    $workbook = $excel.Workbooks.Add()
    $worksheet = $workbook.Worksheets.Item(1)
    $worksheet.Name = "Leads"

    for ($c = 0; $c -lt $colCount; $c++) {
        $worksheet.Cells.Item(1, $c + 1).Value2 = [string]$headers[$c]
    }

    $chunkSize = 500
    for ($offset = 0; $offset -lt $dataCount; $offset += $chunkSize) {
        $count = [Math]::Min($chunkSize, $dataCount - $offset)
        $matrix = New-Object 'object[,]' $count, $colCount

        for ($r = 0; $r -lt $count; $r++) {
            $rowObj = $rows[$offset + $r]
            for ($c = 0; $c -lt $colCount; $c++) {
                $header = $headers[$c]
                $val = $rowObj.$header
                if ($null -eq $val) { $val = "" }
                $matrix[$r, $c] = [string]$val
            }
        }

        $startRow = 2 + $offset
        $endRow = $startRow + $count - 1
        $targetRange = $worksheet.Range(
            $worksheet.Cells.Item($startRow, 1),
            $worksheet.Cells.Item($endRow, $colCount)
        )
        $targetRange.Value2 = $matrix
    }

    $lastCell = $worksheet.Cells.Item($totalRows, $colCount)
    $range = $worksheet.Range($worksheet.Cells.Item(1, 1), $lastCell)

    $listObject = $worksheet.ListObjects.Add(1, $range, $null, 1)
    $listObject.Name = "tblLeadsSegmentados"
    $listObject.TableStyle = "TableStyleMedium2"

    $headerRange = $worksheet.Range($worksheet.Cells.Item(1, 1), $worksheet.Cells.Item(1, $colCount))
    $headerRange.Font.Bold = $true
    $headerRange.Font.Color = 16777215
    $headerRange.Interior.Color = 11842740
    $worksheet.Rows.Item(1).RowHeight = 26

    $worksheet.Activate() | Out-Null
    $excel.ActiveWindow.SplitColumn = 1
    $excel.ActiveWindow.SplitRow = 1
    $excel.ActiveWindow.FreezePanes = $true

    $worksheet.Columns.AutoFit() | Out-Null
    for ($c = 1; $c -le $colCount; $c++) {
        $width = $worksheet.Columns.Item($c).ColumnWidth
        if ($width -lt 12) {
            $worksheet.Columns.Item($c).ColumnWidth = 12
        }
        if ($width -gt 42) {
            $worksheet.Columns.Item($c).ColumnWidth = 42
        }
    }

    $longCols = @("grupos_origem", "arquivos_origem", "oportunidade_recomendada", "motivo_bloqueio")
    foreach ($colName in $longCols) {
        $idx = Get-ColumnIndex -Sheet $worksheet -Header $colName
        if ($idx -gt 0) {
            $target = $worksheet.Range($worksheet.Cells.Item(2, $idx), $worksheet.Cells.Item($totalRows, $idx))
            $target.WrapText = $true
            $worksheet.Columns.Item($idx).ColumnWidth = 36
        }
    }

    $dataRange = $worksheet.Range($worksheet.Cells.Item(2, 1), $worksheet.Cells.Item($totalRows, $colCount))
    $dataRange.VerticalAlignment = -4108

    $idxPode = Get-ColumnIndex -Sheet $worksheet -Header "pode_disparar"
    if ($idxPode -gt 0) {
        $rngPode = $worksheet.Range($worksheet.Cells.Item(2, $idxPode), $worksheet.Cells.Item($totalRows, $idxPode))
        $fc1 = $rngPode.FormatConditions.Add(1, 3, '="1"')
        $fc1.Interior.Color = 13434879
        $fc1.Font.Color = 32512

        $fc2 = $rngPode.FormatConditions.Add(1, 3, '="0"')
        $fc2.Interior.Color = 13421823
        $fc2.Font.Color = 192
    }

    $idxOwner = Get-ColumnIndex -Sheet $worksheet -Header "origem_responsavel"
    if ($idxOwner -gt 0) {
        $rngOwner = $worksheet.Range($worksheet.Cells.Item(2, $idxOwner), $worksheet.Cells.Item($totalRows, $idxOwner))
        $fr = $rngOwner.FormatConditions.Add(1, 3, '="Rhuan"')
        $fr.Interior.Color = 15987699

        $fh = $rngOwner.FormatConditions.Add(1, 3, '="Hugo"')
        $fh.Interior.Color = 10092543

        $fe = $rngOwner.FormatConditions.Add(1, 3, '="Equipe Hogar"')
        $fe.Interior.Color = 15790320
    }

    $listSep = [string]$excel.International(5)
    $validations = @(
        @{ Header = "origem_responsavel"; Values = @("Rhuan", "Hugo", "Equipe Hogar") },
        @{ Header = "ticket_segmento"; Values = @("nao_informado", "entrada", "medio", "premium", "premium_plus") },
        @{ Header = "perfil_grupo"; Values = @("geral", "morador", "investidor", "parceiro", "luxo") },
        @{ Header = "status_lead"; Values = @("novo", "contatado", "respondeu", "nao_interessado") },
        @{ Header = "prioridade_envio"; Values = @("alta", "media", "baixa") },
        @{ Header = "pode_disparar"; Values = @("1", "0") }
    )

    foreach ($cfg in $validations) {
        $idx = Get-ColumnIndex -Sheet $worksheet -Header $cfg.Header
        if ($idx -gt 0) {
            $rng = $worksheet.Range($worksheet.Cells.Item(2, $idx), $worksheet.Cells.Item($totalRows, $idx))
            $rng.Validation.Delete() | Out-Null
            $formula = [string]::Join($listSep, $cfg.Values)
            $rng.Validation.Add(3, 1, 1, $formula) | Out-Null
            $rng.Validation.IgnoreBlank = $true
            $rng.Validation.InCellDropdown = $true
        }
    }

    $guide = $workbook.Worksheets.Add()
    $guide.Name = "Instrucoes"
    $guide.Columns.Item(1).ColumnWidth = 120

    $guide.Cells.Item(1, 1).Value2 = "Guia rapido - Preenchimento da planilha segmentada"
    $guide.Cells.Item(1, 1).Font.Bold = $true
    $guide.Cells.Item(1, 1).Font.Size = 15

    $guide.Cells.Item(3, 1).Value2 = "1) Priorize preencher: grupo_principal, origem_responsavel, ticket_interesse, ticket_segmento e perfil_grupo."
    $guide.Cells.Item(4, 1).Value2 = "2) Use pode_disparar=0 para bloquear contato sensivel (admin, sem contexto, duvida de origem)."
    $guide.Cells.Item(5, 1).Value2 = "3) status_lead deve ser atualizado apos retorno comercial."
    $guide.Cells.Item(6, 1).Value2 = "4) Evite mensagem repetida: personalize por grupo + contexto + oportunidade."
    $guide.Cells.Item(7, 1).Value2 = "5) Anti-ban: manter cadencia e revisar grupos antes de liberar lote real."
    $guide.Range("A3:A7").WrapText = $true

    $workbook.Worksheets.Item("Leads").Activate() | Out-Null

    if (Test-Path $XlsxPath) {
        Remove-Item -Path $XlsxPath -Force
    }

    $xlOpenXMLWorkbook = 51
    $workbook.SaveAs($XlsxPath, $xlOpenXMLWorkbook)

    Write-Output "Arquivo visual gerado: $XlsxPath"
    Write-Output "Colunas detectadas e gravadas: $colCount"
    Write-Output "Linhas detectadas e gravadas: $dataCount"
}
finally {
    if ($workbook -ne $null) {
        $workbook.Close($true)
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
    }
    if ($worksheet -ne $null) {
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($worksheet) | Out-Null
    }

    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}