# Bierglas r03 · Standardauftrag 4

Endabnahme durch Tobias Schröder mit tatsächlicher Erklärung in [user-request.txt](user-request.txt), gebunden in [approval.json](../approval.json). Eindeutiger Gegenstand: r03, Inventar `c211e4c7f6876b883788a6840df2cde6f332a088069dd2464e9626bc0ac6e5c5`. UTC-Aufzeichnungszeit und Auflösung der r02/r03-Formulierung stehen im [Freigabekontext](approval-context.json).

Originalpaket [package.zip](../package.zip): SHA-256 `f723bd3b6a417d94daaf4fa6e76452a8101a097d2f98689944a5ff570130c47c`, 10.836.014 Bytes; Originalhandoff/-inventar unverändert. Keine neue Produktion oder Neuversiegelung. Quellenhead `1147aeb27d5cee911d408624904cefadd09b3c19`, Basis `f666f87d36a0ea7fa3740202d08706f2215bc303`; Branch `content/bierglas-abschlussbild-r01`, Draft-PR #107.

Kategorisierter ZA-1-v2-Export: `technical=true`, `editorial_approved=true`, `category_ready=true`, `catalog_ready=true`, keine Inhaltsblocker. [Exportbericht](export-result.json), [frische Exportinspektion](inspection.json). Kein zusätzlicher Routine-inspect/verify-export.

[Plan](plan.json) geprüft: genau drei neue Runtime-Dateien und eine Adapter-Prüfkopie, zwei Registry-Ersetzungen, genau ein neuer Eintrag; übriger Bestand/Kategorien unverändert. [Registrierung](registration.json) einmalig erfolgreich. Runtime-ID `pz-ad7164c2302a42e5953f6779a1c7`, Revision **1**, Stem/Save-Slot **bierglas_001**, Name **Glas Bier mit Schaumkrone**, Kategorie **suesses-getraenke / Süßes & Getränke**. 25×30 Mono, freigegebene Matrix/Hinweise und C-r01 unverändert übernommen.

[Dateiprüfung](file-verification.json): Runtimebytes identisch zum Adapterexport, Originalbindungen/Freigabe erhalten, exakte Registryprojektion und einzige Kategoriezuordnung, vollständige Manifestdateimenge/Hashes der geschriebenen Prüfkopie, keine offenen Journale. Prüfkopie: 49 Dateien / 7233069 Bytes; keine zusätzliche ZIP-Kopie. Manifest-SHA-256 `61444bab41a9fb953eed9e2488bdce0d4bbe11764a559a9d97cba395d9abb06e`; Freigabe-SHA-256 `09b80c4d4608f64daea486be4b0817781b7c8923a0f7aad17e08894fac489830`.

Getrennter [Selbstreview S4](self-review.json); finale Head-/Test-Merge-/CI-Bindung im PR. Native Starts, Saves, Renders und Spielerbuild: **nicht erforderlich: reine Inhaltsintegration**, nicht ausgeführt. Keine neue rätselspezifische Testsuite oder Bestandsreplays manuell gestartet. Pflicht-CI: `content_only=true`, `docs` und `ci-required` am finalen Head. Offen bleibt der gesonderte Mergeauftrag; kein Main-Mergecommit, kein Release.
