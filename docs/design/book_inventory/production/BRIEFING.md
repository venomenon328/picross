# BP-2-Übergabebriefing aus BP-1R

Stand: 26.09.2026 · **Nur Briefing; keine Bildproduktion in BP-1R.**
Der erste BP-2-A-Versuch wurde nicht akzeptiert. Zunächst neues A, erst nach
Geometrie-/Materialprüfung B als kontrollierte Variation. PR #29 bleibt historisch.
Ein gemeinsamer Bildaufbau, genau zwei kontrollierte Material-/Lichtvarianten.
Auftrag und Grenzen: [#27](https://github.com/venomenon328/picross/issues/27).

## Eingaben vor einem ausdrücklich beauftragten Bildlauf

Diese Dateien gemeinsam öffnen: [Master-Freihaltemaske](png/master-keepout.png),
[Master-Beschnittmaske](png/master-crop.png), [native 2560er Komposition](png/f02-2560-layout.png),
[primäre 1080er Komposition](png/f02-1920-layout.png) und [Geometrie](layout.json).
Die Layouts zeigen Maßvorgaben, keinen gewünschten vereinfachten Zeichenstil.
Die genaue Spielgrafik ist nur Referenz für Platzbedarf: nicht mitmalen.

Zusätzlich die erste Albumstudie, insbesondere das obere A-Beispiel, als Stileingang
verwenden, **wenn sie im konkreten Bildlauf wirklich als Datei vorhanden ist**.
Sie ist nicht in diesem Repository/ZIP enthalten. Andernfalls Verfügbarkeit vor der
Bildproduktion klären; keine angeblich gesehene Bildquelle erfinden. Die folgende
Beschreibung enthält die in #27 bestätigte textliche Übersetzung.

## Gemeinsamer Positivprompt · unverändert für beide Kandidaten

Erzeuge eine detailreich handgezeichnete 2D-Rasterillustration als Nahansicht der linken Seite eines wertigen
aufgeschlagenen, ausreichend breiten Museumsinventarbands auf einem zurückhaltenden Arbeitstisch.
Ausgabeziel 2560×1440, 16:9, opak, ohne UI. Warm, ruhig, neugierig, sorgfältig
kuratiert. Die Qualität soll deutlich über einfachen Vektorflächen liegen:
sichtbar gearbeitete Bindung, glaubwürdige Leder- beziehungsweise Gewebestruktur
an den freigegebenen Rändern, feine Nähte, leicht unregelmäßiger mehrlagiger
Seitenschnitt, differenzierte Papierkanten, vereinzelte kleine Gebrauchsspuren,
feine Einfassungen und sparsame unbeschriftete Randdetails. Kleine Messing- und
gedämpfte Blauakzente; keine flächige Ornamentfüllung. Stimmiges warmes Licht und
physikalisch plausible Kontaktschatten geben Deckel, Seiten und Einlegern Tiefe.
Das bleibt Illustration mit klaren gezeichneten Konturen, keine Pflicht zu
Fotografie, 3D-Rendering oder künstlicher Patina.

Kamera annähernd senkrecht auf eine vergrößerte einzelne linke Buchseite.
Sie füllt den Hauptteil des 16:9-Bildes, keine kleine Hochformatseite in halber
Bildschirmbreite. Ein breitformatiger Band oder entsprechend komponierter naher
Ausschnitt ist zulässig. Die Arbeitsseite bleibt exakt frontal, rechteckig und
flach, ohne perspektivische Verjüngung oder Wölbung. Der Falz liegt rechts außerhalb
aller Arbeits-/Hinweisflächen; höchstens ein schmaler Anschnitt der rechten Seite
bleibt sichtbar. Keine vollständige Doppelseite und kein darüber gelegter Bogen.
Papier, Einband und Seitenlagen sind die gemalte Bühne; keine riesige spätere UI-Karte.
Die technische Vektorvorlage bestimmt ausschließlich Geometrie und Ruheflächen,
nicht ihren vereinfachten Zeichenstil. Der alte A-Versuch darf weder nachgezeichnet
noch einfach beschnitten, vergrößert oder nichtproportional gestreckt werden.

Neue Geometrie in Masterpixeln, Ursprung links oben: linke Seite
x80/y48, 2380×1340; Falzzone x2480/y40, 16×1360; schmaler rechter Anschnitt
x2496/y48, 64×1340; Buchreserve x40/y34, 2480×1372. Der Falz bleibt auch mit
Schatten rechts der Seite, niemals unter Zahlen/Zellen oder Statuszeilen.
Natürliche kleine Unregelmäßigkeiten an freigegebenen Papier-/Einbandrändern
sind erwünscht. Bindung, Seitenlagen und Licht sollen die Buchidentität tragen;
Tisch und Requisiten treten zurück. Keine Fake-Buttons in der Illustration.

Verwende die **gesamte Master-Freihaltemaske**, nicht nur den sichtbaren F-02-Fall:
Weiß bedeutet ruhiges, gut lesbares Material unter späteren Texten, Zellen, Zahlen
und Treffern. Dort keine hochfrequenten Fasern, Flecken, Randzeichnungen,
Kontaktschatten oder harte Helligkeitsverläufe. Eine subtile großflächige Farbnuance
ist möglich, sofern die spätere UI klar bleibt. Schwarz erlaubt Detailgestaltung,
ist aber kein Auftrag, jeden freien Fleck zu füllen. Die Binärmaske selbst darf
nicht als schwarze/weiße Grafik im Ergebnis erscheinen. Keine harten Blattkanten oder Falzschatten innerhalb weißer Zonen.

Die kleine eigene Miniatur wird später als befestigte Inventarkarte separat
gerendert; daneben werden präzise Farbmuster und eine ikonische Werkzeuggruppe
eingesetzt. Bereite dafür ruhige Buch-/Papierbereiche vor, ohne tatsächliche
Karteninhalte, feste Farbschalter, Symbole oder Beschriftung einzumalen. Positionen
unterscheiden sich nach Fenstergröße; daher keine fest an einen einzelnen Screen
gebundenen Karten-/Werkzeugschatten oder Rahmen in das Hintergrundbild einbrennen.
Alle Registerkörper, ihre Beschriftung, Icons und Zustände werden separat als
UI gezeichnet. Keine dekorativen Registerattrappen oder gemalten Navigationselemente. Die spätere UI-Materialmontierung wird in BP-3
mit derselben Ausführung auf beide Kandidaten gesetzt.

Bei 1920×1080 wird das Bild gleichmäßig auf 75 % eingepasst, bei 1280×720 auf 50 %.
Die UI wird separat gerendert. Prüfe, dass Materialqualität schon bei 1080p sichtbar
bleibt. Kein benötigtes Detail an den äußersten 8 Pixeln des Masters; die
Beschnittmaske schützt den übrigen Bildbereich. Für die fünf BP-1R-Fälle wird
zunächst das ganze Bild verwendet. Keine 9-Slice-Streckung des Buchs voraussetzen.

## Gemeinsamer Negativprompt · unverändert für beide Kandidaten

Keine Wörter, Buchstaben, Zahlen, Pseudoschrift, Pseudoziffern, Logos, Wasserzeichen, Spielraster,
gefüllten Zellen, X-Markierungen, Hinweisfolgen, Werkzeugicons, Farbschalter,
Spielerminiaturen oder Rätsellösungen. Kein vorweggenommener Motivname oder
Lösungsspoiler, auch nicht als Randzeichnung. Keine Kamera-/Erfindungsmotive,
Albumkacheln, Sterne, Timer, Notizwerkzeuge, Motivvorschauen oder Texte aus dem
alten Referenzmock übernehmen. Kein gesamtes Referenzblatt nachbauen.
Keine Mottos, lateinischen Sprüche, beschrifteten Dekobücher, Motivationsplaketten
oder atmosphärischen Fülltexte. Funktionale deutsche Texte kommen ausschließlich
in die separate UI. Keine eingebrannten Kategorien wie Inventar/Orte/Tiere.

Kein Fantasy-Grimoire, keine Runen, kein Glühen, keine starken Schmutzspuren,
kein Ornamentteppich, keine generischen abgerundeten Dashboardkarten. Keine
grobe flache Buchsilhouette, keine Sammlung einfacher SVG-Flächen mit Rauschen,
keine hochskalierte unscharfe Skizze als vermeintliche Detailillustration.
Keine Schatten, Falzkanten oder perspektivische Schrägen unter dem Arbeitsraster.
Keine Halbierung, Verkleinerung oder Verschiebung der Arbeitsfläche für Dekoration.
Keine neue Themenwelt, Weltkarte, Werkbanksimulation, Audio- oder Animationsidee.

## Kandidat A · Dunkler Inventarband

Zum gemeinsamen Prompt nur diese Material-/Lichtvorgabe ergänzen:

Braunes, dunkles, fein genarbtes Leder mit dezenten Kantenabrieben und ruhigen
geprägten Einfassungen; dunkler warmer Holztisch mit zurückhaltender Maserung.
Cremefarbene, leicht warme Papierlagen, einzelne feine Bindungsnähte, kleine matte
Messingakzente und sparsame gedeckt blaue Einbanddetails. Weiches warmes Licht
von links oben, sanfte Kontaktschatten rechts unten. Papierweiß und Detailkontrast
so abstimmen, dass die geschützten Arbeitszonen ruhig bleiben. Keine dramatische
Vignette. Gewünschter Dateiname: `bp2-a-inventarband.png`.

## Kandidat B · Heller Sammlungskatalog

Zum identischen gemeinsamen Prompt nur diese Material-/Lichtvorgabe ergänzen:

Etwas hellerer taupebrauner Leinen-/Ledereinband mit feinem Gewebe an den äußeren
Rändern und zurückhaltender Lederkante; derselbe Holztisch und derselbe Bildaufbau,
etwas heller abgestimmt. Warmes Elfenbeinpapier, feine sichtbare Seitenlagen,
dieselben sparsamen Messing-/Blauakzente in denselben erlaubten Randbereichen.
Weiches diffuseres Tageslicht von links oben, etwas geringerer Schattenkontrast
als A, weiterhin warme ruhige Stimmung und klare Materialtrennung. Kein neuer
Gegenstand und kein neuer dekorativer Informationsinhalt gegenüber A.
Gewünschter Dateiname: `bp2-b-sammlungskatalog.png`.

## Ausgabe und Prüfung nach BP-2, vor BP-3

Zunächst neues A als opakes PNG prüfen, danach B mit identischer Geometrie.
Der spätere BP-2-Endstand umfasst genau zwei opake PNG-Bilder. Die schematische
rechte Informationsseite ist nur Anschlussplanung, kein weiterer Bildauftrag. Keine PSD oder angeblich
separaten Malebenen verlangen; ein sauberes Hintergrundbild genügt. Keine weitere
Variante aus Quotengründen. Bilder und transparente BP-1R-UI getrennt lassen.

Je Datei eine kurze Begleitangabe: tatsächliche native Generierungsauflösung,
gelieferte Pixelmaße/Format, Quelle/Werkzeug soweit bekannt, verwendete Referenz,
Promptvariante, Skalierung, Zuschnitt und sonstige Bearbeitung, SHA-256 sowie
bekannter Nutzungsstatus. Native Auflösung unter 2560×1440 offen nennen; bloßes
Upscaling ist kein Detailgewinn. Generierung allein ist keine Rechtegarantie.

Vor Übergabe beide Bilder in Originalgröße und bei 1080p ansehen: Materialqualität
über der Vektorskizze, erkennbares Buch, unverzogene Arbeitszone, kohärentes Licht,
vollständige Einhaltung beider Masken, keine UI-Artefakte oder Pseudozahlen.
Erst die tatsächlich zugänglichen Dateien ermöglichen die separate BP-3-Vorbereitung.
Eigentümerwahl, spätere normale Textkontraste mindestens 4,5:1 auf dem wirklichen
Untergrund und native Bedienprüfung werden dadurch nicht vorweggenommen.
