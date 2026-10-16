# Carabao – Kopf · C-r02 · r10

**Gewünschte zwei Änderungen umgesetzt; Mehrdeutigkeit belegt.**
[Vorher/nachher](vergleich.png),[C-r02](kandidat-C-r02.png),[Paket](package.zip),
[Datei-/Produktionsprüfung](validation.json). ID `pz-b5e2302bf71445c09caac76bbc2a7075`, Kategorie Säugetiere.

Z3/S36 ink→EMPTY, Z5/S8 EMPTY→ink. Alle anderen1038 Zellen identisch zu r09C.
40×26,1040 Zellen,448 gefüllt/592 leer;gewünscht/verwendet genau1 Vordergrundfarbe
ink#000000+EMPTY. Schnauze und Unterlippe weiterhin getrennt vollständig geschlossen,
33 bzw.3 Leerzellen. B-r02 und MA-r03 bytegleich zu tatsächlichen Bildfreigaben.

**Geprüft:** originaler Motivimport, bisherigesC, neue feste Änderungsliste,
neuer Rasterquellimport und Hinweise frisch rekonstruiert. Maße/Palette/Randregel
gültig (links/oben/unten belegt,rechts leer). Linien- und Paarproof unabhängig
bestätigt, beide **stalled**,248 Schritte,10 offene Hornzellen. Kein vollständiger
Endproof oder Endmatrixbeweis, keine Zertifizierung behauptet.

**Logik FAIL:** zwei verschiedene vollständige Lösungen erfüllen identische Hinweise;
unabhängiger Checker bestätigt beide Zeugen und `multiple`. Ihre Unterschiede
liegen bei Z1/S36,Z1/S38,Z3/S36,Z3/S38. Originale Diagnose und beide Zeugen im ZIP.
Paarbudget20M Arbeit/250k Einträge vorab gebunden; Solver2.521.905 Arbeit,
Prüfer17.555.462,Peak1199. Kein Ressourcenabbruch und keine Erfolgumdeutung.

Keine zusätzlichen Zelledits/Suchreparatur: fester Zwei-Zellauftrag schützt alle
übrigen Positionen; weiterer freier Änderungsraum fehlt. Eine andere/zusätzliche
konkrete Folgekorrektur ist für ein eindeutiges Spielrätsel erforderlich.
Vorheriges zertifiziertesC bleibt unverändert in r09 erhalten.

Fünf Gestaltungskriterien bestanden; gleiche Schnauze, Augen, Ohren und restliche
Form, ausschließlich die beiden benannten Hornkanten geändert. Kleine Pupillen/
Lippen/Hornkurven weiterhin grob; obere rechte Spitze diagonal angeschlossen.
Schwarz trägt Kopf/Konturen,Weiß Hintergrund/Binnenräume. Keine neue Farbe/Pose/Bilddatei.
**Keine Schwierigkeit vergeben:** nicht freigabefähig; alte L2-Schätzung nicht übernommen.
Umfang1040 Zellen,Zeit nicht geschätzt,Probespiel optional/nicht durchgeführt.
Hier0 Bildaufrufe,1 Linienimport,1 Paarimport,1 Diagnose,0 Suchreparaturen;
aktive Menschenzeit nicht erfasst. Nutzungsgrundlage nativ beauftragte KI-Bilder
ohne Fremdassets,keine Exklusivität. Vollständige benötigte Vorfahren/Bündel im ZIP.

Kein ZA-1-inspect/-export,keine Spielregistrierung: belegte Logikblockade und fehlende
Endfreigabe; keine Autorisierung erfunden. Sicheren ZIP-Container/CRC/Inventar/
Dateimenge/Handoffkopie geprüft; keine Zieladapterzertifizierung daraus abgeleitet.
Native Spiel-/Buildtests für reine Ablage nicht erforderlich.

Regelwerk0.5.0/Rev14; Tool-/Quellcommit `19fa32e3b4e80cec35c89773f2b019d8d0ae7e0a`.
Inventar-SHA-256: `23ac3d0ad50c02d5f5200dc80c9b3342278ad7702a60cff9d1a16b45dcd59edb`.
ZIP-SHA-256: `e2ddc3c7be474ecd5c40b407a9b9fd9a85164feba51d6ef1997646d520f34266`.
Handoff-SHA-256: `cd9f26b70b782ebb63445fc8fcfa3a65dc0bc2730ea56eb4bb78e8f1f5b83477`.

**Nächster Schritt: Korrigieren oder Fehler beheben.**
Eine neue konkrete Rasterkorrektur muss die Mehrdeutigkeit beseitigen;
Endabnahme allein kann dieses technische Gate nicht aufheben.
