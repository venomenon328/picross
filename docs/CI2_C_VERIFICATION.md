# CI2-C · Kurzer Chromiumumfang und T01

Auftrag: [#415 einschließlich Umsetzungsvorbereitung V1](https://github.com/venomenon328/picross/issues/415).
Basis `main@dd56d310d942eee47448df4cdcca5e4af4a49b00`, Arbeitsbranch
`chore/415-ci2-c-chromium`. [Aktueller Vertrag](CI_B_BROWSER_GROUPS.md).

## Startprüfung und Umfang

Main/Issue/Kommentare am 26.10.2026 erneut geprüft: keine vorhandene C-Arbeit,
keine Kommentare. Separater sauberer Worktree; fremde unversionierte Arbeitsdateien
im ursprünglichen Checkout bleiben unberührt. `gh` ist als Eigentümer authentifiziert,
Repo-Push-/Workflowrechte vorhanden; registrierter Workflow `ci-chromium.yml`
(ID 389212566) ist aktiv. Implementierung und kurzer Chromiumlauf einschließlich
Build sind ausdrücklich beauftragt. Kein Merge, Deployment oder Release.

Neun Kernfälle und zwölf Erfolgsbilder ersetzen 33 Fälle/60 gelieferte Bilder.
Einzelgruppen bauen nur benötigte Exporte. Das separate optionale Exportprofil
hat zwei Fälle und wird nicht an kurze/all-/Toolchainscopes angehängt.
Native AT-Matrix und alle unabhängigen Nichtbrowserpflichten bleiben erhalten.

## Baseline und Messung

Original: [Run 40219765031, Versuch 1](https://github.com/venomenon328/picross/actions/runs/40219765031/attempts/1),
[Browserjob 121259857205](https://github.com/venomenon328/picross/actions/runs/40219765031/job/121259857205),
[Buildjob 121259856855](https://github.com/venomenon328/picross/actions/runs/40219765031/job/121259856855),
[Artefakt 12610550897](https://github.com/venomenon328/picross/actions/runs/40219765031/artifacts/12610550897).
Head `bc54a7122f2796949670e08925dd6eea9c4c1bf6`, Test-Merge
`01dd7f2c765fe206b4a5c1fd0f90b6713a09df3e`. Browser 40:46, Build 1:52.
Die Originalberichte wurden heruntergeladen; kein historischer Browserlauf gestartet.
Aktuelle Messungen werden nach dem ausdrücklich beauftragten Lauf ergänzt.

## T01

Lokale Werkzeugprüfung: 225 Tests, 48,321 s, erfolgreich; drei Linux-exklusive
Prüfungen hier übersprungen und für Linux-CI offen. Enthalten sind tatsächliche
Workflow-Shellgegenproben für 1/2/3 benötigte Builds, Originaleventschutz,
Ausführungs-/Bild-/Quell-/Versuchsgegenproben und fünf günstige Mechanismusfälle
an der unveränderten JavaScript-Speicherbridge. Das ersetzt keinen Browserlauf.
Aktuelle Pflicht-CI, ausdrücklicher kurzer Chromiumlauf und abschließende
Quellen-/Runbindung sind bis zu ihrer dokumentierten Ausführung offen.

## Getrennter Selbstreview und Abnahme

Der abschließende vollständige Selbstreview erfolgt nach der technischen Prüfung
und wird hier getrennt dokumentiert. Er ist keine unabhängige Zweitprüfung.
**CI2-C-R01 bleibt als separates qualifiziertes Review des finalen Heads vor Merge offen.**
Keine neue persönliche Spielabnahme allein durch diesen CI-Umbau.
