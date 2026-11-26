# Schritt 1: Abschlussbilder

**Version 0.8.0 · Dokumentrevision 11 · 26.11.2026 · PW-REMOTE-G**

Pflicht: [Kern und Phasenroute](PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase),
danach diese Phase und die dort zugeordnete Bildnorm. Zusätzlich:
[Qualität](../PUZZLE_QUALITY.md) §2/§3.1.
Sicherung, Wiederaufnahme, gemeinsame Bildkorrektur und Abschlussausgabe: Kern §§6–7.

Jedes Abschlussbild vor der Vorlage anhand der gespeicherten Originalbytes, Maße, Rechte und Q-B01–03 qualifizieren. Die Motivphase übernimmt die gebundene Wahl, die gemessenen Maße und die gültigen Urteile aus Groß- und Kleinansicht.

## 2. Abschlussbild zuerst

### 2.1 Eingaben und Konfiguration

Zulässiger Input: Motivtext beliebiger Ausführlichkeit und/oder Ausgangsbild;
optional Breite/Höhe (ungefähr/fest), Mono/Farbe, Vordergrundfarbzahl
(ungefähr/genau) und weitere Einschränkungen. Eine Vorschau ersetzt keine
Originaldatei. Hauptmotiv, unverzichtbare Merkmale, erlaubte Umgestaltung und
Einschränkungen erfassen. Reversible Details sinnvoll ergänzen; nur wesentliche
offene Entscheidungen mit Empfehlung und Konsequenzen klären.

Frühe Breiten-/Höhenwünsche sind unabhängig: keine, eine oder beide Achsen.
Exakt/ungefähr gilt für ausgefüllte Achsen. Offene Achsen zum Motiv bestimmen;
keine 0, angenommene Quadratseite oder Wiederherstellung aufgehobener Altwerte.
Eine ausdrücklich aufgehobene Breite erhält die weiter gültige Höhe und umgekehrt.
Bloßes Leeren hebt keine veröffentlichte Vorgabe auf. Wünsche im Motivbriefing
sichern; die konkrete spätere Matrix besitzt zwei Maße. Ein freigegebener
Parameterkorridor wird nicht stillschweigend durch spätere Formularwerte geändert.

Zuerst Abschlussbilder nach [RV-02](../images/REVEAL.md#rv-02-illustration),
noch keine Abstraktion, Zellmatrix oder Hinweise. Fehlende Rastermaße/offener
Modus blockieren diese Bildwahl nicht.
Die spätere Abstrahierbarkeit berücksichtigen, ohne die Illustration vorzeitig
auf Zellniveau zu vereinfachen. Eine eigene Eingangsdatei ist zunächst Referenz,
keine automatisch freigegebene Abschlussbilddatei.


### 2.4 Abschlussbildauswahl und Abstraktionsfreigabe

1. Standardmäßig drei sinnvoll unterschiedliche echte Abschlussbilder erzeugen;
   Komposition/Pose/Farbgebung im Auftrag variieren; der gestalterische Anspruch
   folgt [RV-02](../images/REVEAL.md#rv-02-illustration).
   Bindende Referenz (`faithful`) und freie Interpretation (`free`) unterscheiden.
   Nur eine ausdrückliche Vorgabe reduziert die Variantenanzahl.
2. Native Bildgenerierung verwenden; jede Variante tatsächlich als Einzeldatei
   speichern und zeigen. Eine Kontaktübersicht ist nur Auswahlhilfe. Fehlende
   Bildfunktion blockiert den Bildschritt; Konzepte ersetzen keine Originale.
3. Vor jeder Abstraktion muss das konkrete Abschlussbild ausdrücklich freigegeben
   sein: Datei, Revision/Hash und geschützte Merkmale. Eine Auswahl mit Korrekturwunsch
   ist keine Freigabe noch nicht vorhandener korrigierter Bytes.

Übergabe: reveal_review mit erreichbaren Originalen zur tatsächlichen Bildwahl/-freigabe.
Keine Abstraktion vor dieser Entscheidung; neue Briefings erfinden keine ID/Gitquelle.

### PW-FIND · Annahme und Revealwahl

Für aktuelle Befundentscheidungen gilt der Weg nach
[Kern §6.3](PUZZLE_AUTHORING.md#63-pw-find--phasenübergreifende-befundentscheidungen):
Zulässige konkrete Bildbefunde dürfen zusammen mit der Wahl genau dieses
Revealoriginals zur Abstraktion angenommen werden. Offene andere Kandidaten
sperren die geeignete Wahl nicht. Nutzungsgrundlage, feste Motivgrenzen und
wirkliche Bildwahl bleiben erforderlich. Korrekturgrundlage darf ein blockierter
Kandidat sein; fortgeführte Befundannahmen wählen keine neuen Bildbytes vorab.
