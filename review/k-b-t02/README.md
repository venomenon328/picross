# K-B-T02: befristete technische Originale

PR #538; Produkt-Head `56f7768acfae8e07316df327e521ac3ee6b56f12`; Basis `c64cae2a464ccd8d27e986620592f6ef8667efea`.
Implementiererprobe, kein unabhängiges R01 und keine persönliche M01-Abnahme.
Paketentscheidung: https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391
UI-Präzisierung: https://github.com/venomenon328/picross/issues/485#issuecomment-6706227988

Windows, Godot 4.7.2.stable.official.ed1daf0bf, NVIDIA RTX 3070, OpenGL Compatibility.
Echte exportierte EXE/PCK, regulärer Buchroot und unveränderte Produktcodebytes;
keine beschleunigte BookFixture. Produkt-/Buildhashes in build-manifest.json.
Ausschließlich 54 synthetische KAT2-Fixtures und isoliertes APPDATA. Blatt 02 hat
zwei Lösungszellen, damit Abschluss über echte Mausklicks geprüft werden kann.
Die Definition und Registry sind beigefügt. Keine echten Nutzersaves oder Produktionsrätsel.

Der externe Observer liest nur und zeichnet Root-Viewport-PNGs/Zustände auf.
Die Treiber senden echte Win32-Mausereignisse ausschließlich an das eigene Fenster;
Popups werden angeklickt. Die erfolgreiche kleine Auflösung wurde über die echten
Anzeigeeinstellungen samt Bestätigung gewählt; ein vorbereitender direkter
OS-Resizeversuch wurde vom Produkt zurückgenommen und zählt nicht als Prüfung.
Offscreen-/verdeckte Klickversuche wurden vor Eingabe abgebrochen. Frühere
Entwicklungsprozesse 40340/4728 sind nicht Teil dieses Liefernachweises.

19 dokumentierte Szenarien auf finalem Produktcode, Prozesse 29488, 39868, 43140,
41740. observations.json enthält die tatsächlich gelesenen vollständigen Zustände,
checks.json deren erfolgreiche Prüfzuordnung. 29488: zwei bearbeitete IDs über
Undo/Redo und neue Zellaktion; ausgefilterter Direktaufruf/Rückkehr erhält Filter
und beide Scrollpositionen 273/455; tatsächlicher Temp-Verzeichnisfehler erhält
alte Merkerbytes, eigene Wiederholung gelingt; bestätigter Reset und tatsächlicher
Zwei-Zellen-Abschluss entfernen das Angebot. 39868: echter neuer Prozess startet
nach Abschluss ohne Angebot; erneute Bearbeitung erzeugt Merker, Größen/UI100/125.
43140: weiterer echter Neustart lädt diesen begonnenen Merker, Start bleibt Katalog.
41740: eigenes kopiertes Fehlerprofil mit beschädigtem Primary und validem begonnenen
Backup öffnet über den Merker, behält recovered und den bewussten Übernahmedialog;
Abbrechen repariert nichts. Alle Prozesse regulär beendet, keine Skriptfehler.

Bildbelege sind unverkleinerte Originalpixel, bei sechs Bildern nur der nötige
Ausschnitt. image-origins.json bindet Herkunftsframehash, Originalgröße und exaktes
Rechteck. Das komplette 1280×720/UI125-PNG ist byteidentisch zur Aufnahme.
Alle Bilder bleiben unter 1 MiB, damit auch der Contents-API-Base64-Weg Bytes liefert.
Keine alternative Bildgenerierung, Nachzeichnung, Skalierung oder verlustbehaftete Kodierung.

Empfänger: unabhängiges K-B-R01 und Eigentümer K-B-M01. Nach deren Abschluss entfernen;
Aufbewahrungsbedarf spätestens am 2026-11-21 prüfen. Kein Merge dieses Reviewbranches.
W01 bleibt separat auszuführen; diese nativen Bilder behaupten keinen Chromium-/IDBFS-Pass.
Der reguläre Windows-Spieler gehört zum aktuellen Package-CI-Artefakt, nicht in diese Belegablage.
