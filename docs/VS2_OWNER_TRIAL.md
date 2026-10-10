# Reguläre Windows-Spielprobe · SL-M01

## Status und Bindung

**SL-M01 offen.** Diese persönliche Sicht-/Bedienprobe gilt für den neuen kombinierten Head zu [#65](https://github.com/venomenon328/picross/issues/65). PR #62 ist abgeschlossen. Alte Abnahmen und technische Implementiererproben ersetzen diese neue persönliche Prüfung nicht. Keine vollständige Rätsellösung erforderlich.

## Regulärer Start und Bedienung

Das Paket enthält `picross-p1.exe` und die Konsolenfassung. ZIP vollständig in einen
neuen Ordner entpacken und eine der beiden Dateien ohne Zusatzargumente starten.
Godot muss nicht installiert werden. Die Anwendung startet in der Sammlung;
erst die bewusste Auswahl öffnet ein Blatt. Normale lokale Spielstände bleiben
unter derselben Appidentität erhalten. Vor einer persönlichen Probe vorhandene
Spielstände bei Bedarf selbst sichern; keine unbekannten Launcher verwenden.

Unter **Einstellungen → Rätselansicht** stehen **Rasteransicht** und
**Gesamtansicht mit allen Hinweisen**. Die Wahl gilt für diese Sitzung und bleibt
bei Blattwechsel und Reset erhalten. Ein neuer Start beginnt in Rasteransicht.
Minus/Plus und Mausrad wählen die Zoomstufe. Fenster, Hinweise und UI begrenzen die tatsächliche Größe; das Raster bleibt vollständig sichtbar.

Links setzt Farbe, rechts X; erneutes Setzen nimmt den jeweiligen Typ zurück.
Eine auf unbekannt begonnene Geste schützt Vorbelegungen; bewusstes Umwandeln
beginnt auf X mit links beziehungsweise auf einer Füllung mit rechts.
Rückziehen verkürzt die Vorschau; Undo/Redo arbeitet mit vollständigen Strichen.
Die eigene Miniatur ist passiv. Raster und Miniatur lassen sich nicht verschieben.
Eine überlaufende Hinweiszeile lässt sich mit der mittleren Taste waagerecht,
eine Hinweisspalte senkrecht ziehen. Darüberfahren zeigt die gesamte Folge.
Esc, Fokusverlust oder Gegentasten-Down bricht die laufende Zellgeste ab;
nach Gegentastenabbruch beide Tasten loslassen und neu beginnen.
Optionen enthalten Hilfe und Zellanimationen.

Rechts unter Miniatur und Farben stehen genau sechs Aktionen in zwei Spalten und drei Zeilen: Füllen/Radieren, Undo/Redo, Verkleinern/Vergrößern. Alle sechs bleiben ohne Scrollen sichtbar, auch bei 720p/UI125. Drei gezeichnete transparente Rahmen liegen auf einer gemeinsamen Mittelachse. Die Miniatur hat keine Überschrift. Über dem Raster bleibt das Rad Zoom; über den Werkzeugen verändert es keine Zellen oder Rastergröße. Auswahlmarkierungen und Tooltips ersetzen die dauerhafte Werkzeug-/
Farbtextzeile; eine numerische Zoomanzeige gibt es nicht mehr. Nötige Platz- und
Hinweiswarnungen bleiben unten sichtbar.

## Probe am kombinierten SL-A/B-Lieferstand

Bitte an genau dem im PR gebundenen neuen Download prüfen; nur tatsächlich
beurteilte Szenarien als durchgeführt eintragen:

1. Frischer, angefangener und gelöster Stand starten jeweils in der Sammlung.
   Optionen dort öffnen kein Rätsel; Auswahl und Rückweg funktionieren.
2. Beide benannten Ansichten wählen, Blätter wechseln und Minus/Plus sowie Mausrad verwenden.
   Raster-/Miniaturziehen bleibt wirkungslos; lange Hinweise bleiben zugänglich.
3. Gewöhnlich füllen, X setzen, zurückziehen, Undo/Redo und schnellen Folgezug prüfen.
   Zwischen Optionen und Arbeit wechseln; keine alte Animation kehrt zurück.
4. Fenster normal/maximiert, UI 100/125 %, Zoom und Fortsetzung nach Beenden prüfen.
   Große bestehende Blätter können kleine oder kollidierende Hinweise zeigen;
   eine Platzmeldung ist kein Komfortversprechen und bietet keinen Pan-Ausweg.
5. Speichern/Beenden/Neustart: wieder Sammlung, eigener Stand und Redo erhalten.
   Reset betrifft nur das ausdrücklich bestätigte Blatt.
6. **Kompakte Hinweise und Platzierung:** Die Zahlen einer Zeilenfolge stehen sichtbar
   enger, sind aber nicht kleiner oder angeschnitten. Bei freier Breite sitzt der
   ganze Raster-/Hinweisblock ausgewogener statt am linken Rand. Mit langen Folgen
   bleiben sämtliche Hinweise erreichbar; Zahlen dürfen beim Ziehen/Einrasten
   nicht springen oder sich überdecken. Beide Ansichten und UI100/125 ansehen.
7. **Scribble-Optik und Buchrand:** Rasterlinien, kleine Vorschau samt Fassung und
   Farbauswahl wirken leicht handgezeichnet, nicht unruhig. Fünferlinien, benachbarte
   dunkle Füllungen und kleine Zellen bleiben klar. Miniatur, Palette und Werkzeuge stehen auf einer gemeinsamen Mittelachse und berühren den Buchrand nicht; keine Überdeckung von
   Hinweisen, Werkzeugen, Beschriftungen oder einer sichtbaren Speichermeldung.
   Zell- und Farbwahl müssen weiterhin präzise treffen.
8. **Nur Füllungen in der Miniatur:** X sind weiterhin im großen Raster vorhanden,
   erscheinen aber weder als X noch als Punkte im kleinen Bild. Eigene Füllungen
   einschließlich falsch gesetzter Farben bleiben sichtbar. Füllung in X umwandeln,
   Vorschau zurückziehen/abbrechen und Undo/Redo prüfen: Das kleine Bild folgt sofort
   den eigenen vorgesehenen beziehungsweise bestätigten Füllungen, ohne Animation
   oder Lösungskorrektur. Vorhandene ungelöste Albumminiaturen zeigen dasselbe Prinzip.

9. **V3-Striche und Textur:** Rasterlinien sind gegenüber V2 etwas deutlicher
   handgezeichnet. Benachbarte satte Füllungen zeigen unterschiedliche ruhige
   Stiftzüge; Vorschau, Animationsende, Zoomrückkehr und Neustart würfeln sie
   nicht neu. Kleine Zellen, X, Rahmen und Fünfergrenzen bleiben gut unterscheidbar.
10. **V3-Leiste und Titel:** Im kleinen Fenster mit UI125 alle sechs Werkzeuge
    in 2×3 ohne Scrollen erreichen und bedienen; keine ungewollte Rasterbewegung oder
    Zellaktion. Im großzügigen Fenster bleibt die Leiste ruhig. Hilfe/Menü/Info
    sitzen etwas links/unten und sind frei erreichbar. Bakso erscheint nur im
    Arbeits-Blatttitel; `·`, `×` und Ziffern sind vollständig, andere Seiten
    behalten ihre bisherige Überschriftenschrift.

Protokoll: PR/Head, Download/ZIP-Hash, EXE, Windows-Version, Monitorauflösung,
tatsächliche normale/maximierte Clientfläche, Windows-Anzeigeskalierung, gewählte
UI-Skalierung, Maus und Ergebnis je Schritt festhalten. Unbekannte Werte offenlassen.
Technische Eingabeproben ersetzen kein persönliches Komforturteil.

**SL-M01 bleibt vor Merge offen.** Der neue kombinierte Stand benötigt zusätzlich
unabhängiges technisches/visuelles Review und passende Mergefreigabe. Frühere
R1-/ZS2-/GF1-Nachweise nehmen weder die neue Gestaltung noch ihre persönliche
Abnahme vorweg. Dieses Paket ist kein Release; seine Umsetzung ist keine
Mergefreigabe.
