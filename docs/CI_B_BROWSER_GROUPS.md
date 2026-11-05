# Ausdrücklich manuelle Chromiumprüfung

Diese Seite beschreibt den aktuellen Diagnoseumfang, keine automatische
Browserpflicht. Auslöser und Befugnisse folgen [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md).
Die Fachzuordnung steht in [tools/web_tests/contract.py](../tools/web_tests/contract.py).
Firefox gehört nicht zur CI; seine Produkterprobung ist eine getrennte Frage.

## Umfang und Originalprüfung

Die automatische Package-CI und allgemeine Diagnosescopes bleiben browserfrei. Nur der registrierte
`ci-chromium.yml`-Dispatch mit explizitem `browser_scope` startet Chromium.
`short` und der kompatible Browserwert `all` wählen genau neun Kernfälle;
`all` im allgemeinen `scope` bleibt browserfrei. Keine automatische Zusatzmatrix.

| ID | Gruppe | Tatsächlich geprüfter Übergang |
| --- | --- | --- |
| regular-start | regular | Uninstrumentierter Spielerstart, WebGL2, Storage, offline nach Start, keine Fehler |
| C01 | catalog | Metadaten/Tidy-Hand-Rollen, Kategorie-/Sortier-/Ansichtsmenü, Sortierung/Richtung, stabile Öffnungs-ID |
| C02 | input | Echter elastischer Strich, Rechtsstrich, atomarer Undo/Redo, Escape ohne Phantomcommit |
| C03 | input | UI100→125→100, 720p/1080p, Live-DPI150 und tatsächlicher Zelltreffer mit Undo |
| C04 | completion | 5×5-Lösung durch einen Strich, natürliche Überblendung, Endbild/Wiederöffnung, verdientes Katalogbild samt Hover, Resetabbruch und bestätigter Reset mit fremden Savebytes |
| C05 | persistence | Echter Sperrhandoff vor Hydration und abgewiesener Zweittab ohne IDB-Zugriff |
| C06 | persistence | Bestätigter IDBFS-Sync und Reload mit Zellen, History, Redo, Ansicht und Sortierpräferenz |
| C07 | persistence | Echter zweiter Browserprozess im gleichen Profil, DPI125, geladener Stand und wirksamer Redo |
| C08 | persistence | Fehler an der tatsächlichen IDB-Transaktionsgrenze, blockiertes Beenden, sichtbarer Retry und erneuter Reload |

Der normale Viewport 1920×1080/UI100 trägt die ausführliche Katalog-/Bildprüfung.
Weitere Größen stehen ausschließlich in C03. Der HZ-Rückwechsel liefert
Zustandsmessungen, keine wiederholte Fünfergalerie. Es entstehen zwölf
Erfolgs-PNGs (eins davon ein beobachteter echter Übergangsframe), ohne Überschreiben.
Keine großen Vorbereitungsdurchspiele; sämtliche Zustandsübergänge oben verwenden
Browserinput, keine Probe-Setter. Produktanimationen bleiben unverändert.

`browser_scope=regular` benötigt nur `web-player`; jede technische Kerngruppe
zusätzlich `web-test`. Der kurze Gesamtumfang baut somit zwei Exporte.
`browser_scope=export` ist ein **separates** Profil für Export-/Bildkompatibilität:
regular-start plus E01, zwei Fälle, drei Exporte einschließlich eigenständigem
`web-test-update` mit zweiter Bildrevision. E01 prüft begonnenen und gelösten
Stand über Reload und echten Prozessneustart am selben Origin. Unterschiedliche
Build-IDs/Bauzeiten und exportgebundene Bildbytes sind Pflicht; kein Alias.
Dieses Profil wird von `short`/`all` und Dateipfaden niemals ergänzt. Es benötigt
einen eigenen konkreten Auftrag.

Build-/Browserberichte heißen `picross-web-builds-v2` und
`picross-browser-result-v2`; Auswahl-/Gesamtergebnis bleiben im v6-Schema.
Das Gate prüft exakt benötigte Exporte, Originalberichte, eindeutige Szenarien,
Ausführungslog, endliche Phasen-/Operationsmessungen, Pflichtdateien und Hashes.
Leere/fehlende/doppelte/fehlgeschlagene Ausführung scheitert. Originalinput-,
Head-/Base-/Checkout-/Run-/Versuchsbindung und Wiederholungsregeln aus A/B bleiben.
Browserkürzung ändert `at_evidence.MATRIX` für native Prüfungen nicht;
`BROWSER_MATRIX` ist getrennt. Die Originalpixelprüfung bleibt erhalten.

Seltene Varianten bleiben auf ihrer günstigsten passenden Ebene: Savevalidierung,
Recovery/Revision und Slotisolation in den bestehenden nativen Savefällen;
Sortierschlüssel/Gleichstände/Präferenzen in `game/tests/ku_b_cases.gd`;
Glyphen-/Popup-/Geometriegrenzen in HZ-/VS2-Fällen. Der schnelle Node-Test der
unveränderten `game/web/storage.js` prüft serialisierte echte Bridgecallbacks
gegen synthetische FS-Antworten, fehlende Persistenzfähigkeit, Generationen,
Ansichtspending, Fehler/Retry und getrennte Präferenz-/Savefehler. Das sind keine
IndexedDB-Nachweise; diese liefern C06–C08. Node kommt vom vorhandenen Runner,
keine npm-Pakete, kein neuer Job. Native History-/Bildmengen werden hier nicht gekürzt.

Der Gruppenprozess hat einen 360-s-Hängerschutz. Das frühere vier-/siebenminütige
Joblimit sowie das verpflichtende Acht-Minuten-Gesamtziel gelten nicht mehr.
Zehn Minuten sind gemäß [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md) ein weiches Ziel;
Queue, Build, Browser und Upload getrennt messen. Funktionale Speicher-/Animations-
zeitfenster bleiben davon unabhängig.

## Ausführung, Transport und Aufbewahrung

Der manuelle Einstieg [ci-chromium.yml](../.github/workflows/ci-chromium.yml)
ruft [web-chromium.yml](../.github/workflows/web-chromium.yml) und anschließend
[browser-chromium.yml](../.github/workflows/browser-chromium.yml) auf. Vor Setup
prüfen sie den ursprünglichen Dispatchinput; ein nachträglich passender Plan
allein erteilt keinen Browserauftrag. Der aktuelle Linuxweg nutzt isolierte
Profile/Origins, Xvfb/Mesa und ausschließlich Chromium; Details der Buchszene
stehen in [BOOK_INTEGRATION](BOOK_INTEGRATION.md).

`regular` verwendet den uninstrumentierten Export. Technische Gruppen erhalten
eigene Profile, Loopbackports und veränderliche Hostingbäume; Zustände werden
über echte Eingabe hergestellt. Die erforderliche Reload-/Neustartfolge teilt
gezielt ihr eigenes Profil, keine Ergebnisse anderer Gruppen. Fehler einer Gruppe
verhindern den Gesamterfolg, auch wenn weitere Gruppen Diagnosen liefern.

`Diagnostic result` prüft echte Originalberichte, eindeutige Szenario-IDs,
Phasen-/Operationswerte, WebGL-/Builddaten und sämtliche benötigten Dateihashes.
Ein positives Web-Jobergebnis allein genügt nicht. Fehlend, leer, doppelt,
unerwartet, übersprungen, abgebrochen oder fehlgeschlagen ist kein Erfolg.
Head, Basis, Checkout, ursprüngliches Event, Run und Versuche bleiben gebunden:
Auswahlversuch ≤ Buildversuch ≤ Browserversuch ≤ Gateversuch. Ein Branchdispatch
ist kein behaupteter PR-Test-Merge-Lauf.

Der explizite Diagnoseauftrag erzeugt die dafür nötigen temporären Transport-
und Reviewbelege `ci-web-builds-*` und `picross-web-chromium-*` für sieben Tage;
der reguläre `picross-web-player-*` bleibt vierzehn Tage. Profile/Hostingbäume
werden nicht hochgeladen. Keine dauerhafte Screenshotgalerie, keine Wiederholung
historischer Bildmatrizen; dieser manuelle Belegtransport begründet keinen
Standardupload in Package CI. SSH/HTTP-Prüfung ist davon getrennt und kein Browserbeleg.

## Herkunft und Abnahme

[CI2-C-T01](CI2_C_VERIFICATION.md) bindet Einführung und damalige Messungen.
Der vollständige [Vorgänger mit den 27/30/31/33-Fall-Matrizen](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/CI_B_BROWSER_GROUPS.md)
bleibt historisch erreichbar; alte v4-Auswahl, implizite Browserscopes und
pauschale Drei-Exportpflicht sind kein heutiger Vertrag.

Aktuelle Nachweise an den tatsächlich geprüften Stand binden. Synthetische
Workflow-/Gate-Gegenproben ersetzen keinen echten Browserlauf; Browserprüfung
ersetzt keine vereinbarte persönliche Abnahme und erteilt keinen Merge-/Liveauftrag.
