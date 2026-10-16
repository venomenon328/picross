# KK · feste Katalogkacheln (#174)

Vertrag: [vollständiges Issue einschließlich Umsetzungsvorbereitung V1](https://github.com/venomenon328/picross/issues/174).
Startbasis `main@35465bed49055b01583a20aab7add9b37536c129`, nach KB/EA und
den ausschließlich authoringbezogenen PRs #172/#173. Branch
`fix/174-feste-katalogkacheln`, Ziel `main`; ein Paket und ein Draft-PR.

`catalog_card.gd` hält die Bereiche außerhalb inhaltsabhängiger Container-Minima.
Der native Button hat keinen unsichtbaren Text. Breite und Spalten folgen weiterhin
220–240 × UI, tatsächlicher Scrollfläche und Balkenreserve. Innenrand 10 × UI,
Abstände 8 × UI, Resettreffer 44 × UI; alle Werte werden gemeinsam pixelgerundet.
Bakso 20 × UI und Plex 14/15 × UI bestimmen die zwei Titel-/Metadatenzeilen samt
gemessener Fonthöhe und Zeilenabstand sowie die einzeilige Fußzeile. Der gemeinsame
112 × UI hohe Bildraum lässt auch in kompakten Karten eine erkennbare Vorschau zu.
Diese Summe bestimmt die feste gemeinsame Höhe; Namen, Status und Ressourcenmaße
tragen keine Mindesthöhe bei. Explizite Label-Maxima binden Godots nativen Umbruch.
Die unveränderte Bakso-Datei zeichnet für U+2026 einen Buchstaben. Die Titelkürzung
wählt deshalb Godots vorhandenen Ersatz aus drei originalen Punktglyphen über ein
nicht belegtes Ellipsiszeichen; Fontbytes und lokale Fallbackrolle bleiben gleich.
Diagnose und Text-Recovery liegen in einem scrollbar erreichbaren Bildbereich.

KK ersetzt gezielt KB-D01/D02: variable Höhen, zweite Blattüberschrift,
Playcontrol und Kacheltooltip. Der geteilte BookButton-Tooltip wird für die Karte
unterdrückt; Reset behält ihn. Bakso gilt zusätzlich für Motivüberschriften/`???`.
Historische KB-Berichte, 13-Iconinventar, Font-/Assetbytes und KAT-/EA-/Saveverträge
bleiben erhalten. Reset-Sichtbarkeit folgt validiertem Fortschritt und separatem
Speicherzustand, einschließlich Fehler bei intern leerer Session.

| Akzeptanz | Prüfweg / Orakel |
| --- | --- |
| A01/A02 | `kat2_probe.gd`, Modus `kk`: tatsächliche Karten-, Grid-Zellen-, Titel-, Metadaten-, Bild-, Fuß- und Resetrechtecke vor/nach Neu, Leersave, Pointerbearbeitung/Undo, gültigem Abschluss, langem Namen und Reset. Drei gemeinsame Flächen, UI-Rundweg, 128-Zeichen-Kategorie und Spaltengrenzen. Bakso, zwei Zeilen/Auslassung, Footertrennung und proportionale breite/hohe Bilder. |
| A03/A04 | Echte Viewport-Down/Up für Karte/Reset/Bestätigungen im `kb`-/`kk`-/regulären KAT-2-Weg. Native Hoverwartezeit prüft fehlenden Kartenpopup und erhaltenen Resettooltip. Filter, spätere Seite, Abbruch, stabile Dialog-ID und fremde Slotbytes. Bestehende EA-Proben sichern den getrennten Endreset. |
| A05 | `kat2_cases.gd`, Kernsuite/`p13_cases.gd` sowie KAT-2-Modi `regular`, `restart`, `information`: Leersave/Redo, beschädigte Primaries/Backups, explizite Reparatur, Schreibfehler, Pflicht-Flush und echter Prozessneustart. `kk` ergänzt lange Diagnosen und Pointerzugriff auf innen gescrollte Textaktionen bei gleicher Geometrie. |
| A06 | Unveränderte feste technische Inputs, `Session.reveal()` als einzige Abschlussgrenze; 300 synthetische Einträge, höchstens 24 aktive Karten/Revealreferenzen und letzte Restseite. Keine Rätseltests aus Produktionsinhalten. |
| A07 | Vollständiger Diff, getrenntes Selbstreview und aktuelle Pflicht-CI nach [Policy](CI_POLICY.md), einschließlich echter Chromium-/Firefox-/Persistenz- und isolierter SSH-/HTTP-Referenz. Native Windows-Geometrie/Sicht/Pointer und gestartetes CI-EXE/PCK-Paar werden im PR an Head/Basis/Checkout/Run/Artefakte gebunden. |

Die Nacharbeit zu [Review R1](https://github.com/venomenon328/picross/pull/176#pullrequestreview-5545825024)
prüft neutrale Diagnoseklicks für gültige Backups, den realen Reset einer
deaktivierten Fehlerkarte und getrennte Down/Up-Routen für Rad, Scrollbar,
Textdrag und Reparatur. Lange Diagnosen müssen tatsächlich innen scrollen,
ohne den äußeren Katalog oder eine Kartenaktion auszulösen. Auch nach
Rückscrollen während gehaltener Linkstaste bleibt die Kartenöffnung verworfen.
Der innere Scrollcontainer behält `STOP`; nur neutrale Linksklicks ohne
Zieh-/Scrollaktion aktivieren den bestehenden Registry-ID-Öffnungsweg.
Die nativen JSON-Berichte enthalten Scrollbereiche, Pointerpunkte und
Aktionszähler je Speicherzustand. Ein separates leeres Profil prüft den echten
SaveStore-Schreibfehler vor Primary-Veröffentlichung: Diagnose, neutralen
Fortschritt, Flushsperre und tatsächlichen Reset mit Abbruch/Bestätigung und
unveränderten fremden Slotbytes. Ausführung und Ergebnisse stehen im PR.

`tools/kat2_product.py` nimmt KK in den vorhandenen Integrationspfad auf; kompakte
native Originalausschnitte und JSON-Messdaten gehören zur technischen Lieferung,
vollständige Framekontexte bleiben lokal. Der Web-Beobachter der separaten Testfassung
benennt Karten über ihre zugängliche Blattzuordnung und benutzt einen tatsächlichen
Punkt der Kartenfläche. Der Spieler erhält keine Testbeobachtung oder Saveprofile.
Die [dauerhaften Windows-Originalausschnitte](evidence/kk/README.md) werden durch
`tools/kk_windows_probe.py --head <SHA> --run <CI-Run> --engine <geprüfter-editor>
--cache-dir <archivcache> --output-dir <neues-ziel>` am finalen sauberen Head erneut
bytegenau erzeugt. Derselbe Lauf prüft und startet das heruntergeladene CI-EXE/PCK-Paar
über den bestehenden Windows-/EA-Prüfweg, einschließlich eigenem HWND-Bild und Neustart.
Die allgemeinen Kern-, Prozess-/500er-, Pixel-/PERF-B-, Ressourcen-/Export- und
EA-Regressionen bleiben ausgewählt. Harnessänderungen wählen alle aktuellen Jobs
einschließlich Preflight; keine Änderung der CI-Auswahlregeln.

V1-Zugänge wurden beim Implementierungsstart erneut geprüft: GitHub-Quellen/CI,
Pushrechte, separater sauberer Worktree und gepinnte Windows-Archive samt tatsächlichem
Editorhash und Version. Python/Pillow 12.3.0 und native NVIDIA/OpenGL-Ausführung
sind verfügbar. Die aktuelle Browser-/SSH-Referenzprüfung erfolgt in CI, ohne
Kontakt zum Eigentümer-VPS. Keine fremde lokale Arbeit wurde übernommen.

**KK-T01** verlangt vor Übergabe die vollständige technische Lieferung. Konkrete
Resultate, Zeiten, Bytes, Datei-/Artefakthashes und Grenzen stehen im Draft-PR;
diese Prüfzuordnung nimmt keinen erfolgreichen finalen Lauf vorweg.
**KK-R01** bleibt unabhängiges technisches/visuelles Review vor Merge.
**KK-M01** bleibt die gezielte persönliche Eigentümerprobe vor Merge am gebundenen
Windows-Build: Maße, Titel, Vorschau, Fußzeile, Resetanker und Hover bei UI100/125,
Öffnen/Fortsetzen/Ansehen, Resetabbruch/Bestätigung ausschließlich im isolierten
Profil. Windows-/Client-/UI-Skalierung und Ergebnis notieren. Selbstreview und
technische Zeigersimulation ersetzen keines dieser Gates. Kein Merge, Release,
Deployment oder Branchlöschen durch diesen Auftrag.
