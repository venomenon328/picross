# Paket A: Windows-App für Review und Bedienprobe

Produkthead: `843e60ee84be0220a3612249df72ba72e983eb70`, PR #597, Basis
`a7e25f33be1ab5c2544477d51c0a418de526ddb0` nach P3-Integration.
Nur dieses App-Image enthält die A-Oberfläche. `components.json` führt weiterhin
P3s unveränderte Buildformatkennung; der volle Commit identifiziert die Quelle.
`delivery.json` bindet Download, EXE, Komponenten und UI-Dateien.
Das ZIP enthält das vollständige interne Datei-/Größen-/SHA-256-Inventar.

Den ganzen App-Ordner entpacken. Regulär stoppen, vor einem Update tatsächliches
Prozessende abwarten, den gesamten App-Ordner ersetzen und den getrennten eigenen
Zustand erhalten. Git bleibt Voraussetzung; kein globales Python/Node erforderlich.
Unsigniert, keine Schutzfunktionen abschalten. Kein Installer oder Autoupdater.

Empfänger: unabhängiger A-Reviewer und Auftraggeber für die ausstehende A-Bedienprobe.
Desktop/schmales Fenster: Originaldetails geschlossen, separat aufklappbar,
Formulargruppen, sichtbare Einheiten/Fokus/Tastatur, einzelne Achsen und Aufheben.
Theme: System/Hell/Dunkel bei Reload, OS-Präferenzwechsel, vollständigem
App-Stopp/Neustart und Update vom bisherigen P3-Image auf diesen A-Stand prüfen.
Akteur, Windowsversion, verwendeten Download und tatsächliche Fälle im PR melden.
Technischer Frozen-/HTTP-Smoke und DOM-Tests ersetzen diese Bedienprobe nicht.

Separater temporärer Produkt-/Reviewref `review/596-a-app-20261112`, kein Merge-PR.
Nicht in den Produktbranch übernehmen. Verfügbarkeit bis zur erforderlichen
Prüfung, geplanter Endpunkt 26.11.2026 (14 Tage Produktretention); kein automatischer
Git-Ablauf. Bei offenen Gates am Endpunkt Bedarf/Zustellung erneut entscheiden.
Danach eigenen Ref im beauftragten Rückbau entfernen. Keine sofortige Löschung
historischer Gitobjekte behauptet. Lokale Build-/Prüfdaten werden nach Sicherung
bereinigt; dieser Remote-Download bleibt für die offenen Gates erreichbar.
