# AT-A · Originalnachweise

Die Dateien unter `windows/` sind unveränderte Originalausgaben des echten
Windows-Durchstichs am sauberen Commit
`714144eb097001e1b7d078fe318799e97d6fc459`, Basis
`9cc58651518e3a28e97f46932d69554210b0abcb`.

[Windows-Bindung](windows/windows-binding.json) enthält die beiden tatsächlichen
EXE/PCK-Exportinventare mit Hashes, drei Prozessinstanzen, originale Phasen,
identische Definitions-/Registry-/Savebytes und Hashes der sechs unveränderten
Framebuffers. Der Betriebssystem-PID kann nach Prozessende wiederverwendet werden;
die Prozessinstanz bindet deshalb PID und tatsächlichen Startzeitpunkt zusammen
mit den getrennten Exportstarts. Keine vorgegebenen Spieler-Saves.

[Vorheriger Katalog](windows/before-catalog.png),
[neuer Katalog](windows/after-catalog.png),
[neues Endbild](windows/after-end.png) und sämtliche übrigen Bilder liegen als
Original-PNGs vor. Es wurden weder Bilder skaliert noch Pixel retuschiert.
Die beiden vollständigen Exportverzeichnisse und das gemeinsame isolierte
Saveprofil bleiben lokal unter `artifacts/at-a-final/windows-final/` erhalten;
EXE/PCK-Dateien werden nicht zusätzlich in den Quellbaum kopiert.
Der vorherige Windowsnachweis zu `742f183` bleibt unverändert im Git-Stand
`059d9f9` erhalten. Der neue Nachweis enthält auch die korrigierte Behandlung
unsichtbarer Arbeitslayouts; spätere Änderungen betreffen Dokumente,
Originalartefakte und die Browseraufnahme, nicht den Produkt-/Windowsprobecode. Die finale CI-Bindung steht im Draft-PR.

Der [Windows-Startpreflight](windows-start-preflight.json) ist ein eigener
Umgebungsnachweis vor Implementierung. Sein Originalarchiv unter
`artifacts/at-a-start/preflight/p1-preflight-windows-x86_64.zip` hat SHA-256
`922868cfae5fd230dfd0143f3d8ae65a31ccbbee50aa989f741eb63fd05a0351`.
Dieser Startnachweis ist kein Abschlussnachweis des späteren AT-Codes.

Weitere gebundene CI-Originalartefakte, getrenntes Selbstreview und offene Gates
stehen in [AT-A-T01](../../AT_A_VERIFICATION.md).

## Native Linux-Originale

`native/` enthält die unveränderten 30 AT-PNGs, beide AT-Messberichte samt
Fixtures, den vollständigen `native-result.json` und die ursprüngliche CI-Auswahl
aus [Run 39261657542](https://github.com/venomenon328/picross/actions/runs/39261657542).
Dieser frühere Linuxlauf bindet Head
`742f1837cf3a5600e4160c54744b87dfa88dcba1` an dieselbe Basis; sein Integrationscommit ist
`b28f5440f31c2ad79aef4c6e2104cf296b7b3d67`, Run-/Producer-Attempt jeweils 1.
Alle sieben nativen Gruppen bestanden. Die heruntergeladenen Originale wurden
zusätzlich unabhängig mit `at_evidence.native` geprüft: 30 Katalog- und 45
Abschluss-/Überblend-/Wiederöffnungsmessungen bestanden.

Der vollständige technische CI-Download umfasst weitere bestehende Produktfälle;
hier ist der neue AT-Anteil dauerhaft gesichert. Originalartefakt-ID `12191904347`,
197201002 Bytes, GitHub-Archivdigest SHA-256
`c79055990492538241fdf00dab305baacf82e8bd8bffe33d48128b77454691c5`.
Das vollständige Inventar bleibt im originalen `native-result.json` nachvollziehbar.
Die abschließende CI des späteren PR-Heads wird separat im PR gebunden; ältere
Originale werden nicht auf einen neuen Quellstand umetikettiert.

## Linux-Produktionssuite

`production/` enthält den vollständigen unveränderten Produktionsdownload
desselben Runs: 294 Tests in 1220.602 s, `OK`, danach unabhängige Referenzläufe
mit frischer Verifikation und ZA-1-Registrierungsreplay, jeweils bestanden.
Originalartefakt-ID `12193260799`, 107435 Bytes, GitHub-Archivdigest SHA-256
`a3ecfc10d24b7342705403e4dac8d75439d8b2db99062dc975bdab32848e934f`.
Die zusätzlichen Typ-/Speicher- und Runtime-v2/v3-Gegenproben aus dem Selbstreview
entstanden danach und werden durch die nachfolgende finale CI gebunden.
