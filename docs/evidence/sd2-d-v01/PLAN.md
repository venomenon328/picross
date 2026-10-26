# SD2-D-V01 · Technischer Planungsbeleg

**Teilvorschau, keine Übernahmefreigabe.** `plan-adoption` endete mit Exit 0 und `planned-adoption`. Der Plan bindet 44 gültige Ratings und lässt Om ausdrücklich offen. Keine Ausführung von `adopt`, keine Aktivierung und kein No-op-Nachweis einer tatsächlichen Übernahme.

Die 47 vorgeschlagenen Änderungen bestehen aus 44 Ratingdateien, zwei Dauerberichten und der Runtimeprojektion (bei späterer Übernahme Runtime-v5 mit 44×0.4 und 1×0.3). Das ist technisch zulässige Methodenkoexistenz, aber in diesem Auftrag keine autorisierte Teilübernahme. Ratings würden jeweils von Revision 1 auf 2 wechseln; die offene ID bliebe unverändert. Die Defaultquelle gehört nicht zum Plan.

Befehl: `python -m tools.puzzle_production.catalog_analysis plan-adoption --checkout <gebundener Checkout> --work-dir <Belegroot>/final-preview`.

SHA-256 des unveränderten Maschinenoutputs `plan-adoption-stdout.json`: `abc9141ffc94109d84e844ba1dd7fe1f560e4ac585cacc909bd6512e631f19ea`.

```json
{
  "changes": [
    "content/difficulty/pz-00f37200bcee4d548e2c910ce551d077/rating.json",
    "content/difficulty/pz-023b50b44d1c4698a6e17e65b6ea4337/rating.json",
    "content/difficulty/pz-1b7bf32b1fa140918c0692c90d998752/rating.json",
    "content/difficulty/pz-1e9cdac1f83a49d5982f93ded09e58de/rating.json",
    "content/difficulty/pz-20219e14dbe242689b9ef06297828f34/rating.json",
    "content/difficulty/pz-25d245061b0c49c190788de8e5d0e45b/rating.json",
    "content/difficulty/pz-2a8481f61e6443bda174bd3da67c/rating.json",
    "content/difficulty/pz-3a744ae1b7cb4d38b0ac29d030ef/rating.json",
    "content/difficulty/pz-3e97c042f0bf474e8608a84ea034c246/rating.json",
    "content/difficulty/pz-49a9e539419b48119e8f5f506fcf6dc7/rating.json",
    "content/difficulty/pz-51405ea1ad194507a60c9b6701d802f0/rating.json",
    "content/difficulty/pz-5ad1e06e19ab475baebc582d4999daa5/rating.json",
    "content/difficulty/pz-6d980b0285604e22b8ecfce205aa008b/rating.json",
    "content/difficulty/pz-72561c715dd741f9b0082c7ad24802c1/rating.json",
    "content/difficulty/pz-72eb9b188896440c8a9a833e803835ec/rating.json",
    "content/difficulty/pz-7635c2e042e349fc90ad9ae55681de0f/rating.json",
    "content/difficulty/pz-7ec3dcd94bf84e698691ef4b5839/rating.json",
    "content/difficulty/pz-82758295d5d34284bbae2716f64f/rating.json",
    "content/difficulty/pz-86d1d588a88a46e6ac1285f0097afbca/rating.json",
    "content/difficulty/pz-8ea7f3dacdcc428a9fcff7a735bc/rating.json",
    "content/difficulty/pz-8ecddf77e80c4543bf4ec714fe3d/rating.json",
    "content/difficulty/pz-985d36c1634644fbb2c8a0bf7de3aa9f/rating.json",
    "content/difficulty/pz-9a79befc7a834e2d9d5896a477328962/rating.json",
    "content/difficulty/pz-9be288b9b5104da88fc8464184647ae7/rating.json",
    "content/difficulty/pz-9d08697a30c749258b742ac979de9def/rating.json",
    "content/difficulty/pz-9f7c59054ebb4f3f861e2bce3034320e/rating.json",
    "content/difficulty/pz-a13368590b744814915eb722f5b2c5f2/rating.json",
    "content/difficulty/pz-a358a1bf1b994efcbebeb55abf825789/rating.json",
    "content/difficulty/pz-ad7164c2302a42e5953f6779a1c7/rating.json",
    "content/difficulty/pz-b180c25084a34b019f35ad2244f03c24/rating.json",
    "content/difficulty/pz-b3368aea28ac4a11bf09e0dc9c48/rating.json",
    "content/difficulty/pz-b5e2302bf71445c09caac76bbc2a7075/rating.json",
    "content/difficulty/pz-b6f94e528b48444985d0561cb48a5bc7/rating.json",
    "content/difficulty/pz-bd2783fcd3eb428c933d15259961cfcd/rating.json",
    "content/difficulty/pz-c71563f1b8c940de998afdd62f09/rating.json",
    "content/difficulty/pz-d6cb06cb41854b1da84f0ba2f043aa14/rating.json",
    "content/difficulty/pz-d7e68d1138a3448c8b2a4b07e8632350/rating.json",
    "content/difficulty/pz-d829eb9b83e94f9c9357ee5ab9c9e359/rating.json",
    "content/difficulty/pz-dad34b8331914c909e8ded79491dac94/rating.json",
    "content/difficulty/pz-dbbebc72556d4f0c9a37ab69275480e9/rating.json",
    "content/difficulty/pz-e2e5092925ce4821a9219be7816b5931/rating.json",
    "content/difficulty/pz-e45e2e0d67a34f6aa8368f477454/rating.json",
    "content/difficulty/pz-eedd1fe72af54714908d5b5aff34/rating.json",
    "content/difficulty/pz-f68e79ef419a4322b68d06817b39330d/rating.json",
    "content/difficulty/reports/sd2-d-20261026-v01-r4/report.json",
    "content/difficulty/reports/sd2-d-20261026-v01-r4/report.md",
    "game/data/registry.json"
  ],
  "open_ids": [
    "pz-87bf2975c82540a399a3d0c7fa180a25"
  ],
  "report_hash": "5aef432b5241ff7f00c3073553057c12a72e2c39ef39e64c00571cca97e28d1f",
  "status": "planned-adoption"
}
```

Der Ergebnis-/Quellsnapshot und jede ausgewählte Checked-Datei müssen vor einer später autorisierten Übernahme weiterhin exakt passen. Fremde Änderungen machen den Plan stale. Kein manuelles Neuversiegeln. Separates VR01 und passender Folgeauftrag bleiben erforderlich; D03 ist wegen der offenen ID nicht erfüllt.
