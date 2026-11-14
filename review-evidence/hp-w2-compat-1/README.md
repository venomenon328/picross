# HP-W2-COMPAT-1: gezielte Revieworiginale

Produkt-Head: `ac70185e12c0d47722a0e84e437f3861f1bb62e4`.
Basis: `e1e8caf91d9ad1e6661807e09020c338ad6b6d29`.
Originaler Inhaltsstand: `58799134bf11e16bae4d946e8f6ebdadda3edfed`.
Empfänger: unabhängiger Sicherheits-/Integritätsreviewer von PR #647, K07.
Ablauf: **21.11.2026** oder abgeschlossene unabhängige Prüfung, je nachdem was
zuerst eintritt; separaten Ref `review/645-hp-w2-compat` dann im beauftragten
Paketabschluss entfernen. Kein Merge-PR für diesen Belegbranch, keine Übernahme
dieser Dateien nach main. Nach Fristablauf bei offenem Gate Zustellung neu prüfen.

Die Belege dokumentieren eine isolierte technische Nachstellung; #603/#602 wurden
nicht integriert. Keine Registrierung, Completion, Saves, kreativen Bildänderungen
oder neue Inhaltsabnahme. Der echte Produktionscheckout bleibt unverändert.

## Zuordnung

- `baseline.json`: tatsächlich reproduzierter INT-B01 auf dem damaligen aktuellen
  main, vor Mutation; vollständiges historisches Tool, alle neun gegen den
  gebundenen Gitcommit geprüften Modulhashes, aktuelle Codecs/Profil und die
  beiden abweichenden Module. Historische Erzeugermodule wurden nur als Bytes
  gelesen, nicht ausgeführt. `baseline-source.py` ist das verwendete Einmalskript.
- `derive-request.json`, `selected-proof/derivation.json`, `selected-proof/background.png`:
  unveränderte Originalbindungen; `selected-verify.json` bestätigt die echte
  aktuelle Reproduktion mit identischen Bytes einschließlich Diagnostik/Toolobjekt.
- `selected-original.png`, `selected-reveal.png`: unveränderte ausgewählte
  Bildoriginale aus dem Original-ZIP, direkt binär erreichbar. Kein neuer Bildentwurf.
- `original-request/`: unveränderte gespeicherte finale Auftragserklärung,
  Endfreigabe v2, Request und alter Fehlerbefund aus dem festen Inhaltscommit.
- `finalize*.stdout.json`, `finalizer-state/`, `final-inspection.json`:
  tatsächlicher Finalizer v2, Wiederholung `reused`, nachfolgende volle Prüfung
  von `editorially_approved`. Nur Record/Projektion/Ansichtsverweis wurden in
  der isolierten Kopie fortgeschrieben; vier neue finale Sidecardateien.
  Alle anderen 60 bestehenden Dateien behalten Bytes/mtimes, siehe
  `unchanged-originals.json` (63 bestehende Dateien insgesamt).
- `export/`: vollständig verifizierter tatsächlicher v6-Export einschließlich
  byteidentischem Original-ZIP und gebundenen äußeren Belegen. Runtimebilder
  sind direkte Originaldateien, keine Vorschauskopien. Exportfalse-Felder bleiben.
- `offline-verify.json`: wirkliche API-Prüfung mit umbenannten ursprünglichen
  Authoring-/Payloadpfaden, verbotenem Netz und verbotenem Historyreader.
  `verify-export.stdout.json`: zusätzlicher tatsächlicher CLI-Aufruf bei
  nicht erreichbarem ursprünglichem Authoringpfad, Exit 0.
- `synthetic.log`: sechs neue Positiv-/Negativregressionen auf dem Produkt-Head,
  51,083 s, alle erfolgreich. Erzeugersimulation und injizierte Testidentität
  gelten nur für künstliche Inputs. Aktuelle Quellenleser, Bildberechnung,
  Dateivergleiche und Consumertransaktionen bleiben wirklich ausgeführt.
- `binding.json`, `current-description.json`, `manifest.json`: Produkt-/Quell-/
  Tool-/Versionsbindung und echte Dateihashes/Bytezahlen. Hashlisten ersetzen
  keine Originalsicht oder unabhängige Abnahme.

PNG: `a937d68149a2828d19e7295de6d9069da9314dede967a133547f77831536b91f`,
610336 Bytes, 2304×576 RGBA. Befund:
`eddc3abfdfca0d60f07bfa9269434dce3b87972f2e72244b40634c3de7bd21b0`, 3941 Bytes.
Beide sind unverändert aus dem Inhaltsstand; keine neue Ableitung als Ersatz
für die alte Recordprüfung. Die produktive Erzeugeridentität ist genau
`23971ee3834218f28977a346e09f716de6eb18fd6fc3acb8cab25a5ad8cab691`.

## Erneute technische Nachstellung

Alle eigenen Checkouts/venv/Temps unter einer ausdrücklich gewählten Arbeitswurzel
anlegen. Windows, Python 3.13.14, Pillow exakt 12.3.0, zlib `1.3.1.zlib-ng`,
LittleCMS 2.19 sind die tatsächlich geprüfte historische Versionsmap. Abweichende
Codec-/Pythonstände werden absichtlich nicht kompatibel erklärt.

Für die Baseline die fest gebundenen Quellen als eigene detached Worktrees unter
`<T>/repo` (Basis) und `<T>/isolated` (Inhaltsstand) anlegen. `baseline-source.py`
nach `<T>/` kopieren und mit der isolierten Bildumgebung ausführen. Das Skript
vergleicht die historischen neun Modulbytes per `git show`, legt `<T>/payload`
aus der unveränderten gespeicherten Approvaldatei an und schreibt die Baseline
nach `<T>/evidence/baseline.json`. Finalizerfehler und ausbleibende Mutation
werden geprüft. Keine Module des historischen Erzeugercommits ausführen.

Für den positiven Durchstich einen eigenen sauberen Werkzeugcheckout am oben
genannten Produkt-Head verwenden. Vom Werkzeugcheckout aus:

```text
python <Belegpfad>/replay.py --original-root <T>/isolated --payload-root <T>/payload --evidence-root <T>/new-evidence
```

Das Einmalskript wird nicht in CI-Discovery aufgenommen. Es verändert nur den
ausdrücklich isolierten Inhaltscheckout, führt niemals plan/register/completion
aus und prüft alle unveränderten Originale sowie Finalizer-No-op/Export/Offlineweg.
Für einen erneuten Lauf einen frischen eigenen Originalcheckout verwenden.
Die Baseline benutzt den Basiscode, der Positivlauf ausschließlich den aktuellen
Produktcode. `PYTHONIOENCODING=utf-8` ist für Windows-CLI-Logs gesetzt.

## Originalabruf

Dateien am festen Belegcommit per Git oder binärfähigem Raw-HTTP-Client laden,
gegen `manifest.json` (Pfad/Bytezahl/SHA-256) prüfen und Bilder tatsächlich öffnen.
Ein textgebundener Contents-Abruf oder eine GitHub-Vorschau ersetzt das nicht.
ZIP nur mit einem echten Binärdownloader laden und mit einem sicheren ZIP-Leser
öffnen. Die direkte Bildzuordnung ist zusätzlich oben vorhanden. Die Zustellung
wird vor der Übergabe tatsächlich binär nachgelesen; diese Prüfung ersetzt nicht
das unabhängige Review am Produkt-Head.
