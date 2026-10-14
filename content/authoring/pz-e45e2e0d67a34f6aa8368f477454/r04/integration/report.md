# Kölner Dom r04 – Integration im Arbeitsbranch

**Standardauftrag 4 abgeschlossen bis Registrierung und Dateiprüfung.** Paket `pz-e45e2e0d67a34f6aa8368f477454/r04`, Runtime-ID unverändert, Runtime-Revision **1**, Name **Kölner Dom**, **30×50 Mono**, 747 gefüllte Zellen. Kategorie **Gebäude & Bauwerke** (`gebaeude-bauwerke`), Dateistamm/Save-Slot `koelner_dom_001`. L2 (L2–L4), begründete Schätzung/low, unverändert.

Tatsächliche [Endfreigabe](../approval.json) separat an Originalhandoff, Inventar und Endauswahl gebunden; [Erklärung und Zeitbasis](approval-context.json). Originalpaket, Handoff, Inventar, F-r01 und MA-r02 bleiben unverändert. Die offenen Felder des versiegelten Handoffs und die frühere Produktionsinspektion bleiben historische Stände; aktueller Status steht im [Record](../record.json).

ZA-1 `export` mit expliziten IDs/Kategorie/Name/Runtime-Revision/Stem/Slot erfolgreich, einschließlich frischer Eingangsprüfung und interner Prüfung der geschriebenen Ausgaben. [Inspektion](inspection.json): `technical=true`, `editorial_approved=true`, `category_ready=true`, `catalog_ready=true`. [Geprüfter Plan](plan-review.json) zeigt genau sechs Operationen; `register` einmal erfolgreich. [Befehle/Exitcodes](commands.json), [Registrierung](register.json).

[Dateiprüfung](file-verification.json) bestanden: tatsächliche Definition, Reveal und Nutzungshinweise bytegleich zum verifizierten Export. Runtime-Matrix und Hinweise entsprechen exakt dem freigegebenen Endkandidaten. Alle 46 Dateien der deklarierten ZA-1-Prüfkopie stimmen mit dem Export überein, Originalhandoff/-inventar bytegleich. Keine zusätzliche Voll-ZIP unter `content/packages`. Ein neuer Registryeintrag, alle 13 vorherigen Einträge und Kategorien unverändert; Runtimeprojektion kanonisch bytegleich. Kein offenes Registrierungsjournal.

| Bindung | SHA-256 |
| --- | --- |
| Original-ZIP | `7c0f588870e0c4a5e465a8c672d8062e970e252aac24535e1f24137aa656e2f2` |
| Originalhandoff | `a8b755a054582b3992dca53451deb935228a68d74ef7ee258580c1eb608effe6` |
| Originalinventar | `5714eb711cf258cca33c7e182a833a69bf6b38cefc2710e4bad21d63b888adea` |
| Separate Endfreigabe | `0f8a40b52e3454efda207c1f6959eefbdb3009c2970597a48fb34ab62649e1e0` |
| Registriertes Exportmanifest | `e95bedee5a3bd58183472caa8ed0f16f54efa1268a5a737fb9bd1e82fdecc3fc` |

[Getrennter Selbstreview](self-review.json): A-01 durch tatsächliche Endabnahme erledigt. Selbstreview ist keine unabhängige Zweitprüfung. Vorliegende Produktions-/Bild-/Schwierigkeitsbelege passend wiederverwendet. Native Spiel-/Save-/Neustart-/Render-/PCK-/Spielerbuild- und Volltestsuite **nicht erforderlich: reine Inhaltsintegration**. Keine zusätzlichen Routine-inspect/verify-export/check-registry/sync-runtime oder wiederholten register-Aufrufe; keine Bestands-Replays oder neuen Rätseltests.

Branch `content/cologne-cathedral-reveal-r01`, Produktions-/Integrationsquelle `34d687e5e7f03a1978dabf88cbe68778e570c006`, Zielbasis main `f666f87d36a0ea7fa3740202d08706f2215bc303`. Finaler Head und CI-Auswahl/Ergebnisse werden in [Draft-PR #112](https://github.com/venomenon328/picross/pull/112) gebunden. **Kein Merge; nicht auf main integriert, kein Release/Deployment.**
