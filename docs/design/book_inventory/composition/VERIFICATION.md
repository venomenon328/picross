# BP-3 · Prüfbericht

Stand: 26.09.2026 · B3-01 bis B3-05 · Branch `chore/27-bp3-zielkomposition`.
Basis `66b9d39dd3dbce908ff663a18c059351cfccf557`.
Finaler Head, ZIP-Hash, CI- und Test-Merge-Bindung stehen im eigenen Draft-PR.

## Quellen und Ausführung

Aktuelle AGENTS.md, Workflow, Projektprofil, vollständige Produktdefinition und
Gestaltungskonzept, #27 samt Kommentaren, #21 samt Kommentar, BP-1R-Anleitung,
Briefing/Prüfbericht, Layout/Quellen/Fontmessungen und BP-2-Anleitung, Prozess,
Prüfbericht/Manifest sowie PR #31/R1 gelesen. Bestehende Helfer und Tests gelesen;
relevante Zustands-/History-/Hinweis-/Recoveryverträge in P1 §§5–6 nachgeschlagen.
Beide Hintergrunddateien und die fünf technischen Kontrollgrößen tatsächlich geöffnet.

Ein separater Worktree vom aktuellen main hält fremde unversionierte Dateien und
alte lokale Testartefakte im ursprünglichen Arbeitsbaum unangetastet. Keine andere
PR bearbeitet. Die neuen Dateien sind auf Kompositionspaket, engen Helfer mit Tests
und Status-/Gestaltungsverweise in den zwei erlaubten Dokumenten begrenzt.

Rasterisierung: Windows, Python 3.13, vorhandene isolierte Playwright-1.55.0-/
Pillow-11.3.0-Umgebung, Microsoft Edge, Device Scale Factor 1. Exakte Browserversion,
temporäre Font-/Lizenzhashes und alle gemessenen Texte in [render-checks.json](render-checks.json).
Netzwerk beim Rendern blockiert. FontFace-Status plus die pro Textelement vom
Browser gemeldeten tatsächlich benutzten Custom-Fontfamilien werden protokolliert.
Keine globale Installation und keine Fontbytes im Paket.

## Automatisierte Lieferprüfung

Der zusätzliche Helfer prüft die tatsächliche Lieferung mit Standardbibliothek:

- Alle geschützten Produktions-/Artworkdateien sowie deren Helfer/Tests bytegleich
  zur gebundenen Basis; vollständige Paketdateiliste, Dateigrößen und SHA-256.
- Alle PNGs vollständig decodiert. Maße und Transparenz der Haupt-UI geprüft;
  unbekannte Rasterzellen bleiben transparent, gesetzte Zell-/Swatchmitten exakt RGB.
- Grid-, Hinweis- und Miniaturvektoren gegen die unveränderte Vorlage verglichen:
  originale Zellmengen einschließlich Fehlern, gemeinsame Slots, atomarer Überlauf,
  H1-Zeile-2-Beispiel, Palette und Miniaturausschnitt bleiben erhalten.
- Alle Aktionskennungen, Trefferrechtecke und Navigationsziele geprüft. Raster,
  Hinweise, Koordinaten und Status enthalten keine Pixel der Materialebene.
- Separate Montierungs-/Inhaltspixel ergeben die gemeinsame UI; maximal ein
  Kanalwert Rundungsunterschied durch Zwischenquantisierung an Alpha-Kanten beim
  unabhängigen Vergleich über Schwarz und Weiß. Größere Abweichungen werden abgewiesen.
  Die PNG-Lieferung wird ausdrücklich aus den getrennten Ebenen zusammengesetzt;
  direkte Browser-Rasterisierung des kombinierten SVG kann an Kanten leicht abweichen.
- Zehn A/B-Montagen pixelweise rekonstruiert: unverändertes Hintergrundbild
  proportional abgetastet, gemeinsame UI ohne Skalierung darüber. Alle 22
  Detaildateien sind exakte 1:1-Ausschnitte mit gespeicherten Quellrechtecken.
- Textrechtecke und tatsächlich benutzte Schriftfamilien geprüft. Normaltextkontrast
  mindestens 4,5:1 über das lokale Minimum jedes gesamten gemessenen Textrechtecks,
  auf realem Hintergrund plus gerenderten Gehäusen bei entfernten Textglyphen.
  Alle Tafeln/Meldungsbeispiele sind eingeschlossen. Keine Papiermittelwerte und
  keine Wiederverwendung der BP-2-Kontrastwerte; [Einzelwerte](contrast.json).
- Lokale Galerieverweise und vollständiger bytegleicher ZIP-Inhalt geprüft,
  einschließlich der beiden gebundenen Hintergrundinputs, ohne Fonts.

Gezielte Negativtests verändern Hinweiszahl, eigene Miniatur, Trefferfläche,
Navigationsziel, Ebenenfarbe/-alpha und lokalen Kontrast. Sie müssen fehlschlagen.
Die bestehenden Python-Tests, der Dokumentvalidator und Workflows bleiben unverändert.

## Sichtprüfung und Grenzen

Alle zehn Hauptansichten und alle drei Tafeln wurden einzeln betrachtet. Die
2560er Gesamtbilder wurden vom Anzeigewerkzeug auf 2048 Pixel Breite verkleinert;
zusätzlich wurden deshalb alle 22 Detaildateien einzeln in Originalgröße geöffnet.
Die Zahlenausschnitte belegen kleine Ziffern, C1, H1 und Zelltrennung; die zwölf
720p-Randdetails zeigen Miniatur, alle vier Farbmuster, Werkzeuge, beide Zugänge und
Status unskaliert. Die Kanten eines Detailausschnitts sind dessen Beschnittgrenze,
keine im Spielscreen abgeschnittenen Hinweise.

Sichtbefund: Einfassungen passen zu beiden Materialvarianten und bleiben außerhalb
der Raster-/Hinweisarbeit. Miniaturinhalt und Ausschnittrahmen sind erkennbar;
Farbflächen bleiben unverfälscht. Die Auswahl ist zusätzlich zur Farbänderung an
Unterstrich beziehungsweise Eckmarken und am dauerhaften Status erkennbar.
Bei 720p bleiben alle neun Arbeitsaktionen und die getrennten Randzugänge sichtbar.
Die lokalen Schatten sind flach und beeinträchtigen weder Text noch Trefferflächen.
Bei F-01 wurde die zunächst unnötig große leere Palette auf eine einzelne kleine
Mustermontierung innerhalb derselben Reserve reduziert, ohne den Treffer zu ändern.

Die Galerie wurde aus dem entpackten Review-ZIP per `file://` tatsächlich geöffnet:
alle zehn A/B-Umschaltungen, Originalbildmaße/-links, 1:1-Umschaltung und
Nebeneinanderansicht erfolgreich, keine JavaScriptfehler oder externen Requests.
[Browsernachweis](gallery-checks.json) und [Galerie-Screenshot](checks/gallery.png).

Die neuen lokalen Kontrastminima liegen bei A zwischen 8,0558:1 und 8,3233:1,
bei B zwischen 8,3355:1 und 8,7076:1. Die drei Tafeln liegen zwischen 8,9960:1
und 9,1693:1. Gemessen wurden 1.626 Textelemente einschließlich Hinweiszahlen;
farbige Hinweise sind ausdrücklich vom Normaltext-Kontrasturteil ausgenommen.

Normale Textkontraste zertifizieren keine farbigen Hinweiszahlen, Rasterlinien,
Symbole oder universelle Barrierefreiheit. C1, Zelltrennung und Auswahlmarken werden
zusätzlich visuell beurteilt. Die Tafeln sind statische Beispielsituationen nach
P1-Vertrag; sie behaupten keinen realen Speicherversuch, Mausstrich oder vollständige
native Navigations-/Recoveryprüfung. Diese Grenzen gelten auch für die 720p-Probe.

## Abschluss und Gates

Lokal ausgeführt: vollständige Suite mit 63 Tests in 182,647 Sekunden erfolgreich;
ein bestehender Windows-Symlinktest übersprungen. Dokumentvalidator erfolgreich.
Der erste isoliert angesetzte Testaufruf verwendete ein falsches unittest-Startverzeichnis
und konnte das Paket nicht importieren; der verbindliche Aufruf ab `tools` besteht.
Nach der anschließenden Erweiterung der Lieferprüfung um vollständige Swatchflächen
und Zustandszuordnung wird der finale Stand zusätzlich direkt geprüft und durch CI gebunden.

Pflichtbefehle: passende Python-Tests, unveränderter Dokumentvalidator und vollständiger
`git diff --check` gegen die Basis. Aktueller erfolgreicher `docs`-Job am finalen
Head/zugehörigen Test-Merge ist erforderlich. Tatsächliche Ergebnisse der unverändert
aktiven `product`-/`preflight`-Jobs werden im PR ausgewiesen; sie sind Regressionsevidenz
für P1, keine native Integration der neuen UI.

Getrennter Selbstreview im eigenen Draft-PR, keine unabhängige Zweitprüfung.
Vor späterem Merge unabhängiges technisches/visuelles Review und ausdrückliche
Eigentümerfreigabe. Vor #23 konkrete Gestaltungswahl und bestätigter nativer Umfang.
Kein Merge, Release, Beginn von #23/#24 oder Schließen von #27/#21.
