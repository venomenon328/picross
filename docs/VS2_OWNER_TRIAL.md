# Reguläre Windows-Spielprobe · VS2-M01

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
Die Farbe kann einen Füllstrich schützen oder bewusst ein begonnenes X umwandeln.
Rückziehen verkürzt die Vorschau; Undo/Redo arbeitet mit vollständigen Strichen.
Die eigene Miniatur ist passiv. Raster und Miniatur lassen sich nicht verschieben.
Eine überlaufende Hinweiszeile lässt sich mit der mittleren Taste waagerecht,
eine Hinweisspalte senkrecht ziehen. Darüberfahren zeigt die gesamte Folge.
Esc oder Fokusverlust bricht ab. Optionen enthalten Hilfe und Zellanimationen.

Bitte an genau dem im PR gebundenen Download prüfen:

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

Protokoll: PR/Head, Download/ZIP-Hash, EXE, Windows-Version, Monitorauflösung,
tatsächliche normale/maximierte Clientfläche, Windows-Anzeigeskalierung, gewählte
UI-Skalierung, Maus und Ergebnis je Schritt festhalten. Unbekannte Werte offenlassen.
Technische Eingabeproben ersetzen kein persönliches Komforturteil.

**VS2-M01 ist offen.** Unabhängiges technisches/visuelles Review und passende
Mergefreigabe bleiben vor Merge erforderlich. Dieses Paket ist kein Release.
