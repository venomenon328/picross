# SD2-D-F01/T01 · Delta, Arbeitsbelege und Selbstreview

[Ausführungsbericht](../../SD2_D_ADOPTION.md).

Vollarchiv auf dem gemeinsamen Arbeitsplatz: `E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-f01-full-evidence.zip`.

SHA-256: `6a5a2d05e8f34765e3b307dde73b393214133b8baf01fe853f958da7c17b24da`.

134 Dateien, 2306355 Archivbytes, einschließlich des unveränderten vollständigen OM01-ZIP mit sämtlichen V01-Belegen. Alle Einträge nach dem Packen per CRC, Größe und SHA-256 zurückgelesen.

Manifest-SHA-256: `8d8f6699ee6d6cda53b5e0638bda2507b434cd5f8823d734df93fb0de70c56d1`. Das Archiv ist lokal vorhanden, nicht remote hochgeladen. Für Review außerhalb des gemeinsamen Arbeitsplatzes ist es bereitzustellen. Die eingebetteten Archive bewahren die gesamte akzeptierte Eingangskette; Originalarbeitsverzeichnisse bleiben unverändert. Kein Ausführungsskript erneut starten.

## Tatsächliche Aufrufe

| Schritt | Ergebnis | Änderung |
| --- | --- | --- |
| `rating-adopt` | Exit 0, `adopted` | 48 Pfade |
| `rating-noop` | Exit 0, `no-op` | keine, vollständige Dateiinvarianz |
| `activation-plan` | Exit 0, `picross-difficulty-activation-plan-v1` | nur neuer externer Plan |
| `activation-adopt` | Exit 0, `activated` | nur Defaultdatei |
| `activation-noop` | Exit 0, `no-op` | keine, vollständige Dateiinvarianz |

Alle genauen Argumente, UTC-Zeitpunkte, stdout/stderr und getrennten Exitdateien sind archiviert. Rating-No-op vor Aktivierungsplan; Aktivierungs-No-op unmittelbar nach Aktivierung.

## Aktivierungsbindung

Plan-Ergebnishash: `238a4fb0a4b18287f9402b91c3c64bcf81db3d90fc4720e6979e018498158496`. Vollständige 324 Quellpfade auf dem bereits übernommenen Stand. Vorab geprüfte Wirkung ausschließlich `content/difficulty-method.json`.

```json
{
  "activation_hash": "238a4fb0a4b18287f9402b91c3c64bcf81db3d90fc4720e6979e018498158496",
  "format": "picross-difficulty-default-v1",
  "method": "picross-difficulty-0.4",
  "method_hash": "5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf",
  "previous_record_hash": null,
  "record_hash": "3bce95b5f2c57aca8c3c1c71a5f8f028f40a9a3c2e4e925da5bd0d05924f61b8",
  "revision": 1
}
```

## Getrenntes Selbstreview

SHA-256 von `self-review.json`: `d9bed54d61315c5dd3484b6c38a18c7e1cf1f12b6f5344504db3e5ec04074bc3`.

```json
{
  "accepted_report_hash": "a0d1908573a253978273736e86d66d32fa027068480654f1837d5cd570a46c2a",
  "adopted_ids": 45,
  "all_final_existing_file_stats": 305,
  "all_final_source_bindings": 324,
  "both_freezes_unchanged": true,
  "both_noops_bytes_hashes_mtimes_namespaces": true,
  "checked_utc": "2026-10-26T00:35:31.734196+00:00",
  "data_delta_paths": 49,
  "default_revision": 1,
  "durable_report": "exact accepted result, operation.phase adopted",
  "existing_data_files_modified": 46,
  "journal_remaining": false,
  "new_analysis_solver_runs": 0,
  "new_data_files": 3,
  "observed_adoption_journal": "exact old/new/retained source bindings and 48-path delta",
  "old_work_evidence": "unchanged",
  "rating_revisions": 2,
  "runtime_delta": "v4 to v5 and only difficulty per entry; categories and other fields unchanged",
  "scope": "separate self-review; not independent SD2-D-R01",
  "source_tool_commit": "4e23e644f3457362e02b75f78fdb575a99265494",
  "start_head": "44a70dc491dc37d78f98382f957ee88205f26743",
  "status": "passed",
  "unchanged_existing_source_files": 256
}
```

## Vollständiges Ratingdelta

Alle Methoden wechseln 0.3→0.4, Ratingrevision 1→2. Definitionen, Rätselrevisionen und Matrixhashes bleiben gleich. Jede neue Vorgängerbindung entspricht exakt dem alten Recordhash.

| ID | Alt → Neu | Alter Recordhash | Neuer Recordhash |
| --- | --- | --- | --- |
| pz-00f37200bcee4d548e2c910ce551d077 | L3 → L3 | `0da18cd2e6f345669cef33e6ed119cb14c3209b908bb9dbfdbafa3ad865ed000` | `96217c342f9a634d5a360dcbb41405993dcbac7582fd68929528843150dce04f` |
| pz-023b50b44d1c4698a6e17e65b6ea4337 | L3 → L4 | `17df954421cfaa7293d92666d30d4fcc78a43afdf35be3af3973ca956d7c5112` | `b1cf1a965cb802d11fb802bebaaeb0a1eb0f1e66d9e1aa2a971e29679db08c7f` |
| pz-1b7bf32b1fa140918c0692c90d998752 | L3 → L4 | `347a137f45445b2a1ddf9d6e496c78a5df598ae34115c8b14d204bfd26124c7a` | `76c31c9e191e292c62368ea5dce018cfbec69308d475540708752d48bbf50261` |
| pz-1e9cdac1f83a49d5982f93ded09e58de | L4 → L4 | `7b899df69412a12ef83fb1acc16a4336a2834294f6c75ad405eda517441b0b75` | `596d129bf4c5e0ce7e0e3f176b29363d8998041e70ddefdee83857084a20622f` |
| pz-20219e14dbe242689b9ef06297828f34 | L3 → L2 | `a42b32be94bdbc3e5c1078d77400c677c7ed4c1fa94bb0cfe1c9887033b726b8` | `c4bd5184e0cbede7b2a891713d8bbc7795672c55bfab94a49c24ac8749a44ae2` |
| pz-25d245061b0c49c190788de8e5d0e45b | L4 → L4 | `0d0d5dff685002ca6434ab3cb130c916aa9bd0b704a9915dc99ba7c38db1836a` | `cad9d91e562de469c1f8ccf955e5d090dfce1439b71d6a24d17474b3df9e8954` |
| pz-2a8481f61e6443bda174bd3da67c | L3 → L2 | `e1ef816d86d633f121dc16a1c87d2b4becf7c23ff02701de6ed0ed3979a7875f` | `591e2722e3af8c5a05907da3ada14710928db2e8069dcabaad935eccab7d2329` |
| pz-3a744ae1b7cb4d38b0ac29d030ef | L4 → L4 | `c3ace97f5fb51742507388810672d71096f0a3ad20f45f52d11ad3a56842cc3e` | `0da14a0ef6d89c53abdd3934624e617d3eaa9444567ef0e0d745ab48ab166bca` |
| pz-3e97c042f0bf474e8608a84ea034c246 | L4 → L4 | `77ce3908faa280ddf8d8b2a1a34fa6241328d45c5bcb494609b642225ccfc6a8` | `601ae10e2b7dfc1a9151a71887244e21b89df1eddc01bcdd3dedae98196107ab` |
| pz-49a9e539419b48119e8f5f506fcf6dc7 | L3 → L3 | `fe0779cf9c2227a640b90f59b2878c6c56ad4f7ddebd768339e38441535bee60` | `a4be41935e3d64632a74a83264aeedd491bba1fabb07b1874627bb321d9b7049` |
| pz-51405ea1ad194507a60c9b6701d802f0 | L4 → L4 | `a1e04397807f89cc5c4eca656083417e2aa41298d257e6b4095c528b4e2d0477` | `2d4d91b768061094dc2c413745da010de31113723f81be383b49ea6a56f0a601` |
| pz-5ad1e06e19ab475baebc582d4999daa5 | L3 → L2 | `b8efdc20c47ebdc98f97b9c6d0d5cc2b3571ee1b54e711b70f7b23ae9a46ec43` | `0e3d4cbcac0cb1a5558090cd1af51237629593173d4aea23db2dd1b73571acfe` |
| pz-6d980b0285604e22b8ecfce205aa008b | L3 → L1 | `8fb1f8dda4c6539ea92f172895186368b1792c954f9478c081ec0cc2a8503258` | `82e75d3e3f7674a98de12cc51c6753537f54ee14a8827d67d9df01a51ba36be0` |
| pz-72561c715dd741f9b0082c7ad24802c1 | L3 → L1 | `e5f23fe78b521409ba9956d5648b29537c5b27ab6fd6d07549966bc4b4248f30` | `eeb1de263ea6cb665754e953262968784696ff9028d98283be693e33257782f4` |
| pz-72eb9b188896440c8a9a833e803835ec | L4 → L4 | `b585b11603b1a201e71a0182071f50ec2c3374caa81160651dc5481c118b7053` | `0f0b2f6289dd06d1483104ff30a58449aa995d1824c5ef419693dcee86183a44` |
| pz-7635c2e042e349fc90ad9ae55681de0f | L3 → L3 | `1e8ef887096446b4c93e7b295b53de85ff4285fb9c93382b3eb7d437479b89a4` | `43a40c0a6e3c01da2a8b7d12c8735836be13c32432aa6a3379b8d5e72644dab3` |
| pz-7ec3dcd94bf84e698691ef4b5839 | L3 → L1 | `265f0cea55a73ee29bfe36efd5b8d43bc8ccc72595a6b861917791e5a713949d` | `a5cf441d8ac49268c112351d29d0fdec38ef6a087c86ab0371299c794613985a` |
| pz-82758295d5d34284bbae2716f64f | L3 → L2 | `b4b283a49f31597f77698318e5fb2e01f647fcf044f762291660cb0380cb4b12` | `2dbcf591823dd907b8292f6cfd14a90069c9b09c346e7330c4a9dc20d74a7315` |
| pz-86d1d588a88a46e6ac1285f0097afbca | L3 → L4 | `190134af5f7ad02e232d7a539ed368a34608632f26d3256ba6908674619d5d49` | `e2c49d5157a7f3b0f4d55915f93ed5c6382f62b11d5964e19829fcc3a931a715` |
| pz-87bf2975c82540a399a3d0c7fa180a25 | L5 → L5 | `cc6725a636c58f6cdcd3ee03e8dbd321a5a10ab1ffd5806c51068b3ea61198b8` | `848b336fb9122165b0f0db2165d4ce6f7b483faec4a8600c46c63decf8bd2f3e` |
| pz-8ea7f3dacdcc428a9fcff7a735bc | L3 → L4 | `4e4d7df8532d7e6f6c8c8da5f14475ace8edfce69fb7bcd8622f8dd26d82a92f` | `f9a3fbe98e920caa9c96609998e5bee2b678f7cb4c19f4da87c74cfaa86db8ef` |
| pz-8ecddf77e80c4543bf4ec714fe3d | L3 → L4 | `316ab583f92c21b7cd7af0f3a1a8a9d3af5124ad9a2c60470f2b69f7bf3bb6aa` | `4b3396e84a35cf768aa0ed8254056eb43e9311b2b97c506b5e8237d745121cf2` |
| pz-985d36c1634644fbb2c8a0bf7de3aa9f | L3 → L2 | `0316a542f5b5f1e9fde71c4a0ab824c3f35b4b5a68ed2d5375af2fa521ac43e2` | `1c17628088d5bbe44782ede34011447063702267c7981867c58ef7e0f3abd737` |
| pz-9a79befc7a834e2d9d5896a477328962 | L3 → L4 | `035cf8a98d619ea92d957b8962715c47db39bbb6d958bfd5c818a5dc011b7337` | `36374c5163475ab33bb536d8a7df049ef8aa8b5540c1a01c6f992fe2189528ac` |
| pz-9be288b9b5104da88fc8464184647ae7 | L5 → L5 | `a2cb31b3b91e15841dc2963ef64f86096a8baf0c22a8c6d2a501f760f184b7ac` | `8bdef7fe84dc0f5af90c04374c7991afaadae70de0e8d90c147d752d00989651` |
| pz-9d08697a30c749258b742ac979de9def | L3 → L3 | `036955abd9a3a4c183ef05630770c351ccec37943ece06516356d134948891e9` | `605a136f4de504ee33a60d90ef98d88b9b3160c234e5835364b8d81904c6a905` |
| pz-9f7c59054ebb4f3f861e2bce3034320e | L3 → L2 | `85ed91f058db340b1519c183b96845b63568e82fa593a8aee5c30c26e9b57057` | `c1c02f41ec533ac9544fc1ac5cf7fbd4fa7049be2bdd163816df89757cb97a01` |
| pz-a13368590b744814915eb722f5b2c5f2 | L3 → L4 | `29beb166a2c161e2fe44be1a71290f95e25594b111743606f8a74744d94e7a4d` | `1b66779735c5ad99f7b5ce51a40eef01ed9601ba7c7d02394bdcbda631ec54a7` |
| pz-a358a1bf1b994efcbebeb55abf825789 | L3 → L2 | `37536f351cb8c701b9005619e4c8454ea9c30b1f57c3fe2a53fdb74e42316879` | `5e5beed5c1cb6ff937fc275162b56c33da353ee87a8df97a2003f0157b7df46e` |
| pz-ad7164c2302a42e5953f6779a1c7 | L4 → L4 | `8a00800a11e026864ed9a044a8a5a98f3cc4108808618e1a0fa3b2c34b7fe985` | `f1e36f3cca6b93d5baa82b62339d0c14155ac9347243882522d289b80eb81ce7` |
| pz-b180c25084a34b019f35ad2244f03c24 | L3 → L4 | `bcfcf0feefaebd86a521cc62f32a23eae5eb07786d7d9060bd3a80e1d46f2405` | `f3e1ba069f1db9f3bd40318ce230c7037f930980c9897af1433eea7ee19b0c91` |
| pz-b3368aea28ac4a11bf09e0dc9c48 | L3 → L4 | `44d8f3e6e52d9992cfc3c0f3c8b3358a7cd90786ece76e6c8538cd59d72617f1` | `0f67ac323d969e94c4357aa6239b12f5257040e56bca8477a4f0ac371d93857b` |
| pz-b5e2302bf71445c09caac76bbc2a7075 | L4 → L4 | `e85e1f66276dedf1441615c8ddcb0fe6c04870af28eee5ee14e1d0752e88cce1` | `85de5a6da96707abed3edb4b0be128cfb5708553c4310b7fde70b7691b0552ca` |
| pz-b6f94e528b48444985d0561cb48a5bc7 | L3 → L3 | `5ccfcb3461597e8c8d90c4d56edc599b22ddaf3b63a7625ac975fb08b4aeda5f` | `5311226f7f83e84d95f5ef28143bd7c2956497854b7495cafcf566c06128ae5b` |
| pz-bd2783fcd3eb428c933d15259961cfcd | L4 → L4 | `137a023952732f83623b73cc137e44455ce39234c7042047d6fd1e6f656580af` | `0b972ed88e4c145ef0bae427c7fa8fe15130115ed3322a902e07c9b15b50d9da` |
| pz-c71563f1b8c940de998afdd62f09 | L4 → L4 | `d6cb0f92f36b8fb623203b6d59d44f39905bf9428f5b560136bcb9cb90bf3930` | `d92679e737b4bf4c8f00bfa193eecb464c4985d24bbb17356b9b0c3fb6ec2c3b` |
| pz-d6cb06cb41854b1da84f0ba2f043aa14 | L3 → L4 | `42f11c25385dd9c806938137302bd148aeb1ee94e5ed803b1c138ddd13a3377b` | `cb6bba8874e5b7754a11a30b380e719c1326fcff4c1f3a14b0bc9bc7aba751d3` |
| pz-d7e68d1138a3448c8b2a4b07e8632350 | L5 → L5 | `fb2c8d19afb65a43f93995a54879ed64f1e186df0c6bef53f2c45f8bc8e2d3ba` | `a18a1547f23e1c7656da9999953a6c833c0b0d25aca581a04e48fc8f5f9f1f1e` |
| pz-d829eb9b83e94f9c9357ee5ab9c9e359 | L3 → L4 | `24078730489ee91c66eef4a0e8f63c64af1dab535adf809b23e6084503f46519` | `f98f560442838ebfcce494f41945ed702b41d67c86804de010a1d8a89d4d0adb` |
| pz-dad34b8331914c909e8ded79491dac94 | L3 → L4 | `18644bc7a79c0fe83301c3da2ca3557c9bf295c20b9809c5f5cac2fc83d01c10` | `e7ff3aec5010aaff6410d73c41cee02c53c0e6b3c7ceceb8930a986cd134b7da` |
| pz-dbbebc72556d4f0c9a37ab69275480e9 | L3 → L4 | `2bb9d66ea487e4bb4acb0f6e16a3e184f3252227b49cddca703349d2619d1a89` | `cc0b7fa2434a28c305c407925d965205c14d2d3decf001669591b1756727227b` |
| pz-e2e5092925ce4821a9219be7816b5931 | L3 → L1 | `207a38bdad749f358343c5fda3e58c056be701922aa6f1855b47e70f0e8db237` | `7164b28c980190fe7652916c473cf47d7f22fadd500f927141da4ab1978995ea` |
| pz-e45e2e0d67a34f6aa8368f477454 | L3 → L2 | `495cbce8348732c8dd331c3e60f22390228aa92130b766d530ba95b33ed7e583` | `15e701ebff14c4559df0575ddb14bcf0dec7200eef25e6bcfd46838590141d43` |
| pz-eedd1fe72af54714908d5b5aff34 | L3 → L3 | `604e6be5314c58d5043218adb9209bb16b0a7c86b470142247c42493f4985e0a` | `226fa120c63203fe67e4cae56dd4c9ccd27be42a4f8d8987937d6ba4f773c2f7` |
| pz-f68e79ef419a4322b68d06817b39330d | L3 → L2 | `08c9b21b00d08001968ee9e061903021b07e48d552795db4e95347d1c5e961b6` | `cdae26d1159e8e0664c90752512feadf7cb2afd557c668952bbbaab2b1cb4387` |

## Vollständiges Dateimanifest

| Relativer Pfad | Bytes | SHA-256 |
| --- | --- | --- |
| `README.txt` | 1224 | `48c950da0bf1eff606d8a0357d62112b66af9c6ed4eb355c0a499bac68179470` |
| `activation-adopt-command.json` | 312 | `1eeefde64f333e5b36852dd69c88e1590a6e94c84e7865080f2b5cad2c9cfa2b` |
| `activation-adopt-exit.json` | 63 | `b199dae2ab4ed2dc2b5dbd60b9064afab3b04a9783d2f0982e369466f07da74c` |
| `activation-adopt-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `activation-adopt-stdout.json` | 144 | `c6f552c3fbf26ce665a4db39fa5d697b0294d272f848efad02c6ad32cd7f9529` |
| `activation-noop-command.json` | 312 | `8b6b6c0d4673a01fb9c2244b79787ac2bcabdf46a8702f2a434a82c89683ca17` |
| `activation-noop-exit.json` | 63 | `a196a59e05d4ee85809f08647b8c3db577722c83ad2cc8c679b5d6df8a5c7759` |
| `activation-noop-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `activation-noop-stdout.json` | 57 | `6b1c1393b5d2a497dc2c289e9489caae72b3e055c0b36978aa583ded72eb5d1b` |
| `activation-plan-command.json` | 491 | `e024cf57f2f709a478227a5e694139fe621d07b09bdd5d993d903f0174622a13` |
| `activation-plan-exit.json` | 63 | `215117bc2a390a9e508ed165c638a39b30b4126962298cc2007b998f02fc4c1e` |
| `activation-plan-review.json` | 597 | `1bf0bcbbae5e25ced2310888fbc923f841935ac15e1ab68bb93088ae3333378a` |
| `activation-plan-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `activation-plan-stdout.json` | 38541 | `d31661472c2cd461a1438890c7508ea2187db799956f14a219207266e35e5a78` |
| `activation-plan.json` | 37874 | `66f47cfc0b6bffd2e7e0623ff8851be3981ba148406d788d0abda038373490d2` |
| `after-activation-noop.json` | 101622 | `dcbb96efb0999c8537aafde198707ac354be6aab1f855eb5e4ea4a119049fb0e` |
| `after-activation.json` | 101622 | `2352deeb59233db0ffbc03c70dc36a6cdf795b53425485f09d90a95edf5916ef` |
| `after-adoption.json` | 101344 | `a2a4116a31413681154a6e189b61be6f81eab99dbffbaa8a18690bc5d7088b40` |
| `after-files/content/difficulty-method.json` | 365 | `215f544dc4e6b02fa7fa87031d9d6db8a95f32cc38dfd5c68c98476510aea8a2` |
| `after-files/content/difficulty/pz-00f37200bcee4d548e2c910ce551d077/rating.json` | 4100 | `24c7af17f72032db8f21d0dea46588cce4e0f479abd9adc3da52e1c2094d54e6` |
| `after-files/content/difficulty/pz-023b50b44d1c4698a6e17e65b6ea4337/rating.json` | 4132 | `0b38b896f59abd52ff71d92c356a28d8d72b861e353df80fe77d067d50989ca9` |
| `after-files/content/difficulty/pz-1b7bf32b1fa140918c0692c90d998752/rating.json` | 4130 | `ab7b17b5c4d2d42a74876d070d747cd7fba524ddf56f1541379791970c8677bc` |
| `after-files/content/difficulty/pz-1e9cdac1f83a49d5982f93ded09e58de/rating.json` | 4088 | `e89b2934f19095e54405911062d946329365bc3302a2b347f33a52d342850b55` |
| `after-files/content/difficulty/pz-20219e14dbe242689b9ef06297828f34/rating.json` | 4068 | `fc0547b985536996d727be88cabf4bef66fda4494e4909ade5efe0e141647758` |
| `after-files/content/difficulty/pz-25d245061b0c49c190788de8e5d0e45b/rating.json` | 4150 | `1d2ef336341f50a3cbe35b0205276ebd0e3390d0c3fdf5722e6cc5c92cfcd0d3` |
| `after-files/content/difficulty/pz-2a8481f61e6443bda174bd3da67c/rating.json` | 4126 | `49a4f30ca75767c7e8652b860d77b7ec0300c0429bf1aee2b627c32412ee98a5` |
| `after-files/content/difficulty/pz-3a744ae1b7cb4d38b0ac29d030ef/rating.json` | 4182 | `08f5596abf74f0a47ca8b9846fed38a8aec439d92d41d12a3d678eedbd686539` |
| `after-files/content/difficulty/pz-3e97c042f0bf474e8608a84ea034c246/rating.json` | 4136 | `96d150ddd9cd0eb7eacfdf39e66aca490ef13a5b8c5c6daae58a643c0e2e06e9` |
| `after-files/content/difficulty/pz-49a9e539419b48119e8f5f506fcf6dc7/rating.json` | 4052 | `5aa7de2bfe0268c9f7d3387268916ad115ff9a102d2ab8dedf6928554ef25150` |
| `after-files/content/difficulty/pz-51405ea1ad194507a60c9b6701d802f0/rating.json` | 4156 | `0e419e0ba16d79d1220d930fe630142f51a8e9e2cc9a652e9b526a885ca8aa44` |
| `after-files/content/difficulty/pz-5ad1e06e19ab475baebc582d4999daa5/rating.json` | 4069 | `7ce60140dd5bd38e5fb676331e7a02f8c3c0510da13fd9e508083544e634b39a` |
| `after-files/content/difficulty/pz-6d980b0285604e22b8ecfce205aa008b/rating.json` | 4037 | `4b85af2f7ecf166b72b92582cf6fea2522d9f21962f26cc27622a1d60045ea49` |
| `after-files/content/difficulty/pz-72561c715dd741f9b0082c7ad24802c1/rating.json` | 4087 | `135638ff9685c77ac90447c67b8a4240be7666e4f5c0ed70fb78dad79bda99ac` |
| `after-files/content/difficulty/pz-72eb9b188896440c8a9a833e803835ec/rating.json` | 4075 | `cb176868d5d5b8a3533076b2cfd4444079fd57ddf07d6983678629d8daeaa070` |
| `after-files/content/difficulty/pz-7635c2e042e349fc90ad9ae55681de0f/rating.json` | 4078 | `70de247a13587514bc79bb5dd26c0f527e83c6b8398158ae14f68565c821c4c5` |
| `after-files/content/difficulty/pz-7ec3dcd94bf84e698691ef4b5839/rating.json` | 4089 | `cc679314239d6b6461e083de5f43bfe6fe634cdb74a296d895ef510fec067477` |
| `after-files/content/difficulty/pz-82758295d5d34284bbae2716f64f/rating.json` | 4157 | `73e0a735fe6fb120e385e28ace1ca07f86eeca352c6cb5885284d12cef3e59c0` |
| `after-files/content/difficulty/pz-86d1d588a88a46e6ac1285f0097afbca/rating.json` | 4103 | `0d54401e7d5cbfbd473421dab18df2fa63a8703c7ffd03e6e71fe527afa425d0` |
| `after-files/content/difficulty/pz-87bf2975c82540a399a3d0c7fa180a25/rating.json` | 4598 | `3d42087db6f3981c951a6e1e5b5a54fa813898b3f40f5e431573cfc1514c48e7` |
| `after-files/content/difficulty/pz-8ea7f3dacdcc428a9fcff7a735bc/rating.json` | 4112 | `280644dc846503369171e8ab2438f70ab9fc082733cf37a65ef1a3de591ce207` |
| `after-files/content/difficulty/pz-8ecddf77e80c4543bf4ec714fe3d/rating.json` | 4088 | `be3408d4d63317027356bb534590bfcdb87c30229f2400b03be07abc72b7c178` |
| `after-files/content/difficulty/pz-985d36c1634644fbb2c8a0bf7de3aa9f/rating.json` | 4116 | `3eafa47daf7063cb0627e05840e35adccd3ad49467d2138a230e1557b66c0f09` |
| `after-files/content/difficulty/pz-9a79befc7a834e2d9d5896a477328962/rating.json` | 4110 | `9582fca58bdb84390bf073b4992a69550c2d4cf0731766c74e114040c452a368` |
| `after-files/content/difficulty/pz-9be288b9b5104da88fc8464184647ae7/rating.json` | 4594 | `d7dfde658fbf75d69006d744d48cb38486cb6824f25a679bdb107a72955c8d79` |
| `after-files/content/difficulty/pz-9d08697a30c749258b742ac979de9def/rating.json` | 4176 | `fd8b67929952ce504cb6bc3aa40898dce9546d13d5e3f609e4541e27de680a58` |
| `after-files/content/difficulty/pz-9f7c59054ebb4f3f861e2bce3034320e/rating.json` | 4136 | `3efd11b41675291c099a587c9a767f34d4e10ae3b3570441828b9038555c4133` |
| `after-files/content/difficulty/pz-a13368590b744814915eb722f5b2c5f2/rating.json` | 4142 | `9fdd5ea81d61d774523b74a77a785e360945a8939ab2e0138465baca3bdadca3` |
| `after-files/content/difficulty/pz-a358a1bf1b994efcbebeb55abf825789/rating.json` | 4053 | `6e9cbbebcd57e7c374bc6edb7608a280b78e7fb73033a14aaf27679b347fac59` |
| `after-files/content/difficulty/pz-ad7164c2302a42e5953f6779a1c7/rating.json` | 4138 | `652aaf0a456d6ef109f0d84e4ef2e16efe4e2d61d0bbf5755bad82ce2b5b06b7` |
| `after-files/content/difficulty/pz-b180c25084a34b019f35ad2244f03c24/rating.json` | 4230 | `45bae2d5e0d28f253f71371c6abb1855bfb1aa590cc856bd25365d4b9d91b3ac` |
| `after-files/content/difficulty/pz-b3368aea28ac4a11bf09e0dc9c48/rating.json` | 4086 | `bd0fc8479567657c301dd791996933a7573ab78863a8e39090b50c6f5e207533` |
| `after-files/content/difficulty/pz-b5e2302bf71445c09caac76bbc2a7075/rating.json` | 4145 | `fa23431bfd3584c69c4a28560fc241147d77ef6e99a2f970415b4f0c5b99f75e` |
| `after-files/content/difficulty/pz-b6f94e528b48444985d0561cb48a5bc7/rating.json` | 4019 | `8a9bb5346097c16ec59c1e3a766931bb957187378fb391dd7c32d1193ff6f2c5` |
| `after-files/content/difficulty/pz-bd2783fcd3eb428c933d15259961cfcd/rating.json` | 4174 | `31ddb06601631545706e903e4a684e393efd080a403a20b957cc111d3b570ce3` |
| `after-files/content/difficulty/pz-c71563f1b8c940de998afdd62f09/rating.json` | 4072 | `6609f22a7835b824965f77d6ffc5a8d4a716a19d947b7ffc79964f15fd830087` |
| `after-files/content/difficulty/pz-d6cb06cb41854b1da84f0ba2f043aa14/rating.json` | 4136 | `9c5b24d153caea4408f01e197506c136cc9e821a50ed3b9d3ddb4ef110fe7608` |
| `after-files/content/difficulty/pz-d7e68d1138a3448c8b2a4b07e8632350/rating.json` | 4061 | `ae11f0d63eed9cb2f0ffe4a0f644acaec7e00fbd0b585ee7ddfe495f0d4f3174` |
| `after-files/content/difficulty/pz-d829eb9b83e94f9c9357ee5ab9c9e359/rating.json` | 4150 | `29e2b8b0a3b1e43cf7a30998ab1df32cf8ffb8567efd3a0503204e54d17fdbb2` |
| `after-files/content/difficulty/pz-dad34b8331914c909e8ded79491dac94/rating.json` | 4150 | `4ad4ad25daae68a8635c2f32649de3e7d87e7b9f4ae3079fd7d79083aaff36e1` |
| `after-files/content/difficulty/pz-dbbebc72556d4f0c9a37ab69275480e9/rating.json` | 4123 | `5bf551d931672a8f4ac5a7de00030267ce1a9f49035e76bdb5649445afb0d9d2` |
| `after-files/content/difficulty/pz-e2e5092925ce4821a9219be7816b5931/rating.json` | 4033 | `9663ed9fba9627ad112b47e68e2c9ecf507ed1c12d69b65ae0e26ab16cb97f60` |
| `after-files/content/difficulty/pz-e45e2e0d67a34f6aa8368f477454/rating.json` | 4154 | `9d29cc4272e7962e0a00f553a9bceb97d57c3da391746be327b1884a6d0a589d` |
| `after-files/content/difficulty/pz-eedd1fe72af54714908d5b5aff34/rating.json` | 4089 | `84a503119a49b00a11c220d2dbe61f7142c54d6ba7a0c48984c777e510b4bcf0` |
| `after-files/content/difficulty/pz-f68e79ef419a4322b68d06817b39330d/rating.json` | 4029 | `52c54fde8de7e9e663cd6fa49055cf52e60a326ea184863a3b38aea8c2706c86` |
| `after-files/content/difficulty/reports/sd2-d-20261026-om01/report.json` | 107863 | `94e41931fa0bb691c796d8f322e353671448cda84aa48d5246a889753cc93ddc` |
| `after-files/content/difficulty/reports/sd2-d-20261026-om01/report.md` | 88618 | `80029e1787240b9bed1c9ef8f69c60533f3a013d151e21a3014cce657e863415` |
| `after-files/game/data/registry.json` | 21692 | `978d860133450d4d560f36f8993df085b4878498f97138041b1e1a4c09a363e0` |
| `after-rating-noop.json` | 101344 | `11337a77ce587a9d9580bd1b47f09a6ea674d00568f7971dbed0aa2b5003da25` |
| `audit_f01.py` | 7057 | `97a76b42955252bbf2aa555b927b1271c36f58e0f82bea66d1a5a6c4d52f31fc` |
| `before-files/content/difficulty/pz-00f37200bcee4d548e2c910ce551d077/rating.json` | 5746 | `1996934d9b1c38ae5d1953569f3711368e81397ea1bc3df457986e78d9004818` |
| `before-files/content/difficulty/pz-023b50b44d1c4698a6e17e65b6ea4337/rating.json` | 5875 | `5838d557b9bbd1bbdf268ed2cb962a6bfa629232c1431afa6686399de7725634` |
| `before-files/content/difficulty/pz-1b7bf32b1fa140918c0692c90d998752/rating.json` | 5765 | `5830a0dfe6756809812aae0abb8ca62a81b8340a41796167c92a16b2f6adc643` |
| `before-files/content/difficulty/pz-1e9cdac1f83a49d5982f93ded09e58de/rating.json` | 5738 | `de2966818b512578a30ba688dbace16cc7864e873a40c73d03967e69a342c02c` |
| `before-files/content/difficulty/pz-20219e14dbe242689b9ef06297828f34/rating.json` | 5849 | `f877ad1e4cab086624b2d73a7b5ad021bbe09085c9aace15ba4ccfac55ff3b15` |
| `before-files/content/difficulty/pz-25d245061b0c49c190788de8e5d0e45b/rating.json` | 5858 | `f8940531355db681fa5a3e7f3864bd4adbefe243c04626b27ab817fe2ef3b926` |
| `before-files/content/difficulty/pz-2a8481f61e6443bda174bd3da67c/rating.json` | 5852 | `f01dabf986a67287c5e0881211b3b4f3b7287a5fa045fbd172c5099efd3a9d58` |
| `before-files/content/difficulty/pz-3a744ae1b7cb4d38b0ac29d030ef/rating.json` | 5865 | `bc69ff3748fdb6ab721b3ed3988b684a53fb3df5d3c28c86e1d94af3e708a39e` |
| `before-files/content/difficulty/pz-3e97c042f0bf474e8608a84ea034c246/rating.json` | 5860 | `4e1e7dde8d4a566505deece0a93f1f06516722d60c5ba71963fc4a55e482990a` |
| `before-files/content/difficulty/pz-49a9e539419b48119e8f5f506fcf6dc7/rating.json` | 5728 | `e878e6187518c549b955d74579348e8d908947a59e8bc19123dea17c1e884e5d` |
| `before-files/content/difficulty/pz-51405ea1ad194507a60c9b6701d802f0/rating.json` | 5850 | `6155ddefc9f3ed55e6fbe654bb840ca914cb90e4cbe5bcc8b83f3294584ff9ab` |
| `before-files/content/difficulty/pz-5ad1e06e19ab475baebc582d4999daa5/rating.json` | 5847 | `40e3471c2774e932f42d6b7538eb4c1414df2a498892082c7824964fc3bf0bcb` |
| `before-files/content/difficulty/pz-6d980b0285604e22b8ecfce205aa008b/rating.json` | 5736 | `051e18b6ddf290812f575a08008533af68180e97e8aeb0c256538bc9596d0f5a` |
| `before-files/content/difficulty/pz-72561c715dd741f9b0082c7ad24802c1/rating.json` | 5866 | `6d0844d0dccc6940980593ad30caa6b4a840e18d56d99d3d99aa4c5a019e848e` |
| `before-files/content/difficulty/pz-72eb9b188896440c8a9a833e803835ec/rating.json` | 5867 | `ddaece71bd6227f645ab6a66e5b8d430822088a1bcc44ab4c8778687baf3adea` |
| `before-files/content/difficulty/pz-7635c2e042e349fc90ad9ae55681de0f/rating.json` | 5738 | `e747c74165121778aa28e9eb0108c8905155aef9ce5807a5df03a000feb0e890` |
| `before-files/content/difficulty/pz-7ec3dcd94bf84e698691ef4b5839/rating.json` | 5844 | `fb73914af581c5b6bbf5c770427aa5268f775586aa491b8f358d45f2762db70f` |
| `before-files/content/difficulty/pz-82758295d5d34284bbae2716f64f/rating.json` | 5847 | `3b8b935a16aa3b19df4f16d6a72d351eb44b5abe6aa8f51d83d82d1e0cc1b53f` |
| `before-files/content/difficulty/pz-86d1d588a88a46e6ac1285f0097afbca/rating.json` | 5744 | `b2bb615f3d1e7f9d77149b97bd5009435a0578e3e553e28482441f105e6a667a` |
| `before-files/content/difficulty/pz-87bf2975c82540a399a3d0c7fa180a25/rating.json` | 6121 | `d4c47a1ec805003320ee0cf06267c260d078f7821de2ecc78181d638f28a40a4` |
| `before-files/content/difficulty/pz-8ea7f3dacdcc428a9fcff7a735bc/rating.json` | 5865 | `daf025336617dcc34a9477947845f92db09e748153cefed0a2e7e5a9ac4d0fb2` |
| `before-files/content/difficulty/pz-8ecddf77e80c4543bf4ec714fe3d/rating.json` | 5860 | `908149f92a5b0479d350be5d83d734cbbced134cb96a71294f9312ce147a074b` |
| `before-files/content/difficulty/pz-985d36c1634644fbb2c8a0bf7de3aa9f/rating.json` | 5849 | `b8c674551796a70a04413d9a12baab84996de49495b16ace72b73b15919d65f7` |
| `before-files/content/difficulty/pz-9a79befc7a834e2d9d5896a477328962/rating.json` | 5859 | `752eb8224f0d1aa45a65e11f2e2686773564243e13956a10d9ab05f1e3f1af80` |
| `before-files/content/difficulty/pz-9be288b9b5104da88fc8464184647ae7/rating.json` | 6147 | `6c643bbac2f79aedd115cf32518ac9e52dabaa309432d0f761f1eee1be247413` |
| `before-files/content/difficulty/pz-9d08697a30c749258b742ac979de9def/rating.json` | 5756 | `cc69bb7670e00c5162e6135eb3e1a958947ed59f296c2ffe890f620860a7eb25` |
| `before-files/content/difficulty/pz-9f7c59054ebb4f3f861e2bce3034320e/rating.json` | 5757 | `84f8facf54e989614e3922510db82c266522f9c081f5a863cf81228b3e3bf222` |
| `before-files/content/difficulty/pz-a13368590b744814915eb722f5b2c5f2/rating.json` | 5769 | `fa90f2cca619121558d639c163b98c4ff1ded3f2df9128df8cb6318b821cad47` |
| `before-files/content/difficulty/pz-a358a1bf1b994efcbebeb55abf825789/rating.json` | 5832 | `45ca551045d0ba87226eefde1f00bb47dafa0c88d9cf5e5f826b870704d92bfa` |
| `before-files/content/difficulty/pz-ad7164c2302a42e5953f6779a1c7/rating.json` | 5849 | `052346f15bfa832330887156b60108da41a9eb206cc20b9a56b8c628582c98d2` |
| `before-files/content/difficulty/pz-b180c25084a34b019f35ad2244f03c24/rating.json` | 5753 | `f1456cfcfaf92b7e95ef1700acb5e514e6073cc1f014b6ed5d502f7bc8131547` |
| `before-files/content/difficulty/pz-b3368aea28ac4a11bf09e0dc9c48/rating.json` | 5839 | `aad17358bb8022066232d54b1675f5c7bfb1b5a306fde3e0356f88d12660f20d` |
| `before-files/content/difficulty/pz-b5e2302bf71445c09caac76bbc2a7075/rating.json` | 5875 | `8ff8a8b032e3d7bf9e6ca7567b71b7a7f019b13f1c59447068e07b5635342ba8` |
| `before-files/content/difficulty/pz-b6f94e528b48444985d0561cb48a5bc7/rating.json` | 5723 | `a2f7706496238da61544d1911d8de351935b2fa2e9dc238206b8d7cc2f713c64` |
| `before-files/content/difficulty/pz-bd2783fcd3eb428c933d15259961cfcd/rating.json` | 5753 | `a681260dfa7be3eb7c69370e7025e559d8fd0695a709b006c6be3ea7efa4351f` |
| `before-files/content/difficulty/pz-c71563f1b8c940de998afdd62f09/rating.json` | 5871 | `e7eae7bc202a79cfb2c87d9cf340ec1b022746d5a45e1a86749049a74347be3b` |
| `before-files/content/difficulty/pz-d6cb06cb41854b1da84f0ba2f043aa14/rating.json` | 5756 | `cfbc409719e36cf558ebc6893fbbe966bd8b21f91a1f0c5ff0e7b0b61aabdb85` |
| `before-files/content/difficulty/pz-d7e68d1138a3448c8b2a4b07e8632350/rating.json` | 5866 | `99a1e94b0d088705632073495d3cb4691b50861e245befcec39e3a703041f05b` |
| `before-files/content/difficulty/pz-d829eb9b83e94f9c9357ee5ab9c9e359/rating.json` | 5873 | `9686eec62870eed076ce837750ba495435cdb1212ffadc3d653e43484fd75c5f` |
| `before-files/content/difficulty/pz-dad34b8331914c909e8ded79491dac94/rating.json` | 5768 | `201251d3c6c99a8f1ee4de8686d4d5d8e279caeca0d75ba0c8cb71e08f07a0e2` |
| `before-files/content/difficulty/pz-dbbebc72556d4f0c9a37ab69275480e9/rating.json` | 5857 | `ab7bb936da7cbfcce7f89931bd1427bc7db3764dd52e9580a070148880661461` |
| `before-files/content/difficulty/pz-e2e5092925ce4821a9219be7816b5931/rating.json` | 5733 | `fc2fe75f5b6271031562be7a70e923d8d8973420cbd25a741192404f1d202d9b` |
| `before-files/content/difficulty/pz-e45e2e0d67a34f6aa8368f477454/rating.json` | 5860 | `9382629adeb3a2ec109beeab155f7f4faaf21fefd8651f9faaa8a763c186028c` |
| `before-files/content/difficulty/pz-eedd1fe72af54714908d5b5aff34/rating.json` | 5847 | `72a0946dcb76cb6f46184f860e9ed156ba732e05da6e04983ed5223e4c19caab` |
| `before-files/content/difficulty/pz-f68e79ef419a4322b68d06817b39330d/rating.json` | 5734 | `9c7c773a7aae6907f76f767b921b31b2c6ef203c836b5cc59d537325a40c92fc` |
| `before-files/game/data/registry.json` | 21692 | `3022a6e3eaf04650dcbf1d8fb37af803f5faf201fd72dbb379184de076a02f72` |
| `before.json` | 100603 | `c515a9cdeaa1852577d9f92e7121af59d7bd22d75eea7334a04bc9f01a1a9a45` |
| `binding.json` | 5938 | `10c1f24725a4afa5bbf94302f8dbb4623c4e05bfd1b7075e802602921bcb4959` |
| `local-ci-a-result.json` | 402 | `228f7af2529d6a926ee5e4cf1d46572e956a78ee940d0447cec3ad7a5cfc75ca` |
| `outcome.json` | 7328 | `7bc2ffeec1b27e4ffbc1cdb664353e67fa5ae1f76919c54fb14397032abe84f5` |
| `package_f01.py` | 5954 | `ce885bcfde0006a471f48779bcf7cc39ddd88dcf95c4344d63e0a840b321924c` |
| `per-id-delta.json` | 25559 | `20703f8e383710b4e47561b73a1362a4265222917d8a1614385fe2d6c0cc9c6c` |
| `rating-adopt-command.json` | 306 | `86b4145e1cb364f0293acd429dc79846f67e3a5b813169b0068d603d5c65a640` |
| `rating-adopt-exit.json` | 63 | `fd94123b186c43330a60cca8053dd1979f9f0eaafa2960046caea0262d057dc0` |
| `rating-adopt-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rating-adopt-stdout.json` | 3390 | `37782a6e79a9a89e37c6441faa40664fe179962ac0be27bb618df1c29d53b907` |
| `rating-journal-observed.json` | 2525188 | `f27bc10559d9b5adbd3cc8848cd391c0cd58ac909663fcb3ac1b22756c634dbc` |
| `rating-noop-command.json` | 306 | `5b5f7e780d4ca5d4108da311a7aef7bbcd1c07e456f6d8d6c13b05c996b00514` |
| `rating-noop-exit.json` | 63 | `c95dffd7e12423898e341219b2ba5fb7863e60dfcc72ae1604230f1d863dc6a8` |
| `rating-noop-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rating-noop-stdout.json` | 119 | `4c0ac6250a1146426f72e05111068bbf82f0c753f2add0523a342c677be693de` |
| `run_f01.py` | 7623 | `85fe0a4bae64ee97841fb834daec533c1b393a4075e7ba200b390da6b7364df2` |
| `sd2-d-20261026-om01-full-evidence.zip` | 1468335 | `f641f7b34a1cf495df77bc88b262eb94b34104ad5ab1c652b58f6ea563b69f7d` |
| `self-review.json` | 992 | `d9bed54d61315c5dd3484b6c38a18c7e1cf1f12b6f5344504db3e5ec04074bc3` |
