# CI-C: Native Prüfgruppen und Belegvertrag

Inventar vor Umstellung: `main@019b4dba98ef56c549ef5e7da10402dba0c9e93a`,
[Issue #249](https://github.com/venomenon328/picross/issues/249), CI-C/V1.
[CI-Policy](CI_POLICY.md) bestimmt Auswahl und Abnahme. Keine Produktänderung.

## Vollständige Zuordnung

| Gruppe | Erhaltene ausführbare Aussagen und Pflichtbelege |
| --- | --- |
| core | `run_tests.gd` einschließlich Save/Recovery, KAT-2-Status, goldener Atlas-/Geometriefälle; ZS2-Logik; echter Exit-23-Fehlerpfad; p13 write/read in zwei Prozessen; kontrollierter Start. Vollständige gebundene Phasenlogs. |
| history | Fünf Prozesse mit je 100 echten Aktionen, unabhängiges Python-Zell-/History-/Redo-Orakel, sechster Neustartprozess, Navigation und negative Kontrollen; `integration/summary.json`. |
| catalog | Zehn KAT-2-Modi regular/restart/large/empty/invalid/adapter/information/kb/kk/ke einschließlich aller inneren Pointer-, Slot-, Reset-, Fehler-, Last-, KE-Pixelassertions. Temporäre synthetische Adapterregistrierung gehört hierzu, nicht pauschal alle Piloten. Zehn Originalberichte, Zusammenfassung, alle 316 unverkleinerten nativen Crops. |
| completion | Eigener EA-Import; native und restart mit gemeinsamem Profil, sofortiger Commit/Save, Bewegung/Abbruch, Geometrie und ursprungsgebundener Reset. Beide Berichte, alle End-/Rechteckbilder, fünf anhand echter Zeitstempel ausgewählte Phasenbilder und unveränderte native APNG-Zeitfolge. |
| adapters | Vier RP6-Fälle partial/finish/read, fremde Slotbytes und T04-Negativkontrolle nach echter T01-Schreibaktion; anschließend alle vier Pilotcaptures aus genau diesen Saves. ZA-1: vier synthetische Pakete, echte Registrierung, Save-/Recoveryguards, zehn Prozesse einschließlich seed/oldreset, Pixel-/Slotisolation, eigener Windows-Export und tatsächlicher PCK-Audit; Windows zusätzlich EXE-Start. Alle bisherigen Pilot-/ZA-1-Berichte und Pflichtbilder. |
| graphics | VS2 write/read, GF1, HF149 write/read/native, vollständige 96er-Matrix, V1-Fokus, V2 write/read, V3/Sidebar, HC92-, HS186-, HN192-Pixel-/Eingabenachweise; fünf kompakte Capturestufen, 17 Buchzustände, aktuelle ZS2-/ZS1-Bewegungsorakel. PERF-B echte Ressourcen/Cache/Alpha/Mutation/Invalidierung. Alle bisherigen ausgewählten Originalbilder und vollständigen komprimierten Geometrieberichte. |
| export | Regulären Inhaltsbestand ausschließlich für Export übernehmen/importieren; echter Windows-Debugexport, separate EXE/Konsolenhilfe/PCK, externer nativer PCK-Audit, vollständiges Spieler-ZIP und Verpackungsprüfung. Windows zusätzlich headless und GUI-EXE-Start. |

Jede Gruppe behält die hashgeprüfte Toolchain, aktive Buch-/Atlasressourcenprüfung
und ihren eigenen isolierten Editorimport. Die genaue Pflichtdateimenge steht in
[native_artifacts.json](../tools/native_artifacts.json), ausschließlich Dateinamen
aus der aktiven technischen Matrix. Keine historischen Daten oder Korpusreplays.
EA-Phasenbilder werden weiterhin aus den tatsächlichen nativen Zeitstempeln abgeleitet.
Die vollständige Vereinigung erhält jede bisherige aktive Prüfaussage; Pilotcapture
ist jetzt auch bei allein gewählter Adaptergruppe Pflicht.

## Abnahme

CI-C-T01 bindet technische Ergebnisse, Messungen, finalen Head/Base/Test-Merge/Run
und getrennten vollständigen Selbstreview im Draft-PR. CI-C-R01 bleibt ein separater
qualifizierter Review vor Merge. Bestehende Windows-/Eigentümergates bleiben separat.
