# B-B-T01 · Reguläre Buchintegration

Paket: [#498 / B-B-V01](https://github.com/venomenon328/picross/issues/498),
übergeordnet [#493](https://github.com/venomenon328/picross/issues/493).
Basis: `2a0d9e4ae21802637dc26ff8fdf904bf27772972`, Branch
`feat/493-book-integration`. [Aktueller Vertrag](BOOK_INTEGRATION.md).

Die konkrete Lieferung wird im
[B-B-T01-Lieferindex von Draft-PR #499](https://github.com/venomenon328/picross/pull/499#issuecomment-6574847402)
gebunden: vollständiger Head, Basis, Test-Merge/Checkout, CI-Run/Attempt,
Windows-/Webexporthashes, Originalzugriff, Laufkosten und Ergebnisstatus.
Dieser Index gehört zu T01 und wird nach den tatsächlichen Läufen aktualisiert;
ein lokaler Zwischenstand oder die folgende Prüfzuordnung ist kein CI-Pass.
Das getrennte Selbstreview wird dort als eigener PR-Kommentar verlinkt.

## Akzeptanz und tatsächlicher Prüfweg

| Kriterium | Implementierung und gebundene Belege |
| --- | --- |
| A01: regulärer Start/Katalog | `main.tscn` → `book/main.gd` → vorhandener Produktladeweg. Native Lifecycleprüfung unterscheidet leere/fehlerhafte Kataloge, Null-Session und ungültige einzelne Saves. Kataloggruppe prüft globale Filter/Sortierung, Seiten, beide Scrollbereiche, Miniaturen und Slotisolation. Reguläre Windows-/Webstarts und tatsächlicher PCK-Audit ergänzen die synthetischen Komponentenfälle. |
| A02: gewählte Navigation | Gemeinsamer nativer Buchnachweis prüft Öffnung/Rückkehr, zehn Informationsrouten, getrennte Ursprünge, Scrollstände, Einstellungen, Reset und Unterbrechungen. Originalbericht und reale Bewegungsfolge binden N01–N21/N06. Die regulären Integration-, Windows- und Chromiumwege benutzen denselben Präsentationskern. |
| A03: Speicher-/Fehlergrenzen | `book_integration.gd` verwendet den echten SaveStore und einen tatsächlichen Dateisystemfehler. Fehlgeschlagener Flush sperrt Rückkehr, Information und Quit vor Vorbereitung; Primärbytes und ausstehender Zustand bleiben. Retry muss sichtbar sein, tatsächlich speichern und auch im gefilterten Katalog die Fehlermeldung sofort entfernen. Capture, Rückkehr und passive Öffnung dürfen Savebytes nicht neu schreiben. Generation/Quell-ID werden über abgebrochene und veraltete Fortsetzungen geprüft. |
| A04: Kompatibilität/Recovery/Beenden | Eingefrorenes `book-save-v1.json` prüft Schema 1, History/Redo, Werkzeug/Farbe, Zoom und Hinweisanker ohne Migration. Fremde Slotbytes bleiben unverändert. Backup ohne Primary bleibt bis zur bestätigten ID-gebundenen Übernahme schreibgesperrt; Fehler-/Recoveryanzeigen bleiben erreichbar. Null-Session-Close beendet den echten Prozess. Kurze Historyroute: höchstens 20 Kommandos, sechs neue Transaktionen, genau zwei Prozesse. Chromium prüft bestätigten bestehenden IndexedDB-Sync, Neustart, Tab-Sperre und Fehler/Retry. |
| A05: Eingabe/Material/Ressourcen | Vier Layouts: 1280×720/UI125, 1920×1080/UI100, 2560×1440/UI125, gezielt 1920×1200/UI100. Gemeinsamer nativer Bericht prüft mindestens acht physische Pixel Papierrand, vorhandene Trefferbudgets, F01-Tooltip/Release, N06-Fokus und Capturegrenzen. Neun Textur-/Direktübergaben behalten maximal vier Kanalstufen und Mittelwert ≤0,1; Einpixel-/Alpha-Gegenproben bleiben wirksam. Neuer Windowslauf prüft echte Pointerwege, Standard→Maximieren→Wiederherstellen, Informationsseiten sowie Save-/Quitfehler. |
| A06: Exporte/Web | Reguläre PCKs müssen den neuen Root, erforderliche Buchressourcen und Rechte enthalten und technische Studien-/Prüfbeigaben ausschließen. Zwei tatsächliche negative Ressourcenüberlagerungen lassen den PCK-Guard am alten Einstieg und an einer Studienbeigabe scheitern. Chromium `short` umfasst die vorhandenen neun Kernfälle und genau zwei Exporte; echte Eingabe am neuen Root, reguläre HTML-/Storagehülle, keine Zustandssetter als Spielnachweis. |
| A07: Lieferung | Der Lieferindex bindet aktuelle Pflicht-CI und `ci-required`, den ausdrücklich manuellen Chromiumlauf, neuen Windowslauf, Originalsichtung, Kosten und Exporthashes. Vollständiger Diffcheck und getrenntes Selbstreview ergänzen die Producer-/Ergebnisguards. Offene Gates bleiben ausdrücklich offen. |

`tools/book_contract.py` ist das gemeinsame Quellen-/Assertioninventar.
Producer und unabhängiger Ergebnisprüfer verlangen die tatsächlichen
Originalberichte, Phasen, Pflichtassertions und SHA-256-Bindungen; fehlende,
fehlgeschlagene oder falsch gebundene Teilbelege ergeben keinen Erfolg.
Die alten kleinen Komponentenfälle verwenden `tests/book_fixture.gd` am
tatsächlichen Entrypoint mit synchroner Stabilisierung. Sie belegen Logik und
Geometrie, keine reale Animationsdauer. Dafür dienen die unveränderte Produktuhr
der Lifecycleprüfung, gemeinsame native Bewegung, Windows und Chromium.

## Entwicklungsbefunde und Beleggrenzen

Der lokale Entwicklungsstand `173a162742d933fa890a59ccc949d44a810091c2`
bestand 1125 gemeinsame native Assertions und alle neun strengen Handoffs mit
Gegenproben. Gemessene Phasen: Version 1,263 s, Import 9,950 s, reguläre
Integration 30,215 s, gemeinsame native Prüfung 192,356 s und Film 25,451 s.
Die reale Bildfolge enthält 644 Frames bei 30 fps (21,467 s). Die eigene Sichtung
umfasste gebundene Bewegungszwischenbilder sowie Originale für Arbeit,
Information, Falzrand und Windowsfehler. Sie wird für die abschließende Lieferung
anhand ihrer aktuellen Originale ergänzt; keine behauptete persönliche Abnahme.

Der damalige exportierte Windowslauf dauerte 74,081 s und bestand 32 echte
Pointer-Rundwege, Zellaktionen, Undo/Redo, Farbwechsel, Release außerhalb,
Fokus/Resize, UI100/UI125, Maximieren/Wiederherstellen und Save-/Quitfehler mit
Retry. Spätere Layout-/Savekorrekturen verlangen den separat freigegebenen kurzen
Abschlusslauf. Dieser Zwischenstand ersetzt ihn nicht. Desktop, tatsächlicher
Client/Framebuffer, OS-/UI-Skalierung, DPI und Renderer stehen getrennt in den
Rohberichten; Linuxbilder ersetzen keinen Windowsnachweis.

Die CI-Nacharbeit korrigierte veraltete Navigationsannahmen kleiner Prüfungen,
einen überlappenden Kopfbereich, die Kartenwahl in gescrollten Albumhälften und
einen echten ausstehenden Savefehler beim Informationswechsel aus dem Katalog.
Der Retry beseitigt die Fehlermeldung sofort unter Erhalt des Filters.
Pixelgrenzen, Produktzeiten und die 300-s-Phasengrenze bleiben unverändert.
Fehlgeschlagene Zwischenläufe einschließlich Chromium-Grafikinitialisierung
werden im Lieferindex vom abschließenden Erfolg unterschieden.

CI2-Ziele werden anhand tatsächlicher Job-/Phasendauern und Artefaktbytes
beurteilt. Ein überschrittenes Zeitziel wird offengelegt, kein erfolgreicher
Pflichtjob oder Ergebnisguard durch eine Laufzeitbehauptung ersetzt. Keine
allgemeine CI-Optimierung oder zusätzliche historische Replaypflicht.

## Originalzugriff und getrennte Gates

Der Lieferindex verlinkt eine begrenzte Auswahl unveränderter Originalbilder,
Rohprotokolle und den gebundenen realen Bewegungsnachweis. Er nennt jeweils
Quellstand, Dateihashes und Zugriff sowie Sichtungsumfang. Technische
Actions-Artefakte bleiben sieben Tage, Spielerartefakte vierzehn Tage verfügbar;
eine darüber hinaus für R01/M01 benötigte Auswahl erhält einen konkreten
Aufbewahrungszweck und wird nach diesen Gates bereinigt. Lokale Pfade allein
sind kein zugänglicher Reviewbeleg.

Die exklusive Windows-/Mausrunde ist nach Eigentümerentscheidung vom
02.11.2026 ausschließlich für diese Entwicklung beauftragt. Sie wird nicht
Standardprüfung und benötigt vor jedem neuen Desktopblock Freigabe.

B-B-R01 ist eine getrennte unabhängige technische und visuelle Prüfung;
B-B-M01 eine getrennte persönliche Funktions-/Komfortabnahme. Beide werden
weder durch diese Implementierung noch durch Selbstreview ersetzt. Kein Merge,
Deployment, automatisches Schließen von #498/#493 oder behaupteter Browserpass.
