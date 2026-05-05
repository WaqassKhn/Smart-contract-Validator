param(
    [string]$InputMarkdown = "docs/research_paper_ieee_draft.md",
    [string]$OutputDocx = "docs/AI_Smart_Contract_Risk_Explainer_IEEE_Paper.docx"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Escape-XmlText {
    param([string]$Text)
    if ($null -eq $Text) { return "" }
    $escaped = [System.Security.SecurityElement]::Escape($Text)
    return $escaped -replace "`r?`n", " "
}

function New-RunXml {
    param(
        [string]$Text,
        [bool]$Bold = $false,
        [bool]$Italic = $false,
        [string]$Size = "20"
    )

    $rPrParts = @("<w:rFonts w:ascii=""Times New Roman"" w:hAnsi=""Times New Roman"" w:cs=""Times New Roman""/>", "<w:sz w:val=""$Size""/>", "<w:szCs w:val=""$Size""/>")
    if ($Bold) { $rPrParts += "<w:b/>" }
    if ($Italic) { $rPrParts += "<w:i/>" }

    $escaped = Escape-XmlText $Text
    return "<w:r><w:rPr>$($rPrParts -join '')</w:rPr><w:t xml:space=""preserve"">$escaped</w:t></w:r>"
}

function New-ParagraphXml {
    param(
        [string]$Text,
        [ValidateSet("title","author","heading1","heading2","normal","abstract","keywords","bullet","reference")]
        [string]$Kind = "normal",
        [bool]$SectionBreakAfter = $false
    )

    $jc = "both"
    $spacingBefore = "0"
    $spacingAfter = "120"
    $ind = "<w:ind w:firstLine=""360""/>"
    $runSize = "20"
    $bold = $false
    $italic = $false

    switch ($Kind) {
        "title" {
            $jc = "center"
            $spacingBefore = "0"
            $spacingAfter = "180"
            $ind = ""
            $runSize = "28"
            $bold = $true
        }
        "author" {
            $jc = "center"
            $spacingAfter = "60"
            $ind = ""
            $runSize = "20"
        }
        "heading1" {
            $jc = "left"
            $spacingBefore = "160"
            $spacingAfter = "80"
            $ind = ""
            $runSize = "20"
            $bold = $true
        }
        "heading2" {
            $jc = "left"
            $spacingBefore = "120"
            $spacingAfter = "60"
            $ind = ""
            $runSize = "20"
            $bold = $true
            $italic = $true
        }
        "abstract" {
            $jc = "both"
            $spacingAfter = "120"
            $ind = ""
            $runSize = "20"
        }
        "keywords" {
            $jc = "both"
            $spacingAfter = "120"
            $ind = ""
            $runSize = "20"
        }
        "bullet" {
            $jc = "both"
            $spacingAfter = "60"
            $ind = "<w:ind w:left=""360"" w:hanging=""180""/>"
            $runSize = "20"
            $Text = "• " + $Text
        }
        "reference" {
            $jc = "both"
            $spacingAfter = "60"
            $ind = "<w:ind w:left=""360"" w:hanging=""360""/>"
            $runSize = "18"
        }
    }

    $sectPr = ""
    if ($SectionBreakAfter) {
        $sectPr = @"
<w:sectPr>
  <w:type w:val="continuous"/>
  <w:pgSz w:w="12240" w:h="15840"/>
  <w:pgMar w:top="1080" w:right="900" w:bottom="1080" w:left="900" w:header="720" w:footer="720" w:gutter="0"/>
  <w:cols w:num="1"/>
</w:sectPr>
"@
    }

    $runXml = New-RunXml -Text $Text -Bold:$bold -Italic:$italic -Size $runSize
    return "<w:p><w:pPr><w:jc w:val=""$jc""/><w:spacing w:before=""$spacingBefore"" w:after=""$spacingAfter""/>$ind$sectPr</w:pPr>$runXml</w:p>"
}

$markdownPath = Join-Path (Get-Location) $InputMarkdown
if (-not (Test-Path $markdownPath)) {
    throw "Input markdown not found: $markdownPath"
}

$lines = Get-Content $markdownPath
$paragraphs = New-Object System.Collections.Generic.List[string]
$beforeFirstHeading = $true

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i].TrimEnd()
    if ([string]::IsNullOrWhiteSpace($line)) { continue }

    if ($line.StartsWith("# ")) {
        $paragraphs.Add((New-ParagraphXml -Text $line.Substring(2) -Kind "title"))
        continue
    }

    if ($line.StartsWith("## ")) {
        $beforeFirstHeading = $false
        $headingText = $line.Substring(3)
        $sectionBreak = $false
        if ($headingText -eq "I. INTRODUCTION") {
            $lastIndex = $paragraphs.Count - 1
            if ($lastIndex -ge 0) {
                $paragraphs[$lastIndex] = New-ParagraphXml -Text (($lines[$i - 1]).Trim()) -Kind "keywords" -SectionBreakAfter:$true
            }
        }
        $paragraphs.Add((New-ParagraphXml -Text $headingText -Kind "heading1"))
        continue
    }

    if ($line.StartsWith("### ")) {
        $paragraphs.Add((New-ParagraphXml -Text $line.Substring(4) -Kind "heading2"))
        continue
    }

    if ($line.StartsWith("- ")) {
        $paragraphs.Add((New-ParagraphXml -Text $line.Substring(2) -Kind "bullet"))
        continue
    }

    if ($line -match '^\[\d+\]') {
        $paragraphs.Add((New-ParagraphXml -Text $line -Kind "reference"))
        continue
    }

    if ($beforeFirstHeading) {
        $paragraphs.Add((New-ParagraphXml -Text $line -Kind "author"))
        continue
    }

    if ($line.StartsWith("Index Terms—")) {
        $paragraphs.Add((New-ParagraphXml -Text $line -Kind "keywords"))
        continue
    }

    if ($line.StartsWith("Abstract")) {
        $paragraphs.Add((New-ParagraphXml -Text $line -Kind "abstract"))
        continue
    }

    $paragraphs.Add((New-ParagraphXml -Text $line -Kind "normal"))
}

$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
  <w:body>
    $($paragraphs -join "`n")
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1080" w:right="900" w:bottom="1080" w:left="900" w:header="720" w:footer="720" w:gutter="0"/>
      <w:cols w:num="2" w:space="720"/>
    </w:sectPr>
  </w:body>
</w:document>
"@

$stylesXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="20"/>
        <w:szCs w:val="20"/>
        <w:lang w:val="en-US"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="120"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
</w:styles>
"@

$contentTypesXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"@

$relsXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"@

$documentRelsXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"@

$created = (Get-Date).ToUniversalTime().ToString("s") + "Z"
$coreXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>AI Smart Contract Risk Explainer IEEE Research Paper Draft</dc:title>
  <dc:creator>OpenAI Codex</dc:creator>
  <cp:lastModifiedBy>OpenAI Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">$created</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">$created</dcterms:modified>
</cp:coreProperties>
"@

$appXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office Word</Application>
</Properties>
"@

$outputPath = Join-Path (Get-Location) $OutputDocx
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("ieee-docx-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tempRoot "_rels") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tempRoot "docProps") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tempRoot "word") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tempRoot "word\_rels") | Out-Null

[System.IO.File]::WriteAllText((Join-Path $tempRoot "[Content_Types].xml"), $contentTypesXml, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $tempRoot "_rels\.rels"), $relsXml, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $tempRoot "docProps\core.xml"), $coreXml, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $tempRoot "docProps\app.xml"), $appXml, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $tempRoot "word\document.xml"), $documentXml, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $tempRoot "word\styles.xml"), $stylesXml, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $tempRoot "word\_rels\document.xml.rels"), $documentRelsXml, [System.Text.UTF8Encoding]::new($false))

$zipPath = [System.IO.Path]::ChangeExtension($outputPath, ".zip")
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
if (Test-Path $outputPath) { Remove-Item $outputPath -Force }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($tempRoot, $zipPath)
Move-Item $zipPath $outputPath
Remove-Item $tempRoot -Recurse -Force

Write-Output "Created $outputPath"
