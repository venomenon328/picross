# Schritt 2: Motivvorlage

**Version 0.8.0 · Dokumentrevision 12 · 23.11.2026 · KORRIDOR-NORM-A**

Pflicht: [Kern und Phasenroute](PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase),
danach diese Phase und die dort zugeordnete Bildnorm. Zusätzlich:
[Qualität](../PUZZLE_QUALITY.md) §2/§3.2 und H-03/H-04 aus §4.
Sicherung, Wiederaufnahme, gemeinsame Bildkorrektur und Abschlussausgabe: Kern §§6–7.

## 2. Motivvorlage nach Revealfreigabe

### 2.1 Konfiguration nach Bildfreigabe

Nach Bildfreigabe bei offener Konfiguration zwei bis drei sinnvolle Möglichkeiten
knapp vergleichen und eine empfehlen. Motivtreue, Darstellbarkeit, Logikrisiko
und Spielgefühl getrennt begründen; Rechtecke gleichberechtigt berücksichtigen.
Dies verlangt nicht mehrere tatsächliche Abstraktionsbilder.

- Regulär höchstens 50 Zellen je Achse; größere technische Werkzeuggrenzen sind
  keine Produktfreigabe. Klein (längste Achse bis 20), mittel (21–35) und groß
  (36–50) unterscheiden Detailspielraum, nicht logische Schwierigkeit.
- Acht Vordergrundfarben plus Leer sind die technische Obergrenze, kein Ziel.
  Die kleinste motivgerechte Palette empfehlen; Ausgangspunkt Mono oder 2–4 Farben.
  5–8 nur mit benanntem motivischem Nutzen und erklärtem Verlust bei Zusammenlegung.
- Farbzahl zählt tatsächlich verwendete Vordergrund-IDs; EMPTY zählt nicht,
  Weiß kann Vordergrundfarbe sein. Unbenutzte Einträge, ähnliche Schattierungen
  und dekorative Einzelzellen erfüllen keinen Farbwunsch. Vor Versiegelung auf
  nötige Einträge reduzieren und die erforderlichen Neuprüfungen ausführen.
- Genaue Farbzahl ist fest; Konflikte vor Abweichung klären. Ungefähr ist ein
  begründbar abweichendes Ziel innerhalb des vorgeschlagenen und danach
  freigegebenen Korridors. Eine frühe exakte Vorgabe von einer Vordergrundfarbe
  ergibt bei der Parameterfestlegung Mono, wenn der Modus offen war. Explizit
  farbig mit genau einer Farbe ist ein zu meldender Widerspruch. Bei offener Farbzahl
  die empfohlene Palette und eine sinnvoll reduzierte Alternative erläutern,
  Farbrollen nach [MV-03](../images/MOTIF.md#mv-03-farbrollen) benennen.
  Keine zusätzliche Vollmatrix verlangen.
- Maße, Seitenverhältnis und Palette zum Motiv wählen. Vor Nachweis keine
  Lösbarkeit versprechen. Für jede ungefähre Achse den frühen Wunsch als
  **bevorzugten Zielwert** führen. Vorschlagskorridor mit Zielwert, expliziter
  Unter- und Obergrenze, erlaubten Beschnittseiten und geschützten Merkmalen
  begründen. Den Spielraum nach Motiv und Größe so bemessen, dass absehbarer
  Beschnitt leerer Außenlinien und motivtreue Formkorrekturen Platz haben.
  Exakte Achsen bleiben exakt und schließen Beschnitt auf ihrer Achse aus.
- Beispiel für die Breite „ungefähr 20“: Wenn ein 20-Zellen-Import links
  voraussichtlich drei leere Außenspalten hat, kann ein Vorschlag etwa Ziel 20
  und Grenzen 17 bis 22 enthalten. Linksbeschnitt ist nur für leere,
  ungeschützte Spalten vorgesehen. Silhouette und ein prägender Innenraum
  bleiben geschützt. Die Untergrenze ermöglicht so ein motivtreues Endmaß 17.
  Die Obergrenze lässt bei diesem Beispiel etwas Raum für einen größeren
  Importstart, falls die Kontur ihn braucht. Andere Motive und Größen
  erfordern eine eigene Begründung. Es gilt keine pauschale Prozenttoleranz.
  Verbindlich wird der Korridor erst durch die tatsächliche Freigabe nach §2.4.
  Materielle Abweichungen vor weiterer Produktion entscheiden lassen.

### 2.4 Abstraktionsfreigabe

4. Danach standardmäßig eine begründete Abstraktion aus den gespeicherten Bytes
   für die empfohlene Konfiguration erstellen. Weitere Varianten nur für konkrete
   offene Darstellungs-/Detailfragen, nicht zur Erfüllung einer Quote. Reveal und
   Motivvorlage nebeneinander vorlegen; Verluste und Parameterkorridor benennen.
5. Vor Rasterproduktion echte Freigabe der Motivdatei samt Revision/Hash,
   Revealbezug, Invarianten und zulässigen Maß-/Modus-/Cropvarianten abwarten.
   Bildfreigabe ersetzt keine Motivfreigabe; Schweigen ist keine Entscheidung.

Übergabe: motif_review mit Reveal-/Motivvergleich, Verlusten und Parameterkorridor;
vor Rasterarbeit tatsächliche Motiv-/Parameterfreigabe abwarten.

### PW-FIND · Annahme und Motivfreigabe

Für aktuelle Befundentscheidungen gilt der Weg nach
[Kern §6.3](PUZZLE_AUTHORING.md#63-pw-find--phasenübergreifende-befundentscheidungen):
Konkrete zulässige Befunde der gewählten Abstraktion können im selben Auftrag
wie Motiv- und Parameterfreigabe angenommen werden. Revealbezug, Motivbytes,
geschützte Merkmale und eine vollständige zulässige Parameteralternative bleiben
gebunden. Eine Annahme ändert keine festen Maße, Farbzahl oder Motivgrenzen.
Korrigierte Motivbytes benötigen ihre tatsächliche Wahl trotz zulässig
fortgeführter Befundannahmen.
