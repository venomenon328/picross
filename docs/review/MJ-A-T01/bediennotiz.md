# MJ-A-T01 · einmalige Offlinebedienprobe

Produkt-Head: `81b582f7d275f4e1cf8996f3f006e42c2e10efa9`, PR #572.
Quelle: [Paketentscheidung MJ-A](https://github.com/venomenon328/picross/issues/490#issuecomment-6774440064).
Ausgeführt am 10.11.2026 durch Codex als technische Nachweislieferung; unabhängiges MJ-A-A01 bleibt offen.

Chrome 157.0.8103.50 unter Windows 11 (NT 10.0.26200.0), ausdrücklich lokal mit eigenem leerem Profil gestartet, ohne Headlessmodus oder Sicherheitsbypass. Echte Bedienung über Playwright-core 1.65.0/CDP: Klicks, Formulare, Auswahllisten, Dateieingaben, native Bestätigungen, Scrollen und Downloads. Geladen wurde ausschließlich die bytegleiche lokale Produkt-HTML-Datei per `file:`; Browserkontext offline, keine externen Seitenressourcen. Kein Node-DOM-Stummel und keine gesetzten internen Appzustände. Kleine synthetische JSON-Eingaben sowie selbst erzeugte 16×16-PNGs; keine Produktions- oder Nutzerdaten.

| Tatsächlich ausgeführt | Ergebnis |
| --- | --- |
| Zehn Jobs A–J, sieben unterschiedliche angezeigte Phasen inklusive Briefing; A zuerst ohne Produktions-ID, später pz-t01-a | Lokale Kennung erhalten; aktive Auswahl eindeutig. |
| Ungesicherte Bearbeitung, A→B→A und B→A→B, getrennte Ablage-/Merge-/Regeloptionen, source/reveal-Anhang | Daten und Optionen isoliert erhalten; Defaults neuer Jobs blieben eigenständig. |
| Nackter Record v2, lokal zugeordnetes Update v3, Vorschau verwerfen und danach als neuen B übernehmen | Ohne Projektion Übernahme gesperrt; Verwerfen ließ A allein. Paarübernahme erzeugte genau B und zeigte überlieferte Blocker ausdrücklich als nicht frisch geprüft. |
| Eigenständiges Update v3 auf bestehenden B; Sitzung aus echter Download-Datei wieder laden | Ziel, Revision, Inventar, Optionen und Anhang in Vorschau sichtbar; nur gewählter Job geändert. |
| Zwei Rasterangebote B, Auswahl raster-b/r02; zwei Revealangebote C, Auswahl reveal-b; Jobwechsel | Paket-/Inventarbindung gemeinsam gewechselt, Variantenwahl erhalten. |
| Drei getrennte Hintergrundrefs; bg-2→bg-3→bg-2 mit Revealanhang, separater Motivrollenexport | Auswahl bleibt bloße Absicht, offered bleibt offered; Entscheidung/Ableitung bleiben null. Kein Überschreiben des Rollenanhangs. |
| Fremde nichtleere Rätsel-ID, doppelte lokale Job-ID, inkonsistente ID/Paketbindung | Import ohne Teilmutation abgewiesen, zehn Jobs erhalten. |
| Bestätigter Reset J, Sammlungswiederherstellung erst verworfen, dann übernommen; temporären elften Job bestätigt entfernt | Reset betraf J; Verwerfen erhielt den Reset, Übernahme stellte die Basissammlung wieder her. Ursprüngliche zehn Jobs erhalten. |
| A-/B-Sitzungen, A-Auftrag und B-Reveal-/Motiv-Auftrags-ZIPs tatsächlich heruntergeladen und geöffnet | A v3/0.6.0-docrev45; B v4/0.7.0-docrev6. Passende Job-ID, Raster r02/Inventar b…b, bg-2, Regeltext und Originalanhang; alle Inventargrößen und SHA-256 frisch abgeglichen, keine A/B-Vermischung. |
| Sammlung tatsächlich heruntergeladen, geöffnet, importiert und erneut exportiert | JSON-inhaltlich identisch: zehn geordnete Jobs, lokale IDs, aktiver A, Felder, Optionen, Varianten und Anhangsbytes. |

## Layout und Originale

`01-jobs-1440x900.png` zeigt alle zehn Jobs und aktiven B. `02-background-1280x800.png` zeigt die echte Importvorschau, raster-b, den unabhängigen Revealrollenanhang und bg-2 mit den drei getrennten Referenzzeilen. Browserzoom 100 %, devicePixelRatio 1. Beide sind direkte, unveränderte Viewport-PNGs; keine Montage, Retusche, Skalierung oder nachträglich eingefügten Texte. Maße, Zeitpunkte, Bytezahlen und SHA-256 stehen in manifest.json.

Kopf, aktive Jobmarkierung und Hauptaktionen sind lesbar. Lange Übersichtstexte haben Ellipsen; der vollständige nächste Schritt bleibt im Jobformular erreichbar. Bei 1280×800 braucht die Oberfläche Dokument- und linkes Formularscrollen. Hintergrundrefs haben eine eigene Scrollfläche; der dritte lange Hash liegt teilweise unter deren sichtbarer Kante. Im zweiten Aufnahmeausschnitt liegen Teile der oberen Ergänzungssteuerung und des unteren Bildbereichs außerhalb des Viewports. Die Importhauptaktionen und beide Auswahlen sind sichtbar; Bild speichern/Entfernen, Sitzung/Reset und Importaktionen wurden zusätzlich bei beiden Größen vollständig in den sichtbaren Bereich gescrollt. Keine unzugängliche oder horizontal abgeschnittene wesentliche Aktion festgestellt. Kein konkreter Produktfehler in diesem Umfang gefunden.

Eine erste Aufnahme hatte nach CDP-Neuverbindung versehentlich die tatsächliche Fenstergröße 1249×1277 statt der Sollgröße. Diese Fehlaufnahme wurde verworfen; die beiden gelieferten Originale wurden anschließend mit unmittelbar gesetztem und geprüftem Viewport erzeugt. Es gibt keine bearbeitete Ersatzaufnahme.

## Grenzen und Lebenszyklus

Die synthetischen Produktions-/Manifest-/Inventarrefs enthalten ausdrücklich Platzhalterhashes. Geprüft wurden Transport, Bindung, Bedienung und echte lokale Bilddekodierung, keine fremden Paketbytes, Solverproofs, Rechte oder menschlichen Freigaben. Die drei Hintergrunddateien wurden nicht geladen: die Oberfläche führt vertragsgemäß kompakte Referenzen. Kein erzwungener Promise-Racelauf, kein anderer Browser/DPI/Mobilumfang und keine Spielprüfung. Die dokumentierten CI-/Node-Belege werden dadurch weder ersetzt noch als frisch wiederholt ausgegeben.

Genau zwei PNGs, manifest.json und diese Notiz sind für den unabhängigen Reviewer A01 auf einem separaten temporären Reviewref vom Produkt-Head bestimmt. Kein Merge-PR und keine Übernahme in den Produkt-PR. Der konkrete Belegcommit und binäre Abrufnachweis werden im Draft-PR verlinkt. A01 öffnet und beurteilt die Originale selbst. Endpunkt: nach A01 mit gesondert beauftragtem Rückbau, spätestens 17.11.2026; kein automatischer Ablauf eines Gitrefs. Bei dann offenem Gate Zustellung/Frist erneut klären. Entbehrliche lokale Profil-, Eingabe-, Download- und Bedienhilfsdaten werden nach gesicherter Zustellung entfernt; die vier benötigten Belegdateien bleiben bis zur Prüfung erhalten.
