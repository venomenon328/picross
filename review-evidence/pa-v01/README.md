# P-A-V01 · befristete Originale für PR #546

Produkt-Head `3e2bcfbd590a38e1a74764c3a52e88668f20edbe`, Basis
`059bb003dc761e862b304957143b0dd45d92bb82`. Dieser Ref hat den Produkt-Head
als Elternstand, erhält **keinen Merge-PR** und wird nicht in den Produktbranch
übernommen. Empfänger: Eigentümerperson für P-A-M01 und unabhängiger Reviewer
für P-A-R01. Die Sichtung und endgültige Normfreigabe sind offen.

`manifest.json` bindet alle 32 Original-PNGs (47.743.541 Bytes), Bildgrößen,
SHA-256, native Messdaten, Normdateien, Rendererquellen und Enginebytes.
`native.json` enthält Geometrie und Displaykontext pro Bild. Die PNGs sind
unveränderte Godot-Viewportausgaben, keine Vorschaukopien oder Neukodierung.
`Fxx-small-board.png` / `-tokens.png`: 1280×720/UI125;
`Fxx-normal-board.png` / `-tokens.png`: 1920×1080/UI100.
Board und Panel sind je Familie zusammen zu lesen; die Panel-Farbfelder allein
genügen nicht. Native Schriftgrade 6 und 17/18 sind **tatsächlich gemessen**.
Das 720p-Ziffernmaß ist eine offengelegte Einschränkung, kein bestandener
Lesbarkeitstest. C1 bleibt auf den tatsächlichen Runtime-IDs 2/4.

`plan.json` und F01–F08 wurden vor Metrik-Tuning auf Plancommit
`1ac4d44a75af9a604bffcb985c0570954beea761` veröffentlicht. `hypothesis.md`
und `measurement-development.json` kamen vor F08-Auswertung auf
`0c740677931dc3e5f38631a94c7b0f91045b4a46` hinzu. Der Plan bleibt bytegleich.
`measurement-all.json` vergleicht unquantisierte binary64-Oklab-/Luminanzwerte;
`recalculated.json` ist der präzisierte Decimal80-/Ganzzahlvorschlag.
Das interne `positive_warning` in diesem temporären Vergleich heißt technisch
positiv **mit** Warnung, kein neues Produktionsfeld. Alle 47 Paarbefunde stimmen
zwischen H1 und Präzisierung überein. Keine empirischen Eigentümerlabels.

## Originalbytes abrufen und öffnen

Einen echten Git-Checkout dieses im Lieferkommentar festgelegten Belegcommits
verwenden oder die Originale binär von genau diesem Commit laden. Beispiel:

```powershell
git fetch origin review/488-pa-v01-originals
# Den vollständigen Belegcommit aus dem Lieferkommentar ausdrücklich verwenden.
git worktree add --detach <eigener-reviewpfad> <belegcommit>
```

Alternativ `download_originals.py <belegcommit> <neues-eigenes-ziel>` ausführen:
ein angemeldeter binärfähiger `gh api` lädt Manifest/PNGs über die Contents API
mit `Accept: application/vnd.github.raw+json`. Es prüft SHA-256/Bytes, PNG-CRCs,
IHDR und vollständige IDAT-Dekompression. Danach PNGs im eigenen Bildbetrachter
**öffnen** und bei 100 % sowie im Zusammenhang beurteilen. Eine GitHub-Vorschau
oder erfolgreicher Download ist kein persönliches Sichturteil. Über 1 MiB
liegende Originale nicht über den normalen textgebundenen Contents-Abruf laden;
ein leeres `content`-Feld bedeutet keinen Bildzugriff. Der Lieferkommentar
berichtet den tatsächlich getesteten Abrufweg und dessen Kontogrenzen.

## Einmalige Reproduktion

Python-Standardbibliothek, keine dauerhafte Testinstallation:

```powershell
py review-evidence/pa-v01/measure.py
py review-evidence/pa-v01/measure.py --held
py review-evidence/pa-v01/recalculate.py
```

Der erste Befehl überspringt F08; die dritte Rechnung hat eine eigene
Decimal80-Implementierung und vergleicht sämtliche quantisierten Koordinaten
mit der unabhängigen binary64-Rechnung. Sie prüft sieben S-Randproben,
zwei exakte q-Differenzen, Schwarz und alle 28 F07-Paare. Die Gleichheitsproben
sind Reduzertests, keine erfundenen sRGB-Gleichheitsfarben.

Für den endlichen Bildlauf ausschließlich eine neue eigene Arbeitsablage und
AppData/TEMP setzen. Godot Standard 4.7.2-stable aus dem gebundenen offiziellen
Archiv verwenden. Keine echten Nutzerprofile. Das vollständige Diagnoseprogramm
liegt **nur auf diesem Ref** unter `game/tests/pa_v01.gd`:

```powershell
$taskRoot = '<eigener absoluter Arbeitsordner>'
New-Item -ItemType Directory -Path "$taskRoot/tmp","$taskRoot/appdata","$taskRoot/native" -Force
$env:TEMP = "$taskRoot/tmp"
$env:TMP = $env:TEMP
$env:APPDATA = "$taskRoot/appdata"
$env:PA_OUTPUT = "$taskRoot/native"
godot --headless --path game --editor --import --quit
godot --path game --rendering-method gl_compatibility --script res://tests/pa_v01.gd -- --p1-capture
```

Die synthetischen Definitionen werden über den vorhandenen `book_fixture.gd`-
Komponenteneinstieg in der echten Buchszene geladen. Das Diagnoseprogramm markiert
nur seine acht isolierten, nicht registrierten Sitzungen frisch, weil der normale
SaveStore keine solchen Katalogslots akzeptiert; `assert(work.visible)` verhindert
versehentliche Katalogscreenshots. Keine echten Saves oder Kataloginhalte ändern.
Zahlenstatus im Panel wird direkt an den unveränderten Zeichner übergeben;
keine Behauptung eines Statuslogik- oder Deduktionsnachweises. Die nativen Bilder
selbst stammen aus dem abgeschlossenen korrigierten Lauf (`native.log`).

## Sichtentscheidungen und Endpunkt

- P-A-M01: F08 c01/c03 und c01/c04 in beiden Größen/Zuständen einordnen, F02,
  F05 mit/ohne C1 und F06 vergleichen; Formel/Grenzen 10/15 samt Warnzone und
  Präzisierung annehmen oder Korrekturen nennen. Dateien/Manifest, tatsächlichen
  Produkt-Head, Umgebung, Akteur, Zeitpunkt und Ausnahmen im PR binden.
- P-A-R01: vollständigen Produktdiff, Herkunft/Bindungen, 47 Paarrechnungen,
  Gleichheiten, Ausnahme-/Aktivierungssemantik und Originalbilder selbst prüfen.
  Selbstreview, technische Prüfung und persönliche Normfreigabe getrennt halten.
- Ende zunächst **15.11.2026**. Vorher benötigte Originale für diese beiden Gates
  verfügbar halten. Bei offenem Gate am Ablauf Bedarf/Zustellung neu prüfen;
  keine fortbestehende Verfügbarkeit vortäuschen. Im beauftragten Rückbau die
  beiden temporären Belegrefs `review/488-pa-v01` und
  `review/488-pa-v01-originals` entfernen; keine Git-Historienbereinigung und keine
  Produktressourcen löschen. Lokale eigene Arbeitskopien können nach bestätigter
  Veröffentlichung und Binärprüfung entfernt werden. PR-Entscheidungslinks bleiben.

Kein Player-/Chromiumlauf, reale Puzzleproduktion, Dauerbildtest oder P-B-Writer.
