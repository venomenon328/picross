# RZ-EVAL-P1 · begrenzter Rätselseitenversuch

Auftrag: [#558 / Paketentscheidung](https://github.com/venomenon328/picross/issues/558#issuecomment-6739323575).
Basis: `d65ffa78008b117bc4e2530b91d5f6821d3f9a00`. Nur Versuchsbranch/Draft-PR;
keine Bestandsintegration, endgültige Bildwahl, neue Authoringregel oder Mergefreigabe.
R01, Eigentümer-M01 und Ergebnisentscheidung D01 sind getrennte Schritte.

## Bildgrenzen und Stichprobe

Die fünf gebundenen IDs bleiben Tomate, Qualle, Chocolate Hills, Petronas Towers
und Stirnlappenbasilisk. **Das konkrete Rätselmotiv/Subjekt wird niemals gezeichnet.**
Auch kein Reveal, keine Lösungskontur und kein vom Fortschritt abgeleitetes Bild.

Eigentümervorgaben vom 09.11.2026: Qualle erhält Meeresboden, Seegras und einen
kleinen Schwarm winziger Fische; Petronas erhält glaubwürdige Kuala-Lumpur-
Impressionen ohne die Türme. Die übrigen Briefings sind offene Kontextentwürfe:
Gartenwerkzeuge, ländliches Bohol ohne die Hügel und tropisches Flussufer ohne Tier.
Die Tatsachenreferenz für Kuala Lumpur ist [Tourism Malaysia](https://www.malaysia.travel/explore/top-places-to-visit-in-kuala-lumpur);
es wurden keine fremden Bildbytes übernommen.

Späteres Eigentümerfeedback bevorzugt gleichbleibende Höhe, U- oder Halb-U-Form
mit niedriger Mitte, weil dort das Raster steht. Das ist keine strikte Höhenmaske.
Der Drei-Türme-Entwurf mit höchstem Turm in der Mitte wurde ausdrücklich verworfen.
Seine unabhängige Ersatzgenerierung bleibt Kandidat 1/rev2; das Original bleibt
im befristeten Belegsatz als Fehlversuch. Die übrigen Entwürfe wurden als Entwürfe
für okay befunden; das ist noch keine konkrete Bildabnahme auf dem Buchpapier.

Der erste Bohol-Entwurf wurde ebenfalls verworfen: Kleine ferne Hügelformen
widersprechen dem ausdrücklichen Subjektausschluss. Kandidat 1/rev2 ersetzt ihn
durch Handkarren und Bambuszaun ohne Landschaftshorizont. Auch dieser Fehlversuch
bleibt im befristeten Originalsatz.

Eigentümersichtung auf dem Buch: Tomate 1, Qualle 2, Chocolate Hills 1/rev2
und Basilisk 3 sind gewählt. Die bisherigen drei Kuala-Lumpur-Fassungen sind
abgelehnt; ihre Revision benötigt mehr Großstadt-Flair ohne Petronas Towers.
Die Bildwahl ist keine Serienübernahme. Der Eigentümer verlangt außerdem
dieselbe Durchlässigkeit für Hinweise und Raster und keine harten Bildabschnitte.
Die frühere separate Hinweisaussparung ist deshalb aufgehoben.

Es gibt drei aktuelle kreative Kandidaten je ID, insgesamt 20 unabhängige
ImageGen-Generierungen und drei zugeordnete Transparenzkorrekturen per ImageGen.
Acht Vorgänger sind verworfen/ersetzt: die ersten beiden Fehlversuche, drei
vom Eigentümer abgelehnte Kuala-Lumpur-Fassungen und drei neue Stadtbilder mit
unerwünschten weißen Flächen vor der Transparenzkorrektur.
Herkunft, Originalhashes, Prompts, Elternbilder der Korrekturen und die
15 ausgelieferten PNG-Ableitungen stehen in der [Provenienz](../game/art/drawing/rz_eval/provenance.json).
Originale und zusätzliche Vergleichsprofile werden separat für R01/M01 zugestellt.
Keine Zählung von Format-/Größenvarianten als kreative Kandidaten.

## Gemeinsame Leinwand und Darstellungsweg

Logische Referenz 3072×768, Seitenverhältnis 4:1. Alle Bilder werden proportional
eingepasst, horizontal mittig und unten ausgerichtet. Keine Beschneidung,
Streckung, individuellen Offsets oder Layoutfelder. Transparenter Restplatz bleibt
Bestandteil der Leinwand. Die gelieferten ImageGen-Originale haben 2172×724;
die große Ableitung enthält folglich keine zusätzlich erzeugten Details.

`RzEval.placement` verwendet die tatsächliche ruhende rechte Papierprojektion,
ihre Schnittfläche mit dem Viewport, 7,5 % Falzreserve sowie 24×UI Rand. Die
gemeinsame 4:1-Fläche wird unten mittig in diesen sicheren Bereich eingepasst.
Das ist ein Hintergrundbereich; er verändert keine funktionalen Budgets.
Rasterzoom und Überlappung gehen nicht in diese Platzberechnung ein.

`book/rz_eval.gd` liegt passiv in derselben Seiten-/Capturehierarchie unter der UI.
Nur die fünf IDs nutzen diesen Weg. Andere Rätsel und Hilfe behalten RAND-P1;
die fünf Proben haben auch bei fehlendem Bild keinen Kategorie-Fallback.
`--rz-without` zeigt für sie die unveränderte Funktion ohne neue/alte Zeichnung.
`--rz-transparent` ist ein ausdrücklich leerer Zustand ohne geladene Textur.
Fehlend, defekt, leer, wartend, bereit und zu spät sind getrennte Zustände.

Die Anfrage beginnt unmittelbar nach angenommener ID-Aktivierung, vor der
Quellseitenaufnahme, und nutzt deren vorhandene Vorbereitungsframes ohne Warteblock.
Bis zur Zielanordnung ist ihr Zeichenrechteck leer: kein Durchscheinen im Katalog.
Pro Besuch höchstens eine aktive Textur und eine laufende Anfrage. Es gibt keine
Vorladung der fünf/15 Bilder und keinen Verlaufscache. ResourceLoader-Anfragen
lassen sich nicht abbrechen; eine veraltete Anfrage wird abgeschlossen und
verworfen, bevor die einzige zuletzt gewünschte Anfrage startet. Besuchsgeneration
und ID verhindern alte Bilder nach Wechsel/Abbruch. Laden verwendet
`CACHE_MODE_IGNORE`. Zoom verändert nur Geometrie, nie die aktive Ressource.
Nach Verlassen wird die Referenz freigegeben; temporäre Seitensnapshots bleiben
an den bestehenden Buchlebenszyklus gebunden. Ein Ergebnis nach der Vorbereitung
wird für diesen Besuch ausgelassen, damit Dekoration nicht sichtbar nachspringt.
Das Spiel wartet nicht auf sie; ein späterer Besuch versucht erneut zu laden.

## Vergleichsvarianten

Gleiche 48-%-Grunddeckkraft, Illustration, Belegung und funktionale Geometrie:

| Schalter | Wirkung innerhalb des tatsächlichen Rasters samt Rahmen |
| --- | --- |
| `--rz-mode=A` | Illustration unverändert sichtbar |
| `--rz-mode=B1` | Nur lokale Alpha-Abschwächung auf 20 % der Grunddeckkraft |
| `--rz-mode=B2` | Nur lokale 9-Sample-Unschärfe mit 2,5 Anzeige-Pixeln Radius |
| `--rz-mode=C` | Deckender ruhiger Papierfarb-Untergrund für das gesamte Raster, einschließlich unbekannter/X-Zellen und Zwischenräume |

Dieselbe A/B1/B2/C-Regel gilt getrennt für die tatsächlichen Zeilen- und
Spaltenhinweisrechtecke. In A bleiben sie durchlässig, B1/B2 behandeln nur die
darunterliegende Illustration und C hinterlegt auch die Hinweise deckend.
Die funktionalen Zeichen werden danach scharf gezeichnet. B2 mittelt
vormultiplizierte Farbe/Alpha ausschließlich aus der Illustration, ohne Screen-
Textur, zusätzliche Kopie oder Renderziel. Alle Varianten schützen separat
sichtbare Kopf-, Sidebar-, Werkzeug- und Meldungsrechtecke. Ihre lokale
Schutzregel läuft über acht Anzeige-Pixel weich aus. Die gemeinsame äußere
3:1-Quellbildkante innerhalb der 4:1-Leinwand läuft über 3,5 % weich aus;
keine individuelle Motivmaske oder Beschneidung. Vollständig innerhalb der
Zeichenfläche komponierte Motive bleiben das Produktionsziel.
Außerhalb der Rechtecke bleiben die Striche unverändert; keine Schwelle blendet
Leinwand oder unbeteiligte Teile aus. C kann überdeckte Teile vollständig verdecken.
Das ist ein Vergleich, noch keine ausgewählte Produktregel.

## Profile, Prüfung und offene Entscheidung

Der Versuchsspieler liefert drei Kandidaten je ID als PNG mit 2304×576 und
verlustfreiem Godot-Import. Zusätzliche 1536×384-/3072×768-PNG-/WebP-Vergleiche
werden ausschließlich im temporären Vergleichsprojekt vermessen. Die Entwickler-
Schalter `--rz-profile`/`--rz-format` setzen diese separat zugestellten Dateien
voraus; sie sind keine Spielereinstellung und lösen keinen Netzwerkdownload aus.
Die 15 lokalen Kandidaten sind aktuelle Versuchsressourcen, keine technische Galerie.
Ohne Kandidatenschalter gilt die konkrete Eigentümerwahl für die vier gewählten
Rätsel; Kuala Lumpur verwendet Kandidat 1 nur als noch ungeprüfte Referenz.
Zusätzliche Profil-/Messbilder und Buchoriginale gehören nicht in den Spielerdownload.

Prüfbedarf: [.ci/package.json](../.ci/package.json), `docs` und `ci-required`,
Windows-x64-Spieler und ausschließlich `native.catalog`. Die kleinen synthetischen
RZ-Fälle laufen im bestehenden Informationsprozess. Sie prüfen Canvasstabilität,
passive Eingaben, unveränderte Geometrie/Savebytes, leer/fehlend/defekt,
echte verzögerte Ressourcenanfragen und veraltete Besuchsergebnisse. Keine echten
Katalogrätsel als Dauerfälle und kein Solver-/Proof-Replay. Nach R01/M01/D01
mit dem Versuch über Erhalt oder Rückbau dieser kleinen Fälle entscheiden.

Einmalige aktuelle Buchoriginale, reale Zoomfolge und Eingaben, PNG/WebP- und
Import-/Windows-/Web-Bytevergleich sowie Ressourcenmessungen werden im Draft-PR
mit Produkt-/Belegcommit, Größe, SHA-256, Empfänger und Ablauf verlinkt. Sie ersetzen
kein unabhängiges R01 und keine persönliche Bildwahl M01. Messlücken und nicht
ausgeführte Prüfungen bleiben ausdrücklich offen. Bedarfsladen im gemeinsamen
Web-Paket ist kein bedarfsgesteuerter Netzwerkdownload. Kein Chromium, Hosting,
Streamingdienst oder automatischer Rückbau/Übernahme nach main.

Die Ergebnisbilanz E1–E7 und die Empfehlung stehen am tatsächlich geprüften PR-Head.
Aktive Arbeitszeit ist ohne zuverlässige Zeiterfassung unbekannt; tatsächliche
Generierungs-/Laufzeiten und Wartezeit werden davon getrennt ausgewiesen.
Offene Fragen für #489/#490/#491 betreffen spätere Herkunfts-/Freigabebindungen,
Kandidatenauswahl und deterministische Ableitungen. Diese Issues werden weder
geändert noch zur Voraussetzung des Versuchs. Übernahme oder vollständiger
Rückbau benötigt den separaten Folgeauftrag aus D01.
