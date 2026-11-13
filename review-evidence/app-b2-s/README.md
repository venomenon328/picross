# APP-B2-S · befristete technische Originale

Empfänger: unabhängiger Reviewer APP-B2-S-A01 für Produkt-PR #635.
Produkthead: `1b9665ca5db330f75fc2ec63c85e5dccfef83d58`.
Dieser Ref ist kein Produktbranch und wird nicht nach main integriert.

`gui-startup.json` ist das unveränderte Ergebnis einer zusätzlichen lokalen
Windows-11-Quellprobe mit echter, unsichtbarer Tk-Ereignisschleife und realem
HTTP-/Git-/Lock-Lebenszyklus. Sechs Szenarien: Skip, Stop, Offline, Opt-out,
Entwicklerstart, portable Identität. `gui_diagnostic.py` ist der tatsächlich
ausgeführte temporäre Adapter. Seine Pfadkonvention erwartet neben dem Skript
einen `worktree` mit dem Produkthead; TEMP muss außerhalb eines Git-Arbeitsbaums
liegen. Keine echte installierte App, kein öffentlicher Kanal, keine MSI-Ausführung
und kein Ersatz für APP-B2-S-R01/T03. Keine geheimen Schlüsseldateien.

`windows-mutex.log` ist das unveränderte lokale Windows-Ergebnis der bestehenden
`InstallerContractTests.test_idle_versus_held_kernel_mutex_without_touching_real_msi`.
Dieser eine Windows-Test wird im Linux-tools-Job plattformbedingt übersprungen;
die übrigen 459 von insgesamt 460 Tests bestehen dort, einschließlich aller
APP-B2-S-Fälle. Die vollständigen Original-CI-Logs bleiben im zugeordneten Run.

Die Byte-/Hashzuordnung aller bereitgestellten Dateien und Actions-Originale steht
in `originals.json`. Die MSI-/Helper-/Signaturdiagnose kommt aus dem getrennten
nicht veröffentlichenden Windowsdispatch; dortige Byteoriginale werden über den
binärfähigen GitHub-Artefaktdownload bereitgestellt, nicht nochmals hier kopiert.

Endpunkt: nach APP-B2-S-A01, spätestens 2026-11-20. Zuständig für Entfernung dieses
temporären Reviewrefs ist der beauftragte Implementierungs-/Abschlussakteur.
Gitrefs laufen nicht automatisch ab; bei offenem Gate zum Termin Bedarf und
Zustellung neu prüfen. Actions-Technik läuft nach sieben Tagen aus, der MSI-Kandidat
nach vierzehn Tagen (2026-11-27). Konkrete Artefaktlinks und Ablaufzeiten im PR.
Lokale synthetische Testzustände wurden nach jedem Lauf entfernt. Keine Änderungen
an echten Benutzerdateien, Installationen, Secrets oder Veröffentlichungsvariablen.
