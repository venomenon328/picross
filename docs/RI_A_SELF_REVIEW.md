# RI-A: getrenntes Selbstreview

Bezug: [#478](https://github.com/venomenon328/picross/issues/478), RI-A-V01/P01,
Basis `f47a30b904a8d4eba79ca9d3f82576aebcceaa38`, Branch
`feat/478-ri-a-registration-budgets`. Dies ist das Selbstreview des Autors,
kein unabhängiges RI-A-R01 und keine Mergefreigabe. Mess-/CI-Bindung: [T01](RI_A_VERIFICATION.md).

## Gegenstand und Befunde

Der tatsächliche Diff und die neuen Dateien wurden getrennt von der Umsetzung
gegen V01 geprüft. Es gibt keine Änderung an produktiven Katalogbytes,
Journalformaten, Methodenfreezes, Proofverifikation oder fachlichen Grenzen.

| Vertrag | Kontrollierter Befund |
| --- | --- |
| Operationsgrenzen | Neue Optionen nur an `register` und zulässiger Recovery; Plan/Update lehnen Overrides ab. Exakte numerische Typen, Endlichkeit des Werts und der Deadline vor Mutation. |
| Klassifikation | Originalbytes werden begrenzt sicher gelesen; exakte Format-/Operationspaare und Schlüssel, v2 separat, v1 gesperrt. Vollständige bestehende Journalprüfung vor Mutation. Späterer Bytetausch wird erneut blockiert. |
| Fristursprung | Publikationsrahmen vor `validate_journal`; Recovery ab API-Eintritt einschließlich Klassifikation. Keine erneuten inneren 300-s-Rahmen für Registrierung. Kürzere Außenfristen bleiben wirksam. |
| Rollback/Abschluss | Automatischer Rollback löst die verbrauchte Vorwärtsfrist und erhält seinen eigenen Rahmen. Ressourcen-/Signalursache bleibt bei gescheiterter Recovery erhalten. Dauerhaftes P6 markiert erst der erfolgreiche Verzeichnisflush nach Lockentfernung. Historischer Recoveryabschluss wird gesondert als `removed-legacy-contract` bezeichnet. |
| Sichere Reads | Nur der zusätzliche Durchlauf in `tx.read` entfällt. `io.read` behält frische Vor-/Nachpfadprüfung, Handle-/Pfadidentität, Typ-, Größen-, Alias- und Linkprüfungen. Kein Beobachtungscache. |
| Guards | Der Körper von `catalog_publication.guard` und seine fachlichen Aufrufstellen bleiben vollständig. Der zusätzliche Dekorator misst lediglich. Keine RI-B-Prüfwiederverwendung, keine RI-C-Guardausdünnung. |
| Ausgabe | Nur die vier V01-Befehle ergänzen stdout. Separater neuer Bericht, sichere Eltern-/Überlappungsprüfung, atomare Veröffentlichung ohne Ersetzen. Berichtsfehler nach Commit bleibt Diagnosefehler. |
| Messung | Monotone inklusive Phasen, physische Zähler und benannte Abdeckungsgrenzen. Keine Prozentfiktion oder Messdaten in Identitätskernen. |
| Dokumente/Bestand | CLI, API, Recoveryvertrag, RI-Status und Authoring-Dokumentrevision 26 sind nachgeführt; eingebetteter Offline-Snapshot folgt denselben Bytes. Drei neue Python-Dateien haben explizite CI-Zuordnung; keine neuen Ergebnisjobs oder Korpora. |

Im Selbstreview korrigiert: Diagnose der wirksamen verschachtelten Deadline,
Bindung der Journalbytes nach Klassifikation, ehrliche Unterscheidung des
historischen Lockabschlusses, Ablehnung ungenutzter Overrides am historischen
Writer sowie eine versehentlich entfernte CI-Datendateizuordnung. Der vollständige
CI-Lauf fand außerdem die alte exakte CLI-JSON-Erwartung für `plan`/`register`;
die Korrektur prüft die neue Diagnose zusätzlich und erhält die exakte Prüfung
aller bisherigen Fehlerfelder sowie unveränderter Checkout-/Exportbytes. Die
zugehörigen Negativfälle und erneuten Prüfungen stehen in T01.

## Offene Abnahme

Der Vorher/Nachher-Nachweis umfasst drei Wiederholungen auf Linux sowie kurzen
und normal verschachtelten Windows-Pfaden; feste Quell-/Eingangsbindung und
die verbleibenden Messgrenzen stehen in T01. Die gemessenen Werkzeugbytes
bleiben seit `a2c28518cead1f29f0fdc64afe0b65769947eded` unverändert.
Das vollständige CI-Ergebnisgate wird für den endgültigen PR-Head geprüft.
Ein unabhängiger qualifizierter RI-A-R01 auf dem tatsächlichen Lieferstand
bleibt vor Merge erforderlich. Der PR bleibt Draft; es erfolgt kein Merge.
