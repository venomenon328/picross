# BP-3 · Entscheidungsunterlage

**Empfehlung des Bearbeiters, keine Eigentümerwahl:** Kandidat B mit dieser
gemeinsamen UI-Ausarbeitung, Fraunces/IBM Plex Sans und C1 als Ausgangspunkt
für die spätere ausdrückliche Gestaltungsentscheidung verwenden. A bleibt eine
vollständig vergleichbare Alternative. Beide sind in allen fünf Fällen geliefert.

## Sichtbarer Vergleich

| Aspekt | A · dunkler Inventarband | B · heller Sammlungskatalog |
| --- | --- | --- |
| Einband / Material | Kräftiger Leder-/Holzrahmen, deutliche Buchfassung; stärkerer warmer Außenkontrast. | Helleres Gewebe und weicheres Licht; die kleinen Messingfassungen treten ruhiger zum Buch. |
| Arbeitsfläche | Warmes Papier, lesbare dunkle UI; der dunkle Rand setzt einen deutlichen Abschluss. | Ebenfalls warm und ruhig, weniger Kontrast zum Außenrand; lange Sitzungen wirken visuell leichter. |
| Neue UI | Dunkles aktives Werkzeug verbindet sich mit dem kräftigen Einband; Messing tritt deutlicher hervor. | Gleiche Geometrie, Farbe und Schrift; Werkzeuggruppen wirken als zurückhaltende Ergänzung der Sammlungskarte. |
| Grenze | Lokale untere A-Retusche wirkt weicher. | Auch B bleibt aus einer kleineren nativen Quelle hochskaliert. |

Beide Hintergründe stammen nativ aus 1672×941. Die proportional vorbereiteten
2560×1440-Dateien liefern keinen zusätzlichen nativen Detailgrad. Feine Nähte und
Seitenlagen bleiben insbesondere am schmalen Rand begrenzt. BP-3 retuschiert diese
Eigenschaften nicht; sie sind in der Entscheidung zu berücksichtigen.

## Ausgearbeitete gemeinsame UI

Die Inventarkarte erhält zwei kleine Metallhalter, einen ruhigen Papierkörper,
eine präzise Bildfassung und eine zurückhaltende untere Schattenkante. Ihre
Miniaturfläche bleibt exakt gleich groß und zeigt denselben eigenen Zellstand.
Die Palette sitzt als zusammengehöriger Mustersatz in einer flachen Fassung.
Werkzeuge bilden drei funktionale Wannen mit abgeschrägten Kanten und schmalen
Licht-/Schattenlinien. Blattzugänge verwenden dieselbe Material-/Iconsprache.
Diese kleinen Gehäuse sind opak; unter Raster und Hinweisen bleibt das echte Buchpapier sichtbar.

Aktive Werkzeuge tragen einen hellen Unterstrich, dunkle Füllung und den expliziten
Status. Aktive Farbmuster tragen kontrastierende Eckmarken außerhalb ihrer
Original-RGB-Fläche sowie den Farbstatus. Hover hellt nur das Gehäuse auf; Druck
vertieft die Fläche und verschiebt das Icon um 1 UI-Pixel. Deaktivierte Aktionen
erhalten ein zurückgenommenes Icon und eine kleine Sperrmarkierung. Nicht sinnvolle
Zustände sind auf der Tafel ausgelassen, insbesondere dauerhafte Undo-/Redo-Auswahl.

Fraunces 28 px / 600 setzt nur den kurzen funktionalen Titel. IBM Plex Sans trägt
UI, Status und Zahlen: 12–14 px bei UI 100 %, entsprechend skaliert bei 125 %.
Hinweisgrößen und gemeinsame Slots bleiben exakt bei BP-1R. Die Typografie ist
an den tatsächlichen Dateien und im Browser gemessen, keine neue Fontauswahlrunde.

**C1 empfohlen:** Die bereits vorhandene 0,55-px-Kontur hilft insbesondere den
gelben Hinweisziffern auf warmem Papier. Sie verändert weder Farb-ID noch
Zahlenfüllung, Schriftgröße oder H1-Zuordnung. Kleine farbige Hinweise bleiben
anspruchsvoller als normaler UI-Text; C1 ist keine pauschale Barrierefreiheitslösung.
Die konkrete Eigentümerentscheidung zur Kontrasthilfe bleibt vor #23 notwendig.

## Offene Entscheidungen und nativer Anschluss

Vor späterem Merge: unabhängiges technisches/visuelles Review und ausdrückliche
Eigentümerfreigabe. Vor #23 zusätzlich Artwork A/B, UI-Ausführung, Layout-,
Schrift-, Icon- und Kontraststand konkret auswählen und den nativen
Navigationsumfang bestätigen. Die neue Vergleichsunterlage trifft diese Wahl nicht.

Die Anschlusstafel hält `nav-album → album`, `nav-information → information`
und `nav-work → work` getrennt. Sie konkretisiert den Symbol-/Textanschluss an
bestehende Einstellungen und Hilfe, baut aber weder Album noch Statistik.
Reale Zustandsverfügbarkeit, Tooltippositionierung bei Mausbewegung, modale
Recoverybestätigung und blockierte Pflicht-Flush-Übergänge müssen später in der
aktuellen nativen Grundlage angeschlossen und geprüft werden. Die statische
720p-Tafel beweist die gezeigten Größen, keine Laufzeitplatzierung jeder Meldung.

Zellen, History, Ansichts-/Hinweislesepositionen, Gestenabbruch und Recoverygrenzen
bleiben unverändert. Die bestehende gesonderte PR-#25-Nacharbeit gehört nicht zu
BP-3. Keine Live-Fehlerhilfe, neue Wertung, Timer, Notizwerkzeuge oder Motivspoiler.
Keine reale Maus-/DPI- oder Langzeitprobe ausgeführt. #24 folgt erst später;
#27 und #21 bleiben offen.
