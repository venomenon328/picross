# Feste KE-N1-Recoveryinputs

Zwei kleine synthetische, ausschließlich `test_only`-Checkouts als JSON-Mapping
von relativen Dateinamen auf Base64-Bytes. `registration-v2.json` enthält eine
unterbrochene Registrierung; `update-v2.json` eine echte Änderung von Definition
(Revision 1 → 2, fünf → acht Farben), Notice und Paketrevision r01 → r02 bei
erhaltenem Reveal. Jeweils bleiben ein anderes Rätsel und eine Save-Sentineldatei
enthalten. Die Exportdaten wurden einmalig aus den bestehenden ZA-1-Testinputs
eingefroren; sie sind keine Produktionspakete oder neuen Spielerinhalte.

Die beiden Journal-Snapshots enthalten ausdrücklich kanonische Runtime-v2-Bytes
mit sieben Feldern, unabhängig vom heutigen Projektionswriter. Tests lesen diese
festen Bytes; sie erzeugen weder Exporte noch Proofs und benötigen keine alten
Tools, Git oder Netzwerk. Aktuelle v3-Recoveryfälle bleiben in den bisherigen
Adapter-/Updatetests. Die Recovery prüft Bindungen ohne Produktionsreplay.
