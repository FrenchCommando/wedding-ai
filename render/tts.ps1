Add-Type -AssemblyName System.Speech
$dir = Join-Path $PSScriptRoot "out"
$beats = Get-Content "$dir\beats.json" -Raw | ConvertFrom-Json
$syn = New-Object System.Speech.Synthesis.SpeechSynthesizer
$syn.SelectVoice("Microsoft Zira Desktop")
$syn.Rate = -1
$french = @("Marion", "Léa", "fiancée")
$voices = $syn.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }
$frVoice = if ($voices -contains "Microsoft Hortense Desktop") { "Microsoft Hortense Desktop" } else { "Microsoft Zira Desktop" }
"voices: $($voices -join ', ') / french: $frVoice"
$out = @()
$i = 0
foreach ($b in $beats) {
  $f = "$dir\b{0:d2}.wav" -f $i
  if ($b.t.StartsWith("[")) {
    $dur = 2.5
    # silence: 22050 Hz 16-bit mono
    $n = [int](22050 * $dur)
    $bytes = New-Object byte[] (44 + $n*2)
    $ms = New-Object System.IO.MemoryStream
    $bw = New-Object System.IO.BinaryWriter($ms)
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes("RIFF")); $bw.Write([int](36 + $n*2)); $bw.Write([System.Text.Encoding]::ASCII.GetBytes("WAVE"))
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes("fmt ")); $bw.Write([int]16); $bw.Write([int16]1); $bw.Write([int16]1); $bw.Write([int]22050); $bw.Write([int]44100); $bw.Write([int16]2); $bw.Write([int16]16)
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes("data")); $bw.Write([int]($n*2)); $bw.Write((New-Object byte[] ($n*2)))
    [IO.File]::WriteAllBytes($f, $ms.ToArray())
  } else {
    $text = [System.Security.SecurityElement]::Escape(($b.t -replace '“|”','"' -replace '’',"'" -replace '—',', '))
    # French words go to the French voice
    foreach ($w in $french) {
      $text = $text -replace "(?<![\w-])$([regex]::Escape($w))(?![\w-])", "<voice name=`"$frVoice`" xml:lang=`"fr-FR`">$w</voice>"
    }
    $ssml = "<speak version=`"1.0`" xmlns=`"http://www.w3.org/2001/10/synthesis`" xml:lang=`"en-US`"><voice name=`"Microsoft Zira Desktop`"><prosody rate=`"-10%`">$text</prosody></voice></speak>"
    $syn.SetOutputToWaveFile($f)
    $syn.SpeakSsml($ssml)
    $syn.SetOutputToNull()
    $len = (Get-Item $f).Length
    $dur = ($len - 44) / 44100.0   # David outputs 22050 Hz 16-bit mono
  }
  $out += [pscustomobject]@{ i=$i; s=$b.s; j=$b.j; t=$b.t; dur=[math]::Round($dur + 0.6, 3); file=$f }
  $i++
}
$out | ConvertTo-Json | Set-Content "$dir\timing.json" -Encoding utf8
"total: " + (($out | Measure-Object -Property dur -Sum).Sum)
