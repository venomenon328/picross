# Erdbeere r06 · freigegebene Fassung registriert

Auftrag und echte Endabnahme: [Wortlaut](order.md), [Approval v2](../../r06/final-approval/approval.json). Feste Quelle `70831b4eab03d26588489d05e4f6adb339ada685`; aktuelles main `187e37bb2471c03f75a2b365ed3e341150b94f66` ist in den bestehenden Branch `content/pw/pz-erdbeere` eingemergt. Einziger Konflikt: aktueller Paketplan. Fortsetzung in Draft-PR #587, kein Merge.

## Lieferung und tatsächliche Prüfung

Native Folge erfolgreich: Finalizer v2 → Export v6 → Difficulty-Rebind → frischer lesender Plan → autorisiertes Register. Gesamtdauer der getrennten Befehle: Export 11.146 s, Plan 102.840 s, Register 328.857 s. Inklusive Teilzeiten nicht addiert. Vollständige Original-/Proof-/Herkunfts-/Paletten-/Hintergrundprüfung einschließlich unabhängigem Stagingreplay und nativen RI-Publikationsguards; kein neuer Suchsolver oder Difficulty-Analyselauf.

Registrierungscommit `c47e45bdb2026104cb6ffc861791766aa8329fbf`. Anschließend native Completion mit automatischem Record/workspace/current-view: **registered**, leere Blocker. Dies belegt den Draftbranch, keinen Mainabschluss. Historische false-Readinessfelder des v6-Exports bleiben unverändert.

13×22, drei Farben, Kategorie Obst & Nüsse, ID pz-erdbeere, Runtime-Revision 1, Stamm/Slot erdbeere_001. Aktive Bewertung **L1/medium, Methode 0.4**, E1, 11 Wellen; [neu gebundener Checked-v3-Input](checked-difficulty.json). Vollständige Bewertung, rating.source und kompakte Analyse unverändert; die historische 0.1-L2-Begleitschätzung bleibt getrennt.

Matrix `4ce02fc7b0e03dc837eeba766b2b706e049f4a07f36ab578406212089cfb0e3c`, Logik `083e33629b41e4f36d8cd66a38350de7c27213ecb660b997f568e0666be74f21`. Original-ZIP `55b9162d7157e3a5a2c505c1dfb2f64f87124eb51f0e0e12e352575354c54000`, 18871091 Bytes: bytegleich erhalten, auch im Exporttransport. Reveal A/r01 und Hintergrund B/b01 unverändert. B-Ableitung 2304×576 RGBA, 569682 Bytes, SHA-256 `0f1d7bec08c5e9ae7af48b8dca73074711b5f284d7d4f62d3bf57c1d2e9ba8a2`. Aktive Hintergrundsource bindet Bildrevision 1 und die echte Endfreigabe.

Alle 15 Exportdateien identisch installiert; Live-Reveal/Hintergrund/Notices exakt zum Export. Alle 53 bisherigen Registryeinträge exakt erhalten. Runtime v6 ergänzt an bisherigen Einträgen ausschließlich legacy-Hintergrundbindung; übrige Runtimefelder/Kategorien unverändert. Keine bestehenden Definitionen, Bilder, Ratings, Added-Daten oder Saves geändert. Bisherige Authoringrevisionen, Originalfreigaben und Index bytegleich.

Current-view originals=True, ZIP-CRC/Handoffkopie und direkte Bildsicht geprüft. 18 kleine Windows-Kernregressionen, Dokumentvalidator und Diffcheck erfolgreich. Finale CI/Remoteoriginalprüfung steht am veröffentlichten Head im PR. Kein Pflicht-Spielstart, keine Buchmontage, Kandidaten-Testintegration oder neue persönliche Abnahme.

## Selbstreview und Grenzen

Diff gegen main umfasst Erdbeerproduktion, äußere Freigabe/Operationsbeleg, genau eine neue Lieferung, Rating/Added/Hintergrund und beide Indizes. Keine Werkzeug-/Spielcode-, Plattform-, Save- oder Teständerung. `modules=[]`, `evidence.mode=none`, keine neue Dauergalerie. Selbstreview ersetzt kein unabhängiges Review.

Der bestehende Klassifizierer erkennt aktive content/backgrounds- und game/art/backgrounds-Pfade noch nicht als buildfreie Inhalte; deshalb kann die reine Produktion einen Windowsbau auslösen. Kein Override oder ungefragter Toolfix. Tatsächlicher CI-Ausgang im PR, kein Windowsstart behauptet.

Vor Mutation wies der Finalizer einmal einen zusätzlichen ungebundenen Textbeleg zurück, remaining=null. Korrigierter Request enthält nur die Approval-Datei; Auftrag separat hier. Ein stdout-Encodingproblem betraf nur das lokale Protokolllesen. Eigener unversionierter CRLF-Besitzvermerk auf LF korrigiert, Dokumentvalidator anschließend grün. Keine Produktionsdateien oder Gates als Abkürzung geändert.

Unabhängiges Review und ausdrücklich beauftragter Integrationsmerge offen. Fachlicher Abschluss nach Authoring §9 erst nach bestätigtem Mainmerge; kein vorgezogenes Retirement. Keine zusätzliche lokale Abschlussbereinigung beauftragt: eigene Anschlussdaten `.codex-erdbeere-step5` und bestehender Produktionscheckout bleiben. Eigene laufinterne Prüf-/Extraktionsstages beendet, kein offenes Journal oder Recoveryrest. Fremde/policyblockierte Altpfade nicht angefasst. Kein Release oder Deployment.
