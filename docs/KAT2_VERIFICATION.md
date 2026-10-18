# KAT-2: Kategorienkatalog und Prüfzuordnung

**KU-B / #244, freigegebener Sollstand vom 18.10.2026; Umsetzung offen:**
[Katalogsortierung](CATALOG_SORTING.md) ergänzt die Bedienleiste und sortiert den
vollständigen gefilterten Bestand vor der bestehenden Seiteneinteilung. Die
letzte Sortierauswahl samt Richtung wird als eigene lokale UI-Präferenz gemerkt;
Kategorie, Seite und Scrollposition bleiben Sitzungskontext. Blattnummer und
Aktionen bleiben bei Ansichtswechseln an das gleiche Rätsel gebunden. Die unten
beschriebenen KAT-2-Liefernachweise bleiben historische Basis; neue Sortier-,
Neustart- und Datumsnachweise gehören zu KU-B. KU-A verändert zuvor die
Kartenzeichnung gemäß [Katalogdarstellung](CATALOG_PRESENTATION.md).

Implementierung zu [#79](https://github.com/venomenon328/picross/issues/79),
auf `main@ca22f53caaacbae6883a6a2496d0d3e6e9381408` nach KAT-1/PR #80.
PR #77 ist bei Arbeitsbeginn offen/Draft; Knoblauch ist nicht integriert.
Die sechs bisherigen sichtbaren Rätsel und drei unsichtbaren Reservierungen
bleiben unverändert. Maßgeblich sind [KAT-1](CATEGORIES.md), [P1](PROTOTYPE_P1.md)
und die aktuelle [CI-Policy](CI_POLICY.md).

## Umsetzung

`game/ui/catalog.gd` stellt ausschließlich validierte Registry-Sessions dar.
Kategorie, Seite, Scrollposition und ausgewählte Registry-ID gelten für die
laufende Sitzung. Ein neuer Prozess beginnt bei „Alle Rätsel“, Seite 1.
Kategorienamen, Reihenfolge und Zuordnungen stammen aus der KAT-1-Projektion.
Gültiger Leerbestand, leere Kategorie und Ladefehler sind getrennte UI-Zustände;
auch ohne Session bleiben Einstellungen/Info und Beenden erreichbar.

Pro Seite entstehen höchstens 24 Karten. Seitenwechsel geben alte Controls und
Revealreferenzen synchron frei; beim Öffnen eines Blatts werden die verborgenen
Katalog-Reveals freigegeben. Die Abschlussansicht gibt ihre Referenz vor Rückkehr
frei. Es gibt keine zweite globale Auswahlvorschau. Motivnamen folgen dem gültigen
Sessionabschluss, Bilder kommen ausschließlich aus `Session.reveal()`; eigene ungelöste Füllungen werden
unverändert mit der bestehenden passiven Miniatur dargestellt. X bleibt gemäß
dem bestehenden VS2-/Zellrenderingvertrag in der Füllminiatur neutral.

Stabile Blattnummer, Größe, Mono/Farbe und Status stehen auf der Karte, im
Gesamtangebot zusätzlich die Kategorie. „Begonnen“ berücksichtigt Markierungen
und bestätigte History einschließlich Redo; ein leerer Save allein genügt nicht.
Ungültige Saves sperren das Öffnen und bleiben zurücksetzbar; gültige Backups
zeigen die bisherige bewusste Übernahme beziehungsweise Erneuerung.

Öffnen, Reset und Reparatur lösen über Registry-ID zur Session auf. Dialoge binden
die Ziel-ID schon beim Öffnen. Der bestehende Flush blockiert unsichere Wechsel;
Kategorien-/Seitenwechsel selbst schreiben keine Saves. Definitionen, Slotnamen,
Revisionen, Schema 1 und die vollständige Savevalidierung bleiben unverändert.
Registry-Einzellookups kopieren nur den gefundenen Eintrag statt jedes Mal den
gesamten Bestand; die Rückgabe bleibt vom validierten Cache getrennt.

## Automatisierte und native Nachweise

| Kriterium | Prüfweg und Orakel |
| --- | --- |
| A01 | Reguläre Hauptszene, sechs kanonische IDs, 20 Datenkategorien, Start ohne Werkbank; Export-Smoke `KAT2_CATALOG_START_OK` |
| A02 | Temporärer KAT-1-Adapterexport und echte Registrierung eines künstlichen Rechteckrätsels plus zusätzlicher Kategorie; All und Filter ohne UIänderung |
| A03 | Neue, leere gespeicherte, teilweise bearbeitete, nur Redo-, gelöste, zurückgesetzte, beschädigte und rekonstruierte Zustände; Name/Reveal/Count getrennt geprüft |
| A04 | Gefiltertes F09 und synthetische ID 025 auf Seite 2 per Pointer öffnen/bearbeiten/zurücksetzen; fremde Slotbytes vergleichen; Dialog-ID bleibt bei Seitenänderung erhalten |
| A05 | Hauptszene mit echten Viewport-Pointerereignissen und nativen Dialogen; Schreibfehler blockiert Rückkehr, Retry funktioniert; zusätzlicher Prozess liest Neu/Redo/Gelöst und setzt Redo fort |
| A06 | Eigene Prozesse für gültigen leeren und ungültigen Katalog; 300 synthetische Einträge, 20 Kategorien, Verteilung 250/50/18 leer, 150 gültige Abschlusssaves; Seiten, Rückkehr, Zeiten und Ressourcenbegrenzung |
| A07 | Native Framebuffer 1920×1080/UI100+125, 1280×720/UI125, 2560×1440/UI100; normale/gefilterte/leere/paginierte Zustände, langer Kategorienname, vor/nach Abschluss; Windows-Export/-Start und echte PCK-Prüfung |

`game/tests/kat2_cases.gd` ergänzt die Kernsuite um Status-/Spoilerfälle.
`game/tests/kat2_probe.gd` führt die native Route durch `main.tscn` aus;
`tools/kat2_product.py` erzeugt ausschließlich isolierte `test_only`-Projekte und
Saveprofile. Die 300 Runtimekopien dienen Last und Navigation; keine 300 echten
Produktionen oder Solverläufe. Das zusätzliche Adapterpaket besitzt ausschließlich
eine künstliche Testfreigabe. Nichts davon wird ins reguläre Spielerpaket kopiert.

Bis zur Integration von [CI-C (#249)](https://github.com/venomenon328/picross/issues/249)
führt `--integration` KAT-2 zusammen mit der bisherigen 500er-Route aus.
Die am 18.10.2026 freigegebene [CI-Spezifikation](CI_POLICY.md) ist noch nicht
implementiert und erlaubt bis dahin kein Überspringen ausgewählter Pflichtchecks.
CI-C liefert eine eigenständig auswählbare Kataloggruppe mit sämtlichen aktuellen
Eingabe-, Fehler-, Last-, Neustart-, Frame- und Exportaussagen. Katalogarbeit wählt
die 500er-Route oder alle Adapter/Piloten danach nur bei tatsächlicher gemeinsamer
Abhängigkeit. Die gezielte KAT-1-Adapterzuwachsprobe bleibt Teil ihres Vertrags.

Save-/Recovery-, Pilot-, aktuelle Pixel-/PERF-B-, Ressourcen-, Export- und
PCK-Prüfungen bleiben im jeweils relevanten Scope erhalten. Der vollständige
Base-/Head-Diff und gemeinsame/unbekannte Harnesswirkung bestimmen die Vereinigung
nach CI-Policy; native Gruppenwahl gilt erst nach CI-C. Reale Prozessneustarts
und absichtlich gemeinsame Profile innerhalb einer Prüffolge werden nicht durch
vorbereitete Ersatzstände abgelöst.

Die gezielte Nacharbeit zu [R1/B-01](https://github.com/venomenon328/picross/pull/81#issuecomment-6124420290)
unterscheidet eine geöffnete Rätselansicht von Katalog und katalogseitiger Info.
Nur die Werkbank, ihr Abschluss und ihre Informationsseite erzeugen neue
Ansichts-Speicherpflichten. Bereits ausstehende Timer und Speicherfehler werden
unabhängig davon weiterhin geflusht; Schreibfehler blockieren den Übergang.
SaveStore, Schema, Recovery und Bestätigungen bleiben unverändert.

Der zusätzliche native Modus `information` reproduziert mit echten Dropdown-,
Button- und Zellereignissen F01-Primary/Backupfehler, `recovered` mit defektem
beziehungsweise fehlendem Primary sowie `backup_invalid` in getrennten Profilen.
Er wartet über das Saveintervall, prüft Rückkehr und unveränderte Slotbytes,
Abbrechen/Bestätigen von Reset und Reparatur sowie tatsächliche ungesicherte
Werkbankänderungen mit Schreibfehler und Retry. Der letzte Beenden-Klick muss den
Prozess regulär beenden; der Pythonharness vergleicht danach sämtliche Slotdateien.
Die native Reproduktion am Ausgangshead und die neuen commitgebundenen Ergebnisse
stehen im bestehenden Draft-PR. Selbstreview, unabhängiges Nachreview und
Eigentümerabnahme bleiben getrennt.

Die JSON-Berichte enthalten Checks, Fehler, IDlisten, aktive Karten/Revealtexturen,
Start-/Seiten-/Kategoriezeiten, Renderer sowie getrennte Fensterclient- und
Framebuffermaße. Gemessene Zeiten umfassen den jeweiligen Aufbau und native
Framewartezeiten, beim Kategoriepfad auch die Pointerbedienung; sie sind keine
GPU- oder garantierte Eingabelatenz. Die Hauptansicht ist ein nativer SubViewport,
nicht eine behauptete physische Monitorauflösung.

Vollständige native Frames bleiben lokal. Der begrenzte technische Lieferumfang
enthält unverkleinerte Ausschnitte der tatsächlichen Controlrechtecke, eine
zusammenhängende enge Layoutansicht und deren Quellkoordinaten in `kat2/summary.json`.
Die aktuelle CI-Policy ersetzt frühere feste Artefakt-/Laufzeitbudgets.
Pflichtnachweise werden auf tatsächliche Aufnahme in das technische Paket geprüft.
CI-C misst Rendering, Lesen/Zuschneiden, PNG-Schreiben, Verpacken und Upload
getrennt. Eine schnellere verlustfreie PNG-Ausgabe muss auf denselben nativen
Frames identische dekodierte Pixel/Alpha, Maße, Ausschnittkoordinaten und
Pflichtbildmenge belegen; andere PNG-Datei-Bytes sind zulässig. Vollständige
Framekontexte bleiben lokal, geforderte Ausschnitte werden nicht ausgelassen.

## Stand und offene Gates

Gemessene Ergebnisse und der getrennte vollständige Selbstreview werden im
Draft-PR an tatsächlichen Head, Basis und Test-Merge gebunden. Ein grüner lokaler
Lauf ersetzt weder aktuelle ausgewählte CI-Jobs noch `ci-required`.

**Vor Merge weiterhin offen:** unabhängiges technisches/visuelles Review und
**KAT2-M01** durch den Eigentümer am nachgewiesenen Build: Einstieg, Kategorien/Alle,
Lesbarkeit, Öffnen/Fortsetzen und Rückkehr. Keine erneute vollständige Lösung aller
Rätsel erforderlich. Das Langspielthema #24 bleibt separat. Dieser Auftrag erlaubt
keinen Merge, Release oder Deployment.
