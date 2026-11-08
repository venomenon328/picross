# KL-CARD-A: befristete Revieworiginale

Produkt: `a050c6dbe862535bd7e940691b42e8cbfe2cd2c7`. Vorher: `d974886d18ce294c11c2b2467166bae24894e7cb`. Empfänger: unabhängiger R01-Reviewer
und Eigentümer M01. Zweckbindung bis 15.11.2026; danach bei offenem Gate den Bedarf
erneut prüfen. Rückbau des eigenen Remote-Belegrefs im Paketabschlussauftrag.
Kein Merge dieses Branches in Produktbranch oder main.

Alle PNGs sind unveränderte native Godot-Ausgaben. `manifest.json` bindet pro Datei
Szene, Render-/UI-Größe, Seite, Filter/Sortierung, beide Scrollstände, Produktcommit,
Dateipfad, Bytes und SHA-256. Der im PR genannte unveränderliche Belegcommit bindet
dieses Manifest und alle Originale. Binär über den Raw-Link an genau diesem Commit
oder per Git laden, Bytes/Hash prüfen und öffnen; eine GitHub-Vorschauseite genügt nicht.

Aufnahme-Head nachher: `e7121da67f910fda03a6418ee81ad07ba0508445`. Der native Originalbericht behält
diese tatsächliche Herkunft. `application-sources.json` prüft alle verwendeten
Anwendungsskripte/-szenen gegen den oben genannten Produkt-Head. Eine spätere
reine Harness-/Dokumentänderung erlaubt nur bei vollständiger Quellbytegleichheit
diese Wiederverwendung; bei Anwendungsabweichung bricht die Zustellung ab.

Windows 11, Godot 4.7.2-stable, OpenGL 3.3, NVIDIA RTX 3070. Das unveränderte echte
3D-Buch rendert in einem nativen SubViewport mit den angegebenen Clientmaßen. Kein
beschleunigtes BookFixture und kein flaches Kachelmock. Der Host bleibt verborgen;
Viewportereignisse sind synthetisch. Dies ist keine physische Desktop-/Maus-/DPI-
oder persönliche Eigentümerabnahme. Echte Saves werden nicht verwendet.

## K2: vollständig sichtbare Karten

Identischer synthetischer 54er-Katalog, Kategorie Gebäude & Bauwerke (48 Treffer),
Sortierung Größe aufsteigend, erste Doppelseite mit 12/12 Karten, UI100, Scroll 0/0.

| Clientfläche | Spalten je Hälfte | Volle Reihen je Hälfte vorher → nachher | Volle Karten gesamt |
| --- | --- | --- | --- |
| 1920×1080 | 2 | 2 → 3 | 8 → 12 |
| 2560×1440 | 3 | 2 → 4 | 12 → 24 |

Vorher 284×343 px, nachher 301×223 px; gleichbleibend 10 px Innenrand,
8 px Inhaltsabstände und 12 px Reihengap. Clip 709 px bei 1080p bzw. 1042 px
bei 1440p. Vorher brauchen drei volle Reihen 3×343+2×12=1053 px und überschreiten
den 1440p-Clip um 11 px; deshalb ist die im Entwurf angenommene 18er-Ausgangszahl
an dieser aktuellen NAV-A/Pangolin-Basis nicht erreicht. Der untere Rahmen der
dritten Reihe ist im Original abgeschnitten. Nachher: drei Reihen 693 px bei
1080p, vier Reihen 928 px bei 1440p. Scrollbereiche je Hälfte vorher/nachher:
1409/689 px bei 1080p und 366/0 px bei 1440p. Das Nachher-Ziel ist jeweils erreicht.
Die Zählung wurde an den nativen Rechtecken UND Originalbildern kontrolliert.

## K3 und Fehlerwege

`long-wide` zeigt UI125, eine vollständige lange Zweizeilenkategorie,
Nicht eingestuft, separaten 55-px-Reset und ein synthetisches verdientes 10:1-Reveal
mit verschiedenfarbigen Enden. Reset wurde geklickt und abgebrochen. `narrow-long`
und `narrow-metadata` zeigen 1280×720/UI125 mit gemeinsamem Stapelfallback sowie
dem über natives Scrollen vollständig erreichten Streifen. Bei 429 px Kartenhöhe
und 270/267 px Clip ist eine ganze Karte hier bewusst nicht gleichzeitig sichtbar.
Die vollständigen Schrift-/Bild-/Hitbudgets bleiben; keine horizontale Überbreite.
`fit-*` bindet das aus beiden tatsächlichen Papierbreiten interpolierte Grenzpaar
bei UI125: zwei Spalten, gemeinsamer Stapel-/Seitenwechsel. Die genauen Werte
stehen im Manifest. UI100→125→100 erhält 70/140 px Scroll, Auswahl-ID und Slotbytes.

`invalid` kommt aus einem tatsächlich ungültigen synthetischen Primary; Öffnen
bleibt gesperrt, kein Fragezeichen/Reveal. Reset wurde per Pointer bestätigt.
`recovery-2` lädt einen gültigen begonnenen Backup-only-Stand; `recovery-4` einen
gültigen Primary mit beschädigtem Backup. Beide separaten Reparaturbuttons wurden
im inneren Clip erreicht, geklickt und bestätigt. Jeder Fremdslot bleibt bytegleich.
Die Assertions und Rendermaße stehen in `after/measurements.json`; die zwei
temporären Capture-Skripte und der geprüfte Anwendungssourcenabgleich sind beigefügt.

Keine Dauerbilder, Filme, echten Inhalts-/Savekopien oder allgemeiner Technikbaum.
Unabhängiges R01 und persönliche M01 bleiben vor Merge offen.
