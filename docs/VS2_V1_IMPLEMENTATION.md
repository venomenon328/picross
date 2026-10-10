# VS2-V1 · kompakte Hinweise und Flächenaufteilung

V1-Zwischenstand in [Draft-PR #62](https://github.com/venomenon328/picross/pull/62),
Branch `feat/61-regular-full-view`. N01/N02/N04 sind umgesetzt. V2/N03/N05,
kombinierte technische/visuelle Abnahme, unabhängiges Review und VS2-M01 bleiben
offen. Keine Merge-, Release- oder Issue-Abschlussfreigabe.

## Eingang, Auswahl und Präzisierung

[S0](VS2_V1_S0.md) wurde vor Layoutarbeit mit CI `38048159384` positiv geschlossen.
Die ausdrücklich übernommene CI-Policy #63 ist auf main `d7ec4e1` integriert.
[Endlicher Plan](../examples/vs2/v1-plan.json): vor Vergleichen in `06f695f`
versioniert. Kandidat A ist gewählt; B wurde nicht verwendet.

Der [Eigentümernachtrag](../examples/vs2/v1-plan-amendment.json) in `a41cf9b`
nimmt die synthetische Hinweiszahl 100 aus der V1-Abnahme. Ihre zunächst erprobte
Randpuffer-Sonderbehandlung wurde vollständig entfernt. Maßgeblich sind reale
1/11/17/40-Glyphen und die vorgesehenen regulären Inhalte. Bestehende große
Stress-/Pilotdatensätze bleiben als Regressionen erhalten; keine Datenmigration
oder neue Größenvalidierung. Historische Pläne und Nachweise bleiben unverändert.

## Umsetzung und Grenzen

- N01: gemeinsame Zeilenslots 24 × UI statt 26 × UI. Vertikale Slots bleiben
  18 × UI. Unveränderte Fontdateien und Größenregel, C1/AA und Statusumfang.
  Mindestreserven, GF1-Zusatzkapazität und kontinuierliche Sichtbarkeitsgrenzen
  verwenden denselben neuen Pitch. Die historische Zeichnerkomponente bleibt 26.
- N02: unveränderte sichere Boardfläche → Mindestreserven/Fit → GF1 → gemeinsame
  Translation. Tatsächliche Glyphen-/Statusgrenzen bilden mit dem Rasterrahmen
  den belegten Block; bei Überlauf gehört der gesamte mögliche Lesebereich dazu.
  Leere Slots erzeugen keinen Ausgleich. Der Restversatz wird auf ganze Pixel
  gerundet und an der sicheren Fläche begrenzt. Fit und Zellmaßstab stehen davor
  fest. Zeichnung, beide Hinweisflächen und Eingabetreffer verwenden denselben
  Versatz. Zellwerte, H1 und Lesen beeinflussen die Anordnung nicht.
- N04: Miniaturgruppe großzügig um (−16, +24) × UI verschoben, mit Fassung,
  Palette, Beschriftungen und tatsächlichen Trefferflächen. Auf knappen Flächen
  begrenzt die untere Beschriftung den vertikalen Versatz. Farben behalten
  44/55px-Hitflächen. Der Recovery-Knopf liegt links unter der Fehlermeldung im
  schon zuvor reservierten Kopfbereich und verdeckt weder Board noch Gruppe.

Papiergrenzen werden gegen den unveränderten A-Hintergrund gemessen; bei
umgebrochenen Beschriftungen zählt die tatsächliche Textzeilenbreite samt 1px
Rand, nicht ungenutzte Breite des Label-Controls. Hierfür wird Godots
[TextParagraph](https://docs.godotengine.org/en/stable/classes/class_textparagraph.html)
mit den tatsächlichen Fonts, Größen und Umbruchbreiten verwendet.
Miniaturprojektion und sichtbare gerade Rasterstriche bleiben V2-Arbeit.

## Tatsächlich ausgeführter Prüfweg und Nachweisbindung

Der aktuelle Produktharness führt zusätzlich zur bisherigen Regression aus:

- 304 Fälle: neun reguläre und zehn technische Blätter, vier Clientflächen,
  UI100/125, G/V. In jedem Fall V1-Geometrie-/Papier-/Hitflächenprüfung.
- 32 gezielte F-01/VS04/VS08/VS09-Fälle mit Arbeitsgröße/Einpassen und 48 echte
  Savefehler-/Recoveryzustände. Mausaktionen auf verschobenen Ecken/Farben,
  Undo/Redo und H1; beide Hinweisachsen über alle kontinuierlichen Grenzen und
  offenen Intervalle. Native Statusstreifen für 1/11/17/40 bei UI100/125.
- Unabhängiger Python-Oracle berechnet Fit, Schriftgröße und Translation aus
  Messdaten neu. Sechs absichtlich falsche Varianten müssen scheitern:
  alter 26er-Pitch, kleinere Schrift, linke Ausgangslage, leere Reserven,
  allein verschobenes Raster und alte Gruppenposition.
- Bestehende GF1-/ZS2-Slot-Oracles erwarten regulär 24; historische Komponenten
  bleiben 26. Kleine Großfall-Fits werden weiterhin als eingeschränkt ausgewiesen.
  H1-, Gesten-, Speicher-, Pilot-, Pixel- und Rahmenprüfungen bleiben aktiv.

Die Windows-Downloadprobe prüft neu heruntergeladenes EXE-Paar und tatsächliches
eingebettetes PCK: Starts ohne Argumente mit frischem/teilgespieltem/abgeschlossenem
Profil, echter alter Writer/neuer Reader, normale/maximierte Clientflächen,
DPI/UI, verschobene Ecken/Farbwahl, Hinweisdrag und Recovery. Externe Prüfskripte
werden gehasht; sie sind keine exportierte Produktfunktion.

Finaler Head, Basis, tatsächlicher Test-Merge, Run/Jobs, Artefakt-/EXE-/PCK-Hashes,
native Bilder und Ergebnisstatus stehen commitgebunden im PR. Dieser Text allein
behauptet keinen erfolgreichen finalen Downloadlauf. Vorherbilder stammen aus
der ursprünglichen hashgebundenen Referenz und einem ausdrücklich getrennten
Replay des unveränderten Produktstands `32befbf`; kein historischer Import wird
in den Standard-CI-Pfad aufgenommen. Die begrenzte technische Lieferung priorisiert
V1-Messberichte und gezielte native Bilder innerhalb der unveränderten Bytebudgets.

Die CI-Auswahl gemäß #63 ist maßgeblich; dieser breite PR betrifft derzeit alle
sechs Fachjobs und `ci-required`. Ein gesonderter Selbstreview wird im PR als
solcher bezeichnet. Er ersetzt weder unabhängiges Review noch persönliche Abnahme.
