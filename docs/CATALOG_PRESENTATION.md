# Katalogetiketten und unbekannte Motive · KE

Stand: 17.10.2026 · Spezifikation 1.0 · freigegebenes Soll, noch nicht implementiert

Der Eigentümer hat diese Weiterentwicklung als Spezifikation freigegeben.
[Paket #233](https://github.com/venomenon328/picross/issues/233) führt Umsetzung,
Akzeptanz KE-A01–A08 und getrennte technische, Review- und Eigentümergates.
Eine Spezifikationsfreigabe ist weder Implementierung noch Mergefreigabe.

## Geltung und gezielte Ablösung

Ausgangsbasis ist `main@aa5cbeb3812f5fe1f7f5087beed38069240080e8` mit KK
aus [#174](https://github.com/venomenon328/picross/issues/174)/PR #176.
KE ersetzt dessen kombinierte Größen-/Moduszeile, Status rechts in der Fußzeile
und leere Bildfläche bei Neu. Der Verzicht auf Ganzkarten-Tooltips bleibt;
gezielte Modus-/Schwierigkeits-Tooltips kommen hinzu. Gleiche Karten, Reservierung
von Titel/Reset, Fehler-/Recoveryzugriff, Spoilergrenze und Öffnen über die Karte
bleiben verbindlich. Historische KK-R01/KK-M01 sind durch KE nicht abgenommen;
die einmalige Mergeausnahme für KK gilt nicht für KE.

[Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md),
[Zeichensprache](UI_DRAWING_STYLE.md), [Kategorien](CATEGORIES.md),
[ZA-1](ZA1_ADAPTER.md), [P1](PROTOTYPE_P1.md) und [CI-Policy](CI_POLICY.md)
gelten im übrigen Umfang weiter. Historische Prüfberichte bleiben unverändert.

## KE-D01 · Feste Kartenaufteilung

Alle Karten und Grid-Zellen haben bei gleichem Viewport und UI-Faktor dieselbe
Größe. Reihenfolge von oben nach unten:

1. Motivtitel erst nach gültigem Abschluss, sonst `???`; vorhandene Bakso-Rolle,
   höchstens zwei Zeilen mit bestehender Auslassungsregel. Reset oben rechts;
   sein Platz bleibt auch bei verborgenem Reset reserviert.
2. Kompakte Kategoriezeile: in „Alle Rätsel“ befüllt, bei Kategorienfilter leer
   und weiterhin reserviert.
3. Fester proportionaler Bildraum für Fragezeichen, eigene Füllminiatur,
   verdientes Reveal oder bestehende Fehler-/Recoverydarstellung.
4. Eine passive Infobox mit zwei Zeilen und zwei Spalten.
5. Feste Fußzeile mit „Blatt NN“ links.

| Infobox | Links | Rechts |
| --- | --- | --- |
| Oben | Breite × Höhe, etwa `20 × 15` | Gezeichnetes Moduspiktogramm |
| Unten | Schwierigkeit als Text | Statussymbol und Statuswort |

Die bisherigen doppelten Größen-/Modusangaben und der Fußzeilenstatus entfallen.
Das Etikett ist keine eigene Schaltfläche: Klick öffnet dieselbe Karte; Reset
und Recoveryaktionen behalten ihre eigenen vorhandenen Aktionen. Keine neuen
Filter, Sortieroptionen oder Fortschrittsanzeigen.

Die vorhandene kompakte Breite von ungefähr 220–240 logischen Pixeln ist die
Ausgangsbasis; Bildhöhe bisher 112 × UI. Die Infobox darf die Vorschau nicht zum
Briefmarkenbild verkleinern. Eine einmalig angepasste gemeinsame Kartenhöhe ist
erlaubt. Kategorie, mehrzeiliger Titel, „≈ Sehr schwer“, „Nicht eingestuft“, Status,
Reset und Fehlertexte müssen bei UI 100/125 % ohne Überlappung und ohne
zustandsabhängige Layoutsprünge funktionieren. Notwendige Metadaten bleiben
lesbar; der bestehende Titelauslassungsvertrag bleibt davon unberührt.

## KE-D02 · Papieretikett und Moduspiktogramm

Die Infobox wirkt wie ein kleines Inventaretikett des Rätselbuchs: warmes Papier,
leicht dunkler als die Kartenfläche, dünne subtil unregelmäßige Kontur, höchstens
ein sehr zurückhaltender Schatten. Kein schwerer Schmuckrahmen. Vorhandene
lesbare Plex-Schrift für Metadaten; Charakter entsteht durch Kontur und Zeichnungen.
Keine neue Schrift oder Änderung der vorhandenen Schriftdateien.

| Rätselmodus | Zeichnung | Erklärung im gezielten Tooltip |
| --- | --- | --- |
| Monochrom | Ein dunkler Stift mit dunkler Farbprobe | Monochromes Rätsel |
| Farbe | Drei aufgefächerte Stifte in gedecktem Rot, Blau und Gelb | Farbiges Rätsel |

Die Silhouette beziehungsweise Anzahl der Stifte unterscheidet die Modi auch ohne
Farbwahrnehmung. Alle Farbrätsel verwenden dasselbe Symbol; keine tatsächliche
Palette und keine Motivinformation. Der Modus beschreibt das Rätsel, nicht das
Abschlussbild: Auch ein monochromes Rätsel erhält sein farbiges Reveal.

## KE-D03 · Schwierigkeit ohne neue Bewertung

| Vorhandene Stufe | Anzeige |
| --- | --- |
| L1 | Sehr leicht |
| L2 | Leicht |
| L3 | Mittel |
| L4 | Schwer |
| L5 | Sehr schwer |
| Keine Einstufung | Nicht eingestuft |

Redaktionelle Schätzungen tragen sichtbar `≈`, beispielsweise „≈ Mittel“.
Ein gezielter Tooltip erläutert die vorhandene Bewertungsart und Unsicherheit,
die hinterlegte plausible Spannweite und gegebenenfalls notwendige
linienübergreifende Paarlinienlogik/R4. Er formuliert neutral aus typisierten
Metadaten; keine freien Produktionsnotizen oder motivbezogenen Engpassbeschreibungen.
Fehlende Informationen werden nicht erfunden. Keine Sterne, neue Solveranalyse,
menschliche Kalibrierung oder Ableitung aus Format/Farbzahl.

## KE-D04 · Status und Vorschau

| Gültiger Spielzustand | Anzeige | Bildraum |
| --- | --- | --- |
| Neu | Offener Kreis, neutral, „Neu“ | Gemeinsames gezeichnetes Fragezeichen |
| Begonnen | Stift, gedecktes Ocker, „Begonnen“ | Ausschließlich eigene Füllzellen |
| Abgeschlossen | Gezeichneter Haken, gedecktes Grün, „Fertig“ | Verdientes farbiges Reveal |

Symbol und Text erscheinen gemeinsam; Farbe allein trägt keine Bedeutung.
„Fertig“ ersetzt ausschließlich die Kataloganzeige „Gelöst“. Die vorhandene
Statusermittlung bleibt: gültiger Abschluss hat Vorrang; vorhandene History
einschließlich Redo oder nicht unbekannte Zellwerte bedeuten Begonnen, sonst Neu.
Keine Änderung an Abschluss, Save-Schema, History oder globaler Terminologie.

Das Fragezeichen ist eine eigene Zeichnung in warmem Graphit mit leicht
unregelmäßiger Kontur und dezenter Bleistiftschraffur, kein Zeichen einer normalen
Schrift. Es steht mit großzügigem Freiraum auf warmem Papier und nimmt ungefähr
die halbe Bildhöhe ein. Es bleibt statisch und identisch für alle neuen Rätsel,
ohne Leuchten, Pulsieren, Schattenmotiv oder andere Lösungshinweise.

Begonnene Vorschauen zeigen auch falsche eigene Füllungen unverändert. X und
unbekannte Zellen bleiben neutral. Ein begonnener Stand ohne Füllzellen, etwa nur
X oder nach Undo mit verbleibender History/Redo, zeigt eine leere Füllminiatur
und ausdrücklich kein Fragezeichen. Motivname und Reveal bleiben vor gültigem
Abschluss verborgen; kein vorzeitiges Laden des Reveals für den Platzhalter.

## KE-D05 · Fehler, Bedienung und Tooltips

Ein ungültiger Speicherstand darf nicht als Neu dargestellt werden. Vorhandene
Fehlerkennzeichnung, Diagnose, Backup-/Recoveryaktionen und Reset bleiben
erreichbar; Diagnose/Recovery nutzt weiterhin den festen Bildraum und wird nicht
vom Fragezeichen verdeckt. Kein neuer Statusautomat. Reset bleibt bei gültigem,
fehlerfreiem Neu verborgen und in den bisher vorgesehenen Bearbeitungs-/Fehler-
und Recoveryzuständen verfügbar; vorhandene Bestätigung und Ursprungsbindung bleiben.

Kein Tooltip über der ganzen Karte, auch nicht als Ersatz für abgeschnittene
Metadaten. Nur Modus und Schwierigkeit erhalten gezielte Erklärungen; der
vorhandene Resettooltip bleibt. Bestehende zugängliche Beschriftungen führen
Größe, Modus, Schwierigkeit und Status spoilerfrei mit. Kein umfangreicher
Accessibility-Umbau, keine Änderung der bestehenden Fokus-/Öffnungsbedienung.

## KE-D06 · Minimaler Metadatenvertrag

`content/registry.json` enthält bereits `production.difficulty`; die aktuelle
Runtimeprojektion v2 enthält diese Information noch nicht und validiert exakt
sieben Eintragsfelder. Die Umsetzung erweitert Writer, Loader und Validator
gemeinsam um minimale typisierte Katalogmetadaten. Benötigt werden die vorhandene
Stufe, Bewertungsart, Unsicherheit/plausible Spannweite und gegebenenfalls der
Nachweis notwendiger Paarlinienlogik. Methoden müssen eindeutig interpretiert
werden können. Ganze Produktionsobjekte, Freitexte, Motiverklärungen, Quellen,
Proofs oder Pakete dürfen nicht in den Spieler gelangen.

Die konkrete Feld-/Versionsbenennung ist ein Implementierungsdetail und wird im
gleichen PR in [CATEGORIES](CATEGORIES.md) und [ZA1_ADAPTER](ZA1_ADAPTER.md)
verbindlich fortgeschrieben. Der bestehende v2-/Siebenfeldervertrag darf nicht
stillschweigend umgedeutet werden. Vorhandene gültige Runtimeeinträge ohne
Schwierigkeit bleiben lesbar und zeigen „Nicht eingestuft“; ungültige vorhandene
Metadaten sind ein Validierungsfehler und werden nicht stillschweigend weggelassen.
Projektion und kanonische Byteprüfung bleiben deterministisch. Registrierungs-,
Update- und Recoverypfade müssen dieselbe kompatible Projektion verwenden.

Definitionen, Maße, Hinweise, IDs, Keys, Slots, Revisionen, Assets, Freigaben,
Paket-/Integrationsbindungen, Save-Schema 1 und Speicherroot bleiben unverändert.
Die Metadatenergänzung benötigt keine erneute Rätselproduktion, Zertifizierung
oder Paketfreigabe und darf keine Wiederherstellung gelöschter Produktionsdaten
verlangen. Bestehende Inhalts-/Exportverträge werden nicht neu bewertet.

## Prüfumfang und Übergabe

Ein Paket verbindet Projektion/Validierung, Gestaltung und Zustandsregressionen.
Feste synthetische Daten decken KE-A01–A08 ab; keine Tests oder Replays pro echtem
Produktionsrätsel. Geometrie und Darstellung werden in den drei gemeinsamen
Konfigurationen der aktuellen CI-Policy und bei UI 100/125 % geprüft, einschließlich
langer Texte, Filter/Seitenwechsel, Undo/Redo, Fehler/Recovery und Reset.
Native Windows- und Chromium-/Firefoxprüfungen folgen P1 und
[WEB-1](WEB_HOSTING.md). Technische Lieferung KE-T01, unabhängiges Review KE-R01
und Eigentümerprobe KE-M01 sind getrennte Gates vor Merge; konkrete Szenarien,
Verantwortung und Nachweise stehen im Issue/PR.
