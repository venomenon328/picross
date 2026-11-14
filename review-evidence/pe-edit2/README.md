# PE-EDIT2 · T01–T03 · 14.11.2026

Geprüfter Produkt-Head `cf7d4f051728ec893bc4839e78046335b5d36d67`, Basis `cc579fe4d25a081426440da4838557ec7496de16`, PR-Test-Merge `b274b44220e84abce9bd6ef6d93603afb95263d3`. [Draft-PR #643](https://github.com/venomenon328/picross/pull/643), [verbindliches Paket #640 samt Nachtrag](https://github.com/venomenon328/picross/issues/640#issuecomment-6878198255). K01–K08 sind implementiert; die unabhängige Bewertung bleibt PE-EDIT2-A01.

## Produkt und bewusst geänderte Garantie

Der normale Editor verwendet aktuelle kleine Indizes und nur die gewählte Definition/technischen Bildquellen. Geschlossene Pläne und ein kompaktes zielgebundenes Journal ersetzen Vollbestands-Snapshots, Gesamtkopien, historische Bildreplays und globale Guards. Eine Einzelaktion zertifiziert ausdrücklich nur ihre tatsächlichen Eingaben und Änderungen. Die explizite Produktions-/Diagnoseprüfung bleibt umfassend. Herkunfts-/Rechte-/Akteurspflichten entfallen aus neuen UI-, Request- und Quellenformen.

Virtuelle Auswahl mit eigenem Scrollbereich, lokale grafische Rastervorschau und Komposition auf den echten Spielressourcen sowie persistentes Hell/Dunkel gehören zum selben Stand. Der persistente Worker wartet untätig auf einzelne Aufträge; er hält nur validierte Uploads und den aktuellen Plan, keinen Katalogcache und keine Hintergrundinventur.

Keine Migration in App/UI/API oder portablem Paket. #641-M1 ist über die aktuelle Basis integriert. Die neue aktive Quellgeneration benötigt die separate externe #641-M2-Bestandsmigration. Hier wurden ausschließlich isolierte Testkopien auf diese technischen Formen vorbereitet; reale Quellen, Nutzersaves und der fremd geänderte Benutzercheckout blieben unberührt. Runtime-v7 wird lesend abgelehnt. Runtime-v8 mit bisherigen aktiven Quellen unterstützt Metadatenpflege; Bild-/Rasterpflege zeigt bis zur externen M2 einen Hinweis und konvertiert keine ID beim Speichern.

## T01 · Arbeitsmenge und Bedienzeiten

Windows 11 10.0.26200, NTFS E:, Ryzen 7 5800X (8/16), 34.269.659.136 Byte RAM, Python 3.13.14, Edge 157.0.4341.46. Keine gleichzeitig laufenden lokalen Builds, Testfamilien oder Artefaktkopien während der finalen Messreihe. Einmalige Quellinstrumentierung im aktuellen Dienst/Worker; tatsächliche Browseraktionen bis sichtbarem Ergebnis. Je Szenario neuer Dienst, erster Lauf und zwei Wiederholungen. Kein Vorlesen fremder Assets zum Aufwärmen. Der native portable Gesamtweg ist zusätzlich T03.

56: isolierte Kopie des aktuellen realen Bestands, extern vorbereitete technische Quellen; nur die ausgewählte ID `pz-00f37200bcee4d548e2c910ce551d077` wird verändert. 1.000: eine echte Test-ID `pz-test-direct-mono` und 999 reine Indexzeilen, deren individuelle Dateien nicht existieren. Die Auditor-Canary für `game/data/content/fake-0001.json` scheitert absichtlich vor dem Dateizugriff in beiden Fixtures. Normale Aktionen greifen auf keine fremde Einzeldatei zu; keine rekursive Bestandsinventur. Start und Leerlauf enthalten keine verlagerte Fachprüfung.

Liste/Metadaten/No-op/Reassign lesen ausschließlich `content/registry.json`, `game/data/registry.json`, `content/categories.json` plus eigene Transaktions-/Transportdaten. Detail ergänzt genau die ausgewählte Definition und aktuellen Reveal-/Hintergrundreferenzen; Bilder werden nur sichtbar bedarfsweise geladen. Raster ergänzt die aktuelle Rating-/Methodenbindung und neue eigene Proofs. Die genauen Pfade, Opens, Verzeichnisereignisse und Bytezählungen für alle 42 Messungen stehen in [evidence.json](evidence.json).

Zwei sichtbare Detailbilder und kombinierter Neueingang jeweils höchstens 10 MiB. Uploads: echte PNGs 1.200×1.000 und 2.304×576, zusammen knapp 10 MiB, pro Wiederholung andere Bytes. Kleine Raster sind echte unterschiedliche 3×2-Matrizen mit bestehendem Solver/Rating und unabhängiger Proofprüfung. Reassign bearbeitet im synthetischen Fall die Kategoriezuordnung aller 1.000 Einträge. Die Zeiten sind Sekunden, vollständig und ungerundet zusätzlich im JSON.

| Einträge | Szenario | Erster Lauf / Wiederholung 1 / 2 (s) | Grenze (s) | Max. gelesene Bytes / kleinste zulässige Grenze | Max. gesamte Hashbytes |
| ---: | --- | --- | ---: | ---: | ---: |
| 56 | Liste | 0.142919 / 0.133209 / 0.143250 | 1 | 220,187 / 1,759,384 | 177,980 |
| 56 | Detail + sichtbare Bilder | 0.634258 / 0.184355 / 0.232928 | 2 | 189,203 / 1,785,592 | 10,301,497 |
| 56 | Name/Kategorie: Prüfen + Übernehmen | 0.563676 / 0.555563 / 0.584732 | 3 | 860,174 / 2,464,944 | 1,797,982 |
| 56 | No-op | 0.452460 / 0.479017 / 0.478231 | 3 | 364,747 / 1,759,384 | 361,506 |
| 56 | Abschlussbild + eigener Hintergrund | 3.635284 / 3.650347 / 3.664142 | 5 | 71,898,655 / 83,423,004 | 157,311,259 |
| 56 | Echte Rasteränderung 3×2 | 4.253139 / 4.249703 / 4.262765 | 5 | 868,298 / 2,421,844 | 4,001,828 |
| 56 | Kategorie löschen/neu zuordnen | 0.458731 / 0.463285 / 0.482481 | 10 | 863,779 / 2,470,288 | 1,807,227 |
| 1000 | Liste | 0.441516 / 0.355187 / 0.356586 | 1 | 1,516,567 / 6,944,904 | 1,474,360 |
| 1000 | Detail + sichtbare Bilder | 0.860512 / 0.425333 / 0.526736 | 2 | 1,481,278 / 6,958,916 | 11,593,354 |
| 1000 | Name/Kategorie: Prüfen + Übernehmen | 1.718155 / 2.221936 / 2.222690 | 3 | 6,090,516 / 12,835,984 | 13,876,044 |
| 1000 | No-op | 1.705947 / 1.686806 / 1.714173 | 3 | 3,020,013 / 6,944,904 | 2,951,490 |
| 1000 | Abschlussbild + eigener Hintergrund | 4.695786 / 4.646200 / 4.679483 | 5 | 77,112,294 / 93,770,312 | 169,339,545 |
| 1000 | Echte Rasteränderung 3×2 | 2.783638 / 3.231777 / 3.218749 | 5 | 5,167,063 / 11,003,760 | 12,585,075 |
| 1000 | Kategorie löschen/neu zuordnen | 1.532083 / 2.118255 / 2.115448 | 10 | 6,493,148 / 12,880,896 | 14,693,783 |

Alle Einzelmessungen erfüllen ihre Zeit- und Lesegrenze. Grenze: `4 × verschiedene erlaubte aktuelle Eingangs-/Alt-/Neubytes + 1 MiB`. Gemessene Lesezahlen enthalten konservativ auch eigenes Journal und privaten Jobtransport. Browserbildladen, gebundene Programm-/Methodendateien und neue Proof-Artefakte sind im JSON getrennt ausgewiesen. Die letzte Spalte enthält sämtliche erfassten SHA-256-Bytes, einschließlich kanonischer Plan-/Journalrepräsentationen und Speicherhashes; sie ist keine bloße Dateihashsumme und unterliegt nicht der Inhaltslesebytegrenze.

Jede gewöhnliche aktuelle Byteversion wird höchstens viermal vollständig gelesen/gehasht, auch über Kopien im Speicher hinweg; dies wurde gegen globale SHA-256-Aufrufe geprüft. Neue Rasterdefinition/Proofs einer echten Logikänderung sind separat: bestehende Solver-/Ratingkonsumenten hashen ihre kleinen neuen Definitionen (397/561 Byte) teils 22–27-mal. Diese neu erzeugte fachliche Proofarbeit ist vollständig gezählt, keine wiederholte Prüfung alter Definitionen oder fremder Archive. Unveränderte Matrix löst keinen Solver aus; No-op erhält Dateien und mtimes.

## T02 · Integrität und Kompatibilität

25 fokussierte Regressionen bestanden (34,858 s): `python -m unittest tests.puzzle_production.test_editor_change tools.test_puzzle_editor`. Erfasst sind erlaubte Dateimengen, No-op, Konflikt trotz gleicher mtime, gemeinsamer Lock, Unterbrechungen vor/nach Journal und Zielersatz sowie nach Runtime, wiederholte Recovery, fremder Zielzustand, Hardlink/Savepfad-Fälschung, ausgewählte Identitätsbindung und gebundene Bilddeltas. HTTP-Sitzung/Origin/Host/CSP/Listener und Instanzgrenzen bleiben geprüft. Ein tatsächlicher NTFS-Junction-Negativfall verweigert den ersten Indexzugriff. Unbekannte und partielle Journale bleiben erhalten.

Eine gültige 32-MiB-SVG wurde vollständig importiert, geprüft, übernommen und dargestellt (4,6034614 s), Bytes unverändert. Die tatsächlich kompilierte EXE konnte ein absichtlich nach Runtimepublikation unterbrochenes altes v7/v8-Journal zurückrollen; zweiter Recoverylauf war No-op und sämtliche ursprünglichen Bytes stimmten. Das benötigt keinen Migrator im Paket. Neue Bild-/Rasterquellen bestehen explizite Diagnose/Replays; eine echte normale Folgeproduktion erhält manuell gewählte SVG, Metadaten und explizit „kein Hintergrund“. Keine echte Datenmigration wurde dafür ausgeführt.

## T03 · Tatsächliche portable Windows-Bedienung

Version 0.2.0 wurde aus dem sauberen Produktcommit gebaut und aus dem endgültigen ZIP frisch entpackt. Alle 1.145 inventarisierten Programmdateien wurden geprüft. Native EXE zweimal als Standardbenutzer gestartet, jeweils über eigenes natives Fenster bedient; eigenes Edge-Fenster mit isoliertem Profil. Der Eigentümer hat diese Desktopbedienung ausdrücklich erlaubt. Gesamter Ablauf am endgültigen Build bestanden:

- 1.000 virtuelle Einträge, weniger als 30 gleichzeitig gerenderte Zeilen, unabhängiges Scrollen, A–Z/Z–A/Kategorie, Tastaturauswahl.
- Ungültige Rastereingabe zeigt Zeile/Spalte und löscht die falsche Vorschau; gültige lokale Vorschau/Fit ohne Fachjob. Echte 16×12-T-Matrix gespeichert.
- Unverändertes vorhandenes Zitronen-PNG importiert; eigene/keine/Kategoriezeichnung vor und nach Speichern korrekt; echte Papier-/Spielressourcen, Alpha und Bildfarben erhalten.
- Speichern und Verwerfen erhalten Suche, Auswahl und Scrollposition. Gesamte helle/dunkle Oberfläche einschließlich Dialog und Fehler; kein Inhaltsdirty oder Fachworker durch Theme.
- Reload sowie vollständiges Beenden und Neustart ohne Checkoutargument, Port 65512 → 50385: Checkout und dunkles Theme erhalten. Beide nativen Prozesse und eigener Browser ordentlich beendet.

Genau zwei unveränderte Original-PNGs: 1.700×1.200 Browserviewport, frisches eigenes Profil mit 100 % Browserzoom. Sie zeigen denselben ausgewählten Datensatz, echte Raster-/Papierkomposition, links die virtuelle Auswahl. Lokale und anschließend veröffentlichte, binär erneut heruntergeladene Originale wurden geöffnet und geprüft. Alle fünf Dateien am Belegcommit `4fd106b4b706c6f4107f1bc905c43903264fb7eb` waren bytegleich; das ZIP wurde entpackt und sein vollständiges Inventar erneut geprüft. Der direkte Windows-gh-Ausgabepfad scheiterte mit `transform: short source buffer`; authentifiziertes binäres HTTP-Streaming über die Contents-Raw-API funktionierte. Keine Umkodierung oder Verkleinerung. Die unabhängige Sichtung bleibt Aufgabe des Reviewers.

| Datei | Bytes | SHA-256 |
| --- | ---: | --- |
| [light.png](light.png) | 505,822 | `bb4ae963f89417aca8cf7836cee4a75f8eb36a017609db30d9edc5daa16384dd` |
| [dark.png](dark.png) | 505,707 | `ebafa4d378044e0828e7b011896846ac8a1dba4b1424718f79ec8e708a9c1b9b` |
| [Picross-Bestandseditor-windows-x64.zip](Picross-Bestandseditor-windows-x64.zip) | 30,022,701 | `4a345e82b279bcc21d13bb83e4cd3718ad3433dfde2aa32bc850a4b6e858a23c` |

EXE-SHA-256: `a710b5f5eb0ce51f3bc419f2fa4ee187227155bc303bf671f232a087a479db5d`. Python/Tk/Bibliotheksversionen und Buildzuordnung im JSON; Lizenzen und Inventar im portablen Paket.

## CI, Zustellung und offene Abnahmen

[CI-Lauf 43612452543, Versuch 1](https://github.com/venomenon328/picross/actions/runs/43612452543) bindet obigen Head/Basis/Test-Merge. Kern mit Windows-Spieler sowie vollständige Module `tools` und `production.catalog`; keine zusätzliche Chromium-Matrix. Endergebnis vollständig erfolgreich: docs 13 s (21 Kerntests), tools 1 min 40 s (497 Tests / 82,605 s), production.catalog 17 min 59 s (vollständiger Modullauf 1.063,397 s), player 1 min 5 s, ci-required 2 s. Gesamte Laufspanne 18 min 21 s; das weiche Zehn-Minuten-Ziel ist überschritten. [Regulärer Windows-Spieler](https://github.com/venomenon328/picross/actions/runs/43612452543/artifacts/14121090567): 130.169.884 Byte, Ablauf 28.11.2026 15:53:08 UTC nach bestehendem Produktvertrag; auf Linux gebaut, kein nativer Spielertest behauptet. Davon getrennt wurde der hier gelieferte portable Editor tatsächlich nativ unter Windows bedient. Abgebrochene frühere Läufe zählen nicht als Pass.

Diese fünf Dateien liegen ausschließlich im temporären Branch `review/640-pe-edit2`, vom geprüften Produkt-Head abgezweigt. Kein Merge-PR für den Belegbranch; kein Übernehmen seiner Dateien in den Produktbranch. Zweck/Empfänger: unabhängiger Reviewer von PE-EDIT2-A01 mit Repositoryzugriff und binärfähigem Git/HTTP-Client. GitHub-Contents-Raw mit `Accept: application/vnd.github.raw+json` oder echter Checkout liefert unveränderte Bytes. Ein textgebundener Connector kann insbesondere am ZIP scheitern; Metadaten sind kein Download.

Endpunkt **21.11.2026, 15:00 UTC**, weniger als sieben Tage ab Veröffentlichung. Zuständig für den beauftragten Rückbau ist der implementierende Codex bei Abschluss der Reviewübergabe: eigenen Reviewref nach abgeschlossener Sichtung entfernen; spätestens zum Endpunkt Bedarf und Zustellung erneut prüfen. Keine automatische Löschung behauptet. Bis zur erforderlichen Prüfung bleiben die Originale erreichbar; bei späterer Prüfung gezielt erneut zustellen.

**Offen:** PE-EDIT2-A01 (unabhängiges Review, before_merge), PE-B-U01 in #576 (persönliche Eigentümerprobe, before_release), separate reale M2-Übernahme der aktiven Quellen in #641. Keine Merge-/Releasefreigabe aus diesen Implementierernachweisen ableiten. Kein Merge durchgeführt.
