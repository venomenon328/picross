# Ingwer r03 – Integrationsnachweis

**Standardauftrag 4 abgeschlossen: registered im Arbeitsbranch `chore/ingwer-reveal-r01`, Draft-PR #121. Kein Main-Merge.**

Die [echte redaktionelle Endabnahme](../approval.json) samt [Erklärungsbeleg](../approval-evidence.md) bindet das unveränderte Originalpaket r03, Handoff, Inventar und Auswahl area-160. Original-ZIP, Handoff, ältere Prüfberichte und Vorschaubild bleiben bytegleich; ursprüngliche Pending-Angaben darin sind historische Produktionsstände. Aktueller Status und vollständige Dateihashes: [Record](../record.json).

Paket `pz-985d36c1634644fbb2c8a0bf7de3aa9f` / r03; ZIP-SHA-256 `293a8c706e1dbfe49fc517a75e840b47f00af4a7ad70e5b4fc0d2f4494df2096`, Inventar `b538d147dc8ef9a83a7cc83dab3b1eaa2ff913d97e1609178e3f4967cf8fd6ac`. Runtime-ID identisch, Runtime-Revision **1**, Stem/Save-Slot **ingwer_001**, Name Ingwer, Kategorie **gemuese-pilze-kraeuter / Gemüse, Pilze & Kräuter**. 20 × 25, mono, 500 Zellen, Schwierigkeit L2 (Schätzung L2–L4, low) unverändert übernommen.

[Exportbindung](export-result.json): kategorisierter ZA-1-v2-Export hat Quelle, Normalisierung, Matrix, Hinweise, Originalfreigaben und geschriebenen Endproof frisch geprüft. `technical=true`, `editorial_approved=true`, `category_ready=true`, `catalog_ready=true`, keine Blocker. Vollständiger Export-/Prüfbericht und deklarierte Teilkopie liegen unter `content/packages/pz-985d36c1634644fbb2c8a0bf7de3aa9f/r03/`. Kein zusätzliches Routine-inspect oder verify-export.

[Plan](plan.json) geprüft: drei neue Runtime-Dateien, eine Paketkopie, zwei Registry-Ersetzungen; keine Kollisionen. [Einmalige Registrierung](registration.json) erfolgreich. [Dateiprüfung](file-checks.json): alle 58 exportierten Dateien hash-/mengengleich, Runtimebytes gleich Export, Original-B-r01 bytegleich, exakte Matrix/Hinweise, Handoff/Inventar/Freigabe unverändert gebunden. Zwölf vorhandene Einträge identisch, Ingwer genau einmal sichtbar, 13 eindeutige IDs/Slots, aktuelle Kategorien und kanonische Runtimeprojektion korrekt; kein offenes Journal.

Keine Zusatzprobe erforderlich. Native Spiel-/Neustart-/Render-/PCK-Tests und Spielerbuild: **nicht erforderlich: reine Inhaltsintegration**. Keine rätselspezifischen Tests oder zusätzlichen Bestands-Replays, check-registry/sync-runtime-Aufrufe. Prüfung von Diff und aktuellem Head sowie schlanke CI bleiben im PR dokumentiert.

Nächster erlaubter Schritt: Prüfung des Draft-PR. Merge benötigt gesonderte Freigabe; Main-Mergecommit ist null. Produktionsbereinigung nach §9 erst nach tatsächlich nachgewiesenem Main-Merge, daher bleiben Arbeitsrevisionen und Prüfkopie erhalten. Kein Release/Deployment.
