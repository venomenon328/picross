# Reguläre Windows-Spielprobe · VS2-M01

## Status und Bindung

**Rückmeldung mit Änderungsbedarf; keine vollständige positive Abnahme.** Nach
Review R1 zur Erstlieferung `2c332ad688315bfa851f7c0d8642d2ab4ac3709c` hat der
Eigentümer fünf visuelle Nacharbeiten benannt und als Spezifikation freigegeben.
[VS2-V1 / N01/N02/N04](VS2_V1_IMPLEMENTATION.md) ist umgesetzt, V2/N03/N05 bleibt offen. Die folgenden
zusätzlichen Sichtprüfungen gelten erst für deren späteren, im PR gebundenen neuen
Download; die alten EXEs können die neue Spezifikation nicht bereits erfüllen.
Keine vollständige Lösung, konkrete Prüfzeit oder unbekannte Windows-/DPI-Werte
werden aus dem bisherigen Sichtfeedback abgeleitet.

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
**Einpassen** passt innerhalb der gewählten Ansicht ein. **Arbeitsgröße** wünscht
24 Pixel; Fenster, Hinweise und UI begrenzen die tatsächliche Größe.

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

## Probe am späteren kombinierten E1-Lieferstand

Bitte an genau dem im PR gebundenen neuen Download prüfen; nur tatsächlich
beurteilte Szenarien als durchgeführt eintragen:

1. Frischer, angefangener und gelöster Stand starten jeweils in der Sammlung.
   Optionen dort öffnen kein Rätsel; Auswahl und Rückweg funktionieren.
2. Beide benannten Ansichten wählen, Blätter wechseln und Einpassen verwenden.
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
   dunkle Füllungen und kleine Zellen bleiben klar. Miniatur/Palette stehen etwas
   weiter unten/links und berühren den Buchrand nicht; keine Überdeckung von
   Hinweisen, Werkzeugen, Beschriftungen oder einer sichtbaren Speichermeldung.
   Zell- und Farbwahl müssen weiterhin präzise treffen.
8. **Nur Füllungen in der Miniatur:** X sind weiterhin im großen Raster vorhanden,
   erscheinen aber weder als X noch als Punkte im kleinen Bild. Eigene Füllungen
   einschließlich falsch gesetzter Farben bleiben sichtbar. Füllung in X umwandeln,
   Vorschau zurückziehen/abbrechen und Undo/Redo prüfen: Das kleine Bild folgt sofort
   den eigenen vorgesehenen beziehungsweise bestätigten Füllungen, ohne Animation
   oder Lösungskorrektur. Vorhandene ungelöste Albumminiaturen zeigen dasselbe Prinzip.

Protokoll: PR/Head, Download/ZIP-Hash, EXE, Windows-Version, Monitorauflösung,
tatsächliche normale/maximierte Clientfläche, Windows-Anzeigeskalierung, gewählte
UI-Skalierung, Maus und Ergebnis je Schritt festhalten. Unbekannte Werte offenlassen.
Technische Eingabeproben ersetzen kein persönliches Komforturteil.

**VS2-M01 bleibt vor Merge offen.** Der neue kombinierte Stand benötigt zusätzlich
unabhängiges technisches/visuelles Review und passende Mergefreigabe. Frühere
R1-/ZS2-/GF1-Nachweise nehmen weder die neue Gestaltung noch ihre persönliche
Abnahme vorweg. Dieses Paket ist kein Release; die Spezifikation ist kein
Implementierungsauftrag.
