# RP-4: zwölf Quellen, Vergleich und unveränderte Baseline

Status: nach R1-Nacharbeit und [unabhängigem Review R2](https://github.com/venomenon328/picross/pull/45#pullrequestreview-5416322309)
über [PR #45](https://github.com/venomenon328/picross/pull/45) als
`80ae2c19eb6f85bbac58a247badf65b3e0669132` integriert; #38 abgeschlossen.
B-01/A-01 sind geschlossen. Baseline, Bilder, Original-Commitbeleg und historische
Reviewfelder bleiben unverändert. [RP-5](../rp5/README.md) führt die festgelegten
neun Fixpunkte in einem eigenen Paket weiter.
Keine Pilot-/Katalogfreigabe oder reale Eigentümer-Lösung.

Offline-Einstieg: [Vergleichsindex](index.html). Jede Zeile verlinkt das vollständige
RP-3-Bundle mit Original, Normalisierung, exakter Matrix, Hinweisen, Proof und
ursprünglichem Validatorergebnis. Die PNGs unter `views/` stellen sämtliche
48 Raster ohne Glättung neben ihre tatsächliche Eingabe; das ist eine
Produktionsansicht mit Motivspoiler.

- [Festlegung vor Auswertung](SELECTION.md), [Korpusplan](plan.json) und
  [vollständiger Input-Lock](inputs.json).
- [Tatsächliche native KI-Aufrufe](generation.json), [Aufwandserhebung](effort.json).
- [Ursprüngliche Produktion](baseline/production.json) und
  [24 Sichtprüfungen mit 48 Einzelurteilen](reviews.json).
- [Auswertung und Akzeptanzzuordnung](../../docs/RP4_VERIFICATION.md).

19/48 Kandidaten sind vollständig logisch zertifiziert, 29/48 bleiben echte
unvollständige Fixpunkte. 14/48 sind zusätzlich nach der eigenen Sichtprüfung
motivisch für den Vergleich brauchbar, aus sechs verschiedenen Quellen. Diese
Zahl enthält alternative Varianten und Größen desselben Motivs; sie bedeutet
weder 14 eigenständige Katalogrätsel noch eine allgemeine Erfolgsquote.

## Reproduktion und Dateibindung

Python 3.11+ mit Pillow exakt 12.3.0 in der isolierten Image-Umgebung, siehe
[Werkzeuganleitung](../../tools/puzzle_production/README.md). Ab gespeicherten
Eingabedateien vollständig offline; keine KI-Aufrufe durch das Werkzeug.

```sh
.venv/rp4/bin/python -m tools.puzzle_production.rp4 verify --output-dir artifacts/rp4-replay
.venv/rp4/bin/python -m unittest discover -s tests/puzzle_production -p 'test_rp4*.py' -v
```

`verify` prüft Abdeckung/Parameter und sämtliche Input-/Bundlebindungen,
rekonstruiert Original → sRGB/EXIF → exakte Matrix → Hinweise und prüft alle
geschriebenen Proofs unabhängig. Er verlangt für akzeptierte Kandidaten
vollständige identische Enddomains. Aktuelles Replay überschreibt nie ein
ursprüngliches Ergebnis. Der Bericht bindet Head/Basis/Checkout, Run, Input-Lock,
Produktionsreport und die rastergebundenen Sichturteile. Ein CLI-Erfolg bestätigt
die vollständige Untersuchung, nicht 48 gelöste Rätsel.

Die drei eigenen Illustrationen werden zusätzlich aus dem unveränderten
`create_illustrations.py` in einem temporären Verzeichnis neu erzeugt. Geprüft
werden die genaue Dateimenge, der ursprüngliche Bildmodus, die Abmessungen und
sämtliche dekodierten Pixel. Unterschiedliche PNG-Kompression bei gleichem Bild
ist zulässig; Modus-/Größen-/Pixeländerungen sind es nicht. Das lockert keine
Dateibindung: Die gespeicherten Originale und das Erzeugungsskript behalten ihre
ursprünglichen SHA-256-Werte im Plan/Input-Lock. Auch ein nur umkodiertes
gespeichertes Original wird dort weiterhin abgewiesen.

R1/B-01 wird zusätzlich in einem begrenzten Windows-CI-Job mit Python 3.12.10 und
Pillow 12.3.0 geprüft. Der R1-Ausgangstest muss an der dokumentierten
PNG-Byteabweichung scheitern, die aktuellen RP-4-Tests müssen vollständig bestehen.
Laufzeit-/Codec- und Commitdaten stehen im kleinen Windows-Nachweisartefakt;
der Linux-Fachjob bleibt für Referenzbudgets und vollständigen Replay zuständig.

Optional ein neuer deterministischer Produktionslauf in **neuem** Ausgabepfad:

```sh
.venv/rp4/bin/python -m tools.puzzle_production.rp4 produce --output-dir artifacts/rp4-new-production
```

Die eingecheckte Baseline bleibt unverändert. Zeiten neuer Läufe dürfen abweichen;
Codecunterschiede werden nach dem RP-3-Vertrag auf exakte Pixel geprüft. Eine
Neuerzeugung aus den Prompts wird nicht als reproduzierbar behauptet.
`freeze` war der einmalige Eingangsabschluss vor dem ersten Lauf und verweigert
ein Überschreiben von `inputs.json`. `views` und `index` bauen ausschließlich die
Vergleichsansichten aus vorhandenen Daten; keine Rasterkorrektur/Filteroptimierung.

## Provenienz der vorab fixierten Stände

Korpus-Festlegung: `37c97a6215a550a6e74fd2536a30c8ff13d9baba`.
Alle 24 Eingänge inklusive nativer Stilisierungen wurden vor dem ersten Solverlauf
im sauberen lokalen Commit `726e89d573558a558c6b64f883c33331a26b8365` fixiert.
Der tatsächliche Produktionsreport führt diesen unveränderten Produzentenbezug.
Sein Git-Baum `80201bbde68240dd51f8583acdb103db4a791bbe` wurde über die GitHub-API
byteidentisch als `5926bab3fb7a59ebd07e741869f3286d2bb41860` veröffentlicht;
nur Commitmetadaten unterscheiden sich. Der direkte Git-Push hatte keine
Anmeldedaten, der autorisierte GitHub-Zugang übernahm die Veröffentlichung.

R1/A-01 verlangte zusätzlich die unabhängig abrufbaren Bytes des ursprünglichen
Commitobjekts. [Der Originalpayload](provenance/producer-726e89d.commit) wurde für
R1-N1 mit `git cat-file commit` binär aus dem erhaltenen Produzentencheckout
ausgelesen: 268 unveränderte Bytes, keine Rekonstruktion der Metadaten. Seine
SHA-256 ist
`4e4b747ad959ee9c7c267c04e0f4ed60d35b692c8d00858e43bec1a27c8a2cac`.
Der Git-Objektheader `commit 268` einschließlich NUL plus diese Bytes ergibt die
ursprüngliche Commit-ID. Dies lässt sich auch in einem frischen Checkout prüfen,
ohne dass dessen Git-Datenbank das historische Originalobjekt enthält:

```sh
git hash-object -t commit examples/rp4/provenance/producer-726e89d.commit
python -m unittest discover -s tests/puzzle_production -p 'test_rp4_provenance.py' -v
```

Erwartete Objekt-ID: `726e89d573558a558c6b64f883c33331a26b8365`. Die ersten beiden
Payloadzeilen binden Tree `80201bbde68240dd51f8583acdb103db4a791bbe` und Parent
`37c97a6215a550a6e74fd2536a30c8ff13d9baba`; der veröffentlichte Commit
`5926bab3fb7a59ebd07e741869f3286d2bb41860` führt denselben Tree/Parent. Der Test
bindet den tatsächlichen Payload außerdem an den unveränderten Produktionsreport.
Die unabhängige Nachprüfung lädt den Beleg aus dem finalen Remote-Stand selbst.
Die Objektbindung ist kein nachträglicher Augenzeugenbeleg für den damals im Report
als sauber protokollierten Arbeitsbaum. Sie ändert keinen Produktionsbezug.

Input-Lock SHA-256:
`21f2f9f5b719f6eb244e3617f351faa9a1d9741d95b68e5a23ee243d791bbe43`.
Originaler Produktionsreport SHA-256:
`63568a23fe97f3465a419e46a4dbf202b4a252ac88c59f358a1a0269a9ac2d3e`.
Keine Quellen ausgetauscht, keine verworfene Variante ausgelassen. Sieben lokale
temporäre Stagingreste (45 Dateien) wurden nach vollständigem Bytehashvergleich
als Duplikate veröffentlichter Bundle-Dateien außerhalb des Repositorys erhalten;
sie enthalten keinen zusätzlichen Versuch oder abweichendes Ergebnis.
