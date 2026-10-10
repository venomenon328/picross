# VS2-V2 · stabile Konturen und reine Füllminiaturen

N03/N05 sind auf `feat/61-regular-full-view` im bestehenden
[Draft-PR #62](https://github.com/venomenon328/picross/pull/62) umgesetzt.
Der PR bindet die tatsächlichen kombinierten Prüfergebnisse an Head, Basis,
Test-Merge, Run und heruntergeladene Artefakte. Unabhängiges kombiniertes Review,
persönliche VS2-M01 und Mergefreigabe bleiben offen. Kein Release oder Issueabschluss.

## Eingang und endliche Auswahl

Vorbereitung V2-S1–S5 aus [#61](https://github.com/venomenon328/picross/issues/61),
Head `13f9e02d7cc98b0e6e3816e09653f75ee0102c01`, Produktreferenz
`40829b43db6509447863c9d27dbb87dcfaf2a988`, Main-Basis
`d7ec4e1e4a29d82b6979537a33868d57732d3713` wurden vor Beginn geprüft.
Der vorhandene Arbeitsbranch wurde ohne fremde Änderungen weitergeführt.
S0 ist abgeschlossen, R2-B01 dokumentarisch behoben; keine Wiederöffnung.
Der eigene [endliche Plan](../examples/vs2/v2-plan.json) wurde **vor Vergleichen**
in `75b640c` versioniert. Ein begrenzter Kandidat, keine offene Variantenoptimierung.
Ursprüngliche VS2-/V1-Pläne, Nachtrag, Reports, Fonts und Assets bleiben erhalten.

## Umsetzung

Der reguläre `FullViewBoard` zeichnet jede gemeinsame Rasterkante genau einmal.
Ein reiner ganzzahliger Identitätsmischer verwendet Definitions-ID/-Revision,
Achse, Linie und Segment. Er liest weder Uhrzeit noch Zellzustand oder RNG.
Abweichung höchstens 0,18 px; Hauptstriche 1,40–1,64 px, Nebenstriche 0,70–0,90 px.
Die Abweichung wächst zwischen Zellgröße 4 und 24 px von null zum vollen Wert.
Bei gleicher Geometrie bleiben Neuzeichnen, H1, Blattwechsel und Neustart stabil.
Kein zusätzlicher Ticker oder Animationszustand.

Außenlinien und Endpunkte liegen einen Pixel innen. Die konservative Grenze
aus Abweichung, halber Strichbreite und 1 px Antialiasing ergibt außen höchstens
1 px. Damit bleiben V1s Rahmenbudget, Fit, GF1 und gemeinsame Translation erhalten.
Logische Zellrechtecke und Trefferabbildung ändern sich nicht. Der historische
Basiszeichner behält seine geraden Linien; die neue virtuelle Zeichenmethode
erlaubt ausschließlich dem regulären Board den neuen Strich.

Miniaturrahmen, Buchfassungen und Farbmusterkonturen verwenden denselben reinen
Zeichner mit maximal 0,25 px Abweichung und 1,5 px Breite. Gemessene Punkte samt
AA müssen innerhalb der bestehenden 2-px-Gruppenhülle bleiben; Miniatur und
Farbcontrols werden zusätzlich mit 1 px Außenrand geprüft. Hitflächen, Auswahl-
und Fokusmarken sowie Originalfarbflächen bleiben. Das Hintergrundbild und alle
Schriftdateien sind unverändert.

Der gemeinsame Miniaturzeichner zeichnet ausschließlich positive eigene Zellen.
X=0 und unbekannt=−1 erzeugen dasselbe Papier; die vollständige Eingangsmatrix
bleibt erhalten. Arbeit verwendet weiterhin `visible_cells()` samt elastischer
Vorschau; beide vorhandenen Albumwege verwenden bestätigte eigene Zellen.
Keine Lösung wird dem Zeichner übergeben, kein Filter verändert Modell, Save
oder History. Füllformen bleiben proportional, ruhig und ohne Animation.
Bedienhilfe und aktive Fachtexte erklären dieselbe Regel.

## Technischer Nachweisweg

- NA03: `vs2_v2_cases.gd` misst tatsächliche Strichpunkte/-breiten gegen unabhängige
  feste Korridore einschließlich AA. Eingebunden in 304 Matrixfälle, V1-Fokusfälle
  und 40 native Fensterfälle. F01/F02, VS04/VS08/VS09, Arbeitsgröße/Einpassen,
  vier Flächen, beide Ansichten und UI100/125 bleiben abgedeckt. Die gezielte
  V2-Probe ergänzt die angebotene 12-px-Stufe und dunkle Fünferkreuzungen.
- NA05: `vs2_v2_tests.gd` vergleicht komplette native Miniaturpixel bei gleichen
  Füllungen und abweichenden X/unbekannt. Positive Originalfarben und eigene
  falsche Füllungen verhindern einen trivialen Leerbild-Pass. 19 Übergangsszenarien
  sichern Vorschau, Rückzug, Escape/Fokus/Gegentaste, Commit, Undo/Redo, Reset,
  Album und Blattwechsel. Ein separater Prozess prüft exakte Zellen, History,
  ausstehendes Redo, gleiche Miniaturpixel und Strichgeometrie.
- Negativkontrollen: vergrößerte Strichbreite überschreitet den Korridor;
  geänderte Punkte verletzen Stabilität; eingefügter X-Pixel und unterdrückte
  Füllfarbe verletzen Pixelgleichheit. Das native Raster unterscheidet sich
  nachweislich von seiner geraden Endpunktreferenz und bleibt beim Redraw gleich.
- Vier Rahmenkanten: Der Pixelprüfer verlangt auf jeder Probe mindestens einen
  dunklen Strichpixel mit Farbentfernung unter 0,28. Zwei voll deckende Pixel
  wären bei 1,40–1,64-px-AA-Strichen kein gültiger Maßstab. Fehlende Kanten bleiben
  eine harte Verletzung; vollständige Bilder und tatsächlicher Umfang sind separat geprüft.
- V1: unveränderte 24/18-×-UI-Hinweispitches und Fonts, Fit-vor-GF1-vor-Translation,
  reale 1/11/17/40-Glyphen, unabhängige Hinweisnavigation und 44/55-px-Hits.
  80 Fokus-/Recoveryfälle, sechs Glyphenstreifen und Python-Gegenprüfungen bleiben.
  Die neue Zeichenhülle wird gegen Buchrand, Board, Navigation und Recovery geprüft.

Die ersten Entwicklungsversuche deckten Fehler im neuen Prüftreiber auf:
Reset kehrt in die Sammlung zurück, deshalb muss vor Zellklicks das Blatt erneut
geöffnet werden. Positive Miniaturpixel werden im Innenbereich gemessen, damit
der vorhandene Rahmen keine Randzellprobe verfälscht. Die Krümmungsassertion
berücksichtigt die geplante Ausblendung unter 6 px. Diese Befunde änderten weder
den Produktkandidaten noch Fit-, Farb- oder Persistenzverträge. Nur die späteren
erfolgreichen, commitgebundenen Läufe gelten als Liefernachweis.

## CI, Referenz und Windows-Paket

Es gilt die [aktuelle CI-Policy](CI_POLICY.md), einschließlich vollständiger
Base-/Head-Auswahl und `ci-required`. Wegen der Harnessänderung werden alle
aktuellen Bereiche benötigt: Tool-/Dokumentchecks, Product samt Kernregression,
500er-Route, sechs Piloten, kompakte native Pixelprüfung und Export, Preflight
sowie Produktions-/Windows-/Reparaturfachprüfungen. Keine historischen Importe
oder vollständigen Galerien im Standardpfad. Der V2-Schreib-/Lesetest läuft im
aktuellen nativen VS2-Worker und ergänzt dessen Bericht um Plan-/Skripthashes.

Sechs gezielte V2-Bilder werden erzeugt: zwei Gesamtansichten und vier 1:1-Ausschnitte
(Mono-/Farbprojektion, Fünferkreuzung, Miniatur/Palette). Die begrenzte technische
Auswahl teilt weiterhin 12 MB Bildbudget, 20 MB Technik und 75 MB Gesamtbudget.
Gerenderte Assertions und tatsächlich gespeicherte Auswahl werden getrennt gemeldet.
Die bestehende gebundene V1-Referenz aus Run `38053346260`, Artefakt `11670403247`,
dient dem Vergleich; kein neu gerendertes Vorherprojekt.

`tools/vs2_windows_probe.py` verlangt den sauberen ausgelieferten Head und lädt
Spielerpaket sowie technische Daten neu herunter. Es prüft Artefaktdigest,
inneres ZIP, Head/Base/Test-Merge/Run, EXE-Paar, eingebettetes PCK und Bildhashes.
Beide EXEs starten ohne Argumente mit frischem, teilgespieltem und gelöstem Profil.
Echte alte Writer/neue Reader und normale/maximierte Fenster mit getrennten
DPI-/UI-Angaben sichern Fortsetzen, Recovery und Eingabe. V2-Schreib-/Lesetest und
Strichprüfung laufen zusätzlich gegen das tatsächlich heruntergeladene PCK;
externe Testskripte bleiben aus dem Spielerexport ausgeschlossen.

Der PR dokumentiert die Resultate und einen **getrennten Selbstreview**.
Die Implementiererprobe ist keine persönliche VS2-M01 und keine unabhängige
technische/visuelle Zweitprüfung. Historische Komfortgrenzen großer Raster gelten
weiter; geometrische Passung bedeutet keine bestätigte Lesbarkeit.
