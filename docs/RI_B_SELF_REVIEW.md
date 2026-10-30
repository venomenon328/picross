# RI-B: Getrenntes Selbstreview

Geprüfter Werkzeug-/Testhead: `a46d7c9945d2f06af7a5943ca4c9504a829fc59f`.
Basis: `864c4e6289df15ea7b3522b850542ece3489160f` (main/RI-A).
Nachfolgende T01-/Statusdokumentation verändert keine gemessenen Werkzeugbytes.
Prüfung am vollständigen Diff nach Implementierung und Testlauf: **Selbstreview**,
keine unabhängige Zweitprüfung. Finaler PR-Head/Test-Merge/CI folgen im T01-CI-Anhang.

## Selbst geprüft

Vollständige Code-/Test-/Normativänderungen samt unverändertem Aufrufkontext von
Integration, gemeinsamem Writer, Checkoutreplay und Recovery gelesen. Der Kontext
wird nur nach unabhängig erfolgreichem vollständigem Staging-Replay aktiviert;
der erste Eingangsproof bleibt. Die isolierte Ergebniskopie ist kein externer
Pass-Beleg. Original-/Stagingbytes, Inventare/Identitäten, Freigaben/Parameter,
Checked-Quelle, Ausgangssnapshot, genau ein Journal samt Addition-Mapping und
tatsächliche Werkzeug-/Methodenbytes bleiben gebunden. Die aktive Instanz prüft
Prozess, Thread und Checkoutidentität. Scopeende entzieht sie auch bei Abbruch;
keine Serialisierung, Persistenz oder versteckte globale Prüferumschaltung.
Die Vertrauensgrenze ist der kontrollierte Pythonprozess, keine Schutzbehauptung
gegen beliebigen darin autorisierten Pythoncode.

P3/P5 prüfen vollständig frische geschriebene Paketbytes und Inventare;
bytegleicher Austausch gebundener Dateien, Staging oder Checkoutroot invalidiert
den Kontext. Andere Einträge behalten vollständigen Replay. Runtime/Notice
bleiben unabhängig über Journalvalidierung, sichere Writerreadbacks und
Projektion gebunden. Plan/No-op/Update erhalten keinen Kontext; Plan blieb
lesend, No-op erhielt Bytes/mtimes. `verify_export` selbst blieb bytegleich und
immer vollständig. Kein neuer CLI-Schalter oder neuer Freigabeschritt.

AST-Vergleich gegen die Basis: vollständige Körper von
`catalog_publication.guard/recover/_checkpoint/write`,
`catalog_transaction.guard/recover/_recover/validate_journal` und
`content_registry.recover/_recover` identisch. Alle globalen `guard`-/`guard_fn`-
und Checkpointaufrufe in beiden Writern bleiben in identischer AST-Reihenfolge.
P0–P6/R0–R2 werden nicht verschoben; alle positiven Messungen bestätigen 80 Guards.
Recovery hat keinen Kontextparameter und keinen versteckten Reuseweg.
Rollback/Fremdbyteerhalt, Ressourcenfehler und dauerhafter P6-Abschluss bleiben.
Keine neue Journalgeneration. Beide Freezes und gebundenen Methodendateien sind
bytegleich, ihre strikten Prüfungen aktiv. Keine neue Solver-/Difficultyanalyse.

Offline-HTML gesondert geprüft: eingebettetes Regelwerk stimmt exakt mit
Authoringrevision 27 überein; sichtbare Revision und Requestmetadaten sind
ebenfalls aktualisiert. Kein Browserlauf. CI2-Konsumentenzuordnung besteht ihre
acht Prüfungen: neues Testmodul genau catalog, Quellenmodul images/adapter/catalog.
Gemeinsame Änderungen unterdrücken keine weiteren benötigten Nichtbrowserjobs.

## Nachweise, Befunde und offene Gates

[T01](RI_B_VERIFICATION.md) bindet gezielte Linux-/Windows-Tests, sechs echte
A/B-Berichte mit je drei Wiederholungen und vollständige Eingangs-/Quellinventare.
Der lokale volle Tool-/Dokumentlauf scheiterte an Sparse-Checkout und vorhandenen
ignorierten Arbeitsartefakten; kein behaupteter Pass. Aktuelle vollständige
Remote-CI bleibt erforderlich. Verworfene Windows-Messungen sind als Fehlschläge
dokumentiert; keine fehlende Plattform oder nicht angeforderte Browserprüfung
wird als Erfolg ausgegeben.

**RI-B-O01 bleibt offen:** vollständige Kandidaten-/Einzelproof-/Exportprüfungen
sinken 4→2, die Registrierungszeit steigt im kleinen synthetischen Fall.
Zusätzliche Byte-/Identitätsarbeit ist teuer; der Befund ist in #477 persistiert.
Keine Sicherheitsbindung oder globale Guardstelle wurde dafür entfernt;
kein RI-C- oder erweiterter Cacheauftrag daraus. Große Kataloge, komplexe
Proofketten, harte OS-Kills und Betriebslasten sind nicht abgenommen.

Urteil der Eigenprüfung: enger B-Umfang implementiert und gezielt geprüft,
kein festgestellter verbleibender funktionaler Blocker. Aktuelle Pflicht-CI,
gesondertes qualifiziertes Review und ausdrückliche Mergefreigabe bleiben
getrennte Gates. Draft-PR, kein Merge.
