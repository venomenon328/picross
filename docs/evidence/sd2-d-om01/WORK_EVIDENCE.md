# SD2-D-OM01 · Vollständige Arbeitsbelege und Selbstreview

[Ausführungsbericht](../../SD2_D_OM_FOLLOWUP.md). Lokaler Belegroot: `E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-om01`.

Portables vollständiges Archiv: `E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-om01-full-evidence.zip`.

Archiv-SHA-256: `f641f7b34a1cf495df77bc88b262eb94b34104ad5ab1c652b58f6ea563b69f7d`.

89 Dateien, 1468335 Archivbytes; enthält zusätzlich das vollständige unveränderte V01-ZIP (512 Dateien). Alle ZIP-Einträge nach dem Packen anhand CRC, Größe und SHA-256 zurückgelesen.

Manifest-SHA-256: `bafc2212dca8e64512de8f6fd667248bddd3d1189ab3d09176861a496b08c1ca`.

Das Archiv liegt auf dem gemeinsamen Arbeitsplatz und ist nicht remote hochgeladen. Ein externer Reviewer benötigt dieses Archiv. Im PR liegen Vorschau, Plan, dieser vollständige Index und die kompakte Begründung. V01-ZIP in ein frisches Unterverzeichnis `V01` entpacken; `portable-selection.json` ordnet die 45 Eingänge portabel zu. Alle aktuellen Checked-Dateien liegen außerdem unter `preview/checked`. Alte Ausführungspfade in Befehlen bleiben historische Angaben. Keine Ausführungsskripte erneut starten oder alte Bundles überschreiben.

## Getrennter Selbstreview

SHA-256 von `self-review-audit.json`: `1cf7ff2dd72f6a9c89e1ffe91da8c139779e4c4878eddd0b58381a91a98b1998`.

```json
{
  "all_checked_inputs": 45,
  "all_new_bundle_file_bindings": "passed",
  "both_freezes_unchanged": true,
  "checked_utc": "2026-10-25T23:52:20.968007+00:00",
  "exact_om_score_and_boundaries": "passed",
  "existing_bytes_and_mtimes_unchanged": 302,
  "final_preview_result_hash": "a0d1908573a253978273736e86d66d32fa027068480654f1837d5cd570a46c2a",
  "fresh_pair_attempts": 1,
  "line_prefix_unchanged": true,
  "new_deduction_runs_in_audit": 0,
  "new_sd2_analyses": 1,
  "open_ids": [],
  "planned_paths": 48,
  "rated": 45,
  "recorded_independent_verifier_results": "passed",
  "runtime_default_active_ratings": "unchanged 0.3 / runtime-v4",
  "scope": "separate self-review; not independent VR01",
  "source_bindings": 322,
  "source_commit": "4e23e644f3457362e02b75f78fdb575a99265494",
  "status": "passed",
  "unchanged_prior_checked_and_report_rows": 44,
  "v01_archive_unchanged": true,
  "v01_manifest_files_unchanged": 511
}
```

Die separat im Bericht geführten drei Snapshot-Bindungen wurden beim Packen zusätzlich gegen die vollständige Quellenbindung geprüft. Auditkorrektur und Geltungsgrenze stehen im Bericht und in `README.txt`. Das Audit führt keine Deduktionssuche aus und ersetzt kein unabhängiges Review.

## Dateimanifest

| Relativer Pfad | Bytes | SHA-256 |
| --- | --- | --- |
| `README.txt` | 1192 | `5529f1e7c074dd6e4a285dcc0b4f076eb708f437083ed758fa7cf415244eb3c4` |
| `analyze-command.json` | 1052 | `b91500deab1f9d4bab930418cb9128b061da262646d8eba268b8e9acd679b5ea` |
| `analyze-exit.json` | 63 | `49509f26414d9a3cc49b5ab7a929d20375ae522b5afd1d87b79e845126ca80e9` |
| `analyze-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `analyze-stdout.json` | 4568 | `1016d73d2918c7fe85f573490a9249238f7bfd0df259f4b0206dcc525579ae79` |
| `audit_om01.py` | 7647 | `43c64c40320540099556f00a6e56b503945e2843e410d6a034c81798e34edcf2` |
| `binding.json` | 102554 | `0865905c3ed69bdb4d6bbf2a268432770cced01bd3370567db8e4497152b2bf5` |
| `checked-selection.json` | 11206 | `19fb256a9b23b713addf145a1b85ed9b7139d62506cc2b72466145d5fc8f19d4` |
| `followup-bundle/catalog-context.json` | 427 | `6f17b1e1d8d56e000181511673dfe40cff23ec1a4d165b76876f9cf7ee547a85` |
| `followup-bundle/rating/analysis/input.json` | 5461 | `2021497d6e79578feca61b836986280a54f33e7a91eac06dfe6c970567068912` |
| `followup-bundle/rating/analysis/logic.json` | 4108 | `7d56c7c4d50a4989ced55ab29017da2284527ce735a527a360afdf0411d85d52` |
| `followup-bundle/rating/analysis/r4-baseline.json` | 16203 | `f2d5011080f17a6b7dec48546266c41d85754755290501b014e72d8e1832b828` |
| `followup-bundle/rating/analysis/r4-proof.json` | 78680 | `d740e93a7a975ad7ede1c41924710ef7a60428706062d8d0b70a61fd2427ed62` |
| `followup-bundle/rating/analysis/report.json` | 7696 | `7c3320b5ff721566bae3342165982fb9ff8eb235f619efa92feeb7473ea40998` |
| `followup-bundle/rating/analysis/trace.json` | 8530 | `72a0aa4831e4caab69dcee76e014cc03d98967f2ddca411a72562c91dfc4108d` |
| `followup-bundle/rating/rating.json` | 1728 | `3b454a0406f9060ddc638a45ff976b919837cb6579d3d7ca72179557d6a5f98d` |
| `followup-bundle/rating/report.md` | 750 | `3586e3f95d7b81f25032af8d56c81e64eae722f4cb9515f24db5479f03c95d82` |
| `logic.json` | 4066 | `238641c8bec22fd32bedbc0feb2b01475983d6af508269d8941837e0b7e21ab6` |
| `om-checked.json` | 4335 | `62f802f1c92be4b02fce35dbc417aaa6940157a8698cbf2785af71cb1d8f9e8a` |
| `outcome.json` | 3398 | `3fefabd332545b8d9a59ee791601723b35e56443a20e64722ad5c47c58b8020a` |
| `package_om01.py` | 5831 | `e8dd624dc79a1ca4d554a68d7ce23928a5673f0e25badc328cf98e638994dd4f` |
| `plan-adoption-command.json` | 314 | `8d69e289b279ed78a1d5399dde2dcfd44ae5996a0f0e0c413ddee904f7d83241` |
| `plan-adoption-exit.json` | 63 | `4f3f9d26ab4c2191c4bea4aa7923e362ed491e346bf7415dc5b9d00cfb35e56e` |
| `plan-adoption-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `plan-adoption-stdout.json` | 3399 | `71242d28d08615f9f67ba6347371506df685a26cbc9a0a891153e940c611ae81` |
| `portable-selection.json` | 4906 | `8a833493ae0303b40f3ccd942c613317112651d61e234a4813f787f40d6a9a72` |
| `preview-command.json` | 8373 | `15b6385fca51470f16395e24f51eff7e9fcc783e18170de35836843c7b738f4e` |
| `preview-exit.json` | 63 | `fadd4bcca596f3495827ffe244e93eead58cff971889eee76a6dba2f1b488124` |
| `preview-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `preview-stdout.json` | 113684 | `edd3db0a714e3957f30bbacddd9d0932b51a50446e01f4dfd00c47019d30ee56` |
| `preview/checked/pz-00f37200bcee4d548e2c910ce551d077.json` | 3837 | `60f710d70e886853d7c440764697f84f0e8ee40ce8b68e3f3fe0ef76b2acf530` |
| `preview/checked/pz-023b50b44d1c4698a6e17e65b6ea4337.json` | 3869 | `d55ebf461c8a1af4e4d98d294d00c9127f5e603777bb02e65c038a021f87b637` |
| `preview/checked/pz-1b7bf32b1fa140918c0692c90d998752.json` | 3867 | `6591a4fe5d1cddcf76b8c6752824a39c1a4af361c0c05c2a0ab140d31db695dc` |
| `preview/checked/pz-1e9cdac1f83a49d5982f93ded09e58de.json` | 3825 | `4b97b2c6800109e2bdfb142b1dbf88ef22e3b92f6fc9680e46524597d7013a33` |
| `preview/checked/pz-20219e14dbe242689b9ef06297828f34.json` | 3805 | `0e631e4aabc0f6c8f356caf714c8357dfd6e932c8385034f59758f57b2f8f9af` |
| `preview/checked/pz-25d245061b0c49c190788de8e5d0e45b.json` | 3887 | `eda58f9e539dc94c3053c84bb5d36da2cf494a39c5c3d5a0a5565475747dc6ef` |
| `preview/checked/pz-2a8481f61e6443bda174bd3da67c.json` | 3863 | `0e171ae75e9b911f2b1db8ac14de8b6332c5827a1fb09ce4d564b38a3c584596` |
| `preview/checked/pz-3a744ae1b7cb4d38b0ac29d030ef.json` | 3919 | `18ea96bdf80a4168c22dde06cdc3209c9dac8726ca7e881fde6e83bf749b415d` |
| `preview/checked/pz-3e97c042f0bf474e8608a84ea034c246.json` | 3873 | `9d4c1f7ba1fb7b9d3381088b36deac20a364c7f0ef67fca75bfe316670852eba` |
| `preview/checked/pz-49a9e539419b48119e8f5f506fcf6dc7.json` | 3789 | `f1d85a15b9bc4eabb20200dd9508fa25cee86ab7e1cbe56d05b63c80af1f6242` |
| `preview/checked/pz-51405ea1ad194507a60c9b6701d802f0.json` | 3893 | `8301344a8ab067e02eac099c7cc2a64fd8059dd804d24b1ea9e2c496a9d3c29e` |
| `preview/checked/pz-5ad1e06e19ab475baebc582d4999daa5.json` | 3806 | `a7ae2de361f0ea7039ee7e1286ea5d84ed5e98e1ae5c1e926b0d8624e4235fc9` |
| `preview/checked/pz-6d980b0285604e22b8ecfce205aa008b.json` | 3774 | `cd9e58d0787e41812b4c21a0d8edfa9cf1bd457bc4063cb6235c5edb8050eae5` |
| `preview/checked/pz-72561c715dd741f9b0082c7ad24802c1.json` | 3824 | `b63c4c733c93fe149d65e2f4a2af24721b3acfe6b7803d13c58e07b3dbc7a065` |
| `preview/checked/pz-72eb9b188896440c8a9a833e803835ec.json` | 3812 | `4809361c59196bcde24c52985d38a4bf35682d4b09f61e8cfbe154c00f40fc69` |
| `preview/checked/pz-7635c2e042e349fc90ad9ae55681de0f.json` | 3815 | `695c9fa7a69ce1b35c11213e688d1512bb0a64913d586ed60985fa20b2073684` |
| `preview/checked/pz-7ec3dcd94bf84e698691ef4b5839.json` | 3826 | `2a10a9b1ec95511af12a28ea431c53ac8c96c63b3a6089803beee3cb08530892` |
| `preview/checked/pz-82758295d5d34284bbae2716f64f.json` | 3894 | `e61cad9312227a45cba5bf8923957d2038f16cac7e891f576bac9b912f4674aa` |
| `preview/checked/pz-86d1d588a88a46e6ac1285f0097afbca.json` | 3840 | `1372bc78aa84c7fe07b1f018f30c5cc3bbe80d8f55b4feab279dd654e9d95ec3` |
| `preview/checked/pz-87bf2975c82540a399a3d0c7fa180a25.json` | 4335 | `62f802f1c92be4b02fce35dbc417aaa6940157a8698cbf2785af71cb1d8f9e8a` |
| `preview/checked/pz-8ea7f3dacdcc428a9fcff7a735bc.json` | 3849 | `b1546aadcbb5f5a9d9804700d313109fee2d42e6067867359276b685c471ea0f` |
| `preview/checked/pz-8ecddf77e80c4543bf4ec714fe3d.json` | 3825 | `7ed388b8dfea504835ca4634583e5afb96ea2caf9353562f4f2a20b875705523` |
| `preview/checked/pz-985d36c1634644fbb2c8a0bf7de3aa9f.json` | 3853 | `082f51e43a8c33ea3ad106c26830fbf862bf06b53e6708f4b36654612b7316c8` |
| `preview/checked/pz-9a79befc7a834e2d9d5896a477328962.json` | 3847 | `379b458eea3aafdf5e720cb563571ee487c6d0796ea61e34d50597f52f7457da` |
| `preview/checked/pz-9be288b9b5104da88fc8464184647ae7.json` | 4331 | `d614fdfeb79f9455dc162557872e04726ed0448f6e661eef95cc8fc8df43fc25` |
| `preview/checked/pz-9d08697a30c749258b742ac979de9def.json` | 3913 | `606c915dfd24150a23f1cedc51365b864f83a8601ba158d99b6f55438ee66b59` |
| `preview/checked/pz-9f7c59054ebb4f3f861e2bce3034320e.json` | 3873 | `60ba4f2f83d4d3bf2598fe4fb6faf79ceb4acdb37b4aed0f433e27d9c31b2b8f` |
| `preview/checked/pz-a13368590b744814915eb722f5b2c5f2.json` | 3879 | `19d486302ac9f2a21999298133527776258b15be900a91cbb96dcf55c1fa7ffb` |
| `preview/checked/pz-a358a1bf1b994efcbebeb55abf825789.json` | 3790 | `af9bed85b84be0309e41018ca4afb35d53b3954897334f521406bd8528e340f6` |
| `preview/checked/pz-ad7164c2302a42e5953f6779a1c7.json` | 3875 | `a93e4462284549fe3cd7df835afec6e4420d380a606c4eb3cab9bb6f6013a12a` |
| `preview/checked/pz-b180c25084a34b019f35ad2244f03c24.json` | 3967 | `c5149b987170fb20b29b67964017c69e1ae86ed31910acd7f28f6711fc30912c` |
| `preview/checked/pz-b3368aea28ac4a11bf09e0dc9c48.json` | 3823 | `be7b01da2d143a3fe3e224c0df8f854fe2f7bc2dfb27dd0ce2f2f0f71eecb7d6` |
| `preview/checked/pz-b5e2302bf71445c09caac76bbc2a7075.json` | 3882 | `6bf49599ad95fce2ebfa5823996e6522223010a75dde67c994b49d75451c98ce` |
| `preview/checked/pz-b6f94e528b48444985d0561cb48a5bc7.json` | 3756 | `c8a38e220c630a13b96bc8aad81d69884969a424918113466604fdde6c4c3e3d` |
| `preview/checked/pz-bd2783fcd3eb428c933d15259961cfcd.json` | 3911 | `ea26861a7139f44dc2ef8f7ba83b04bc8cd5856c4d6f18a62f7cd0a3565bf326` |
| `preview/checked/pz-c71563f1b8c940de998afdd62f09.json` | 3809 | `f2245c4de435b06e001bd24e845db96c4b6e5fe6660e9ab020def93d67a49571` |
| `preview/checked/pz-d6cb06cb41854b1da84f0ba2f043aa14.json` | 3873 | `0b464de25ad57c91d585ddef96365dfe3157115c38fa009493f08244d6d78740` |
| `preview/checked/pz-d7e68d1138a3448c8b2a4b07e8632350.json` | 3798 | `310a0b00e8b74abcfc69fc21a5d621752b48b553f9f77c9ac732bcdc897b878e` |
| `preview/checked/pz-d829eb9b83e94f9c9357ee5ab9c9e359.json` | 3887 | `f8003f99dd9aa906d97e2dd9d4b1d745a035b56321bea8c1fc9b3d6a3feb74c6` |
| `preview/checked/pz-dad34b8331914c909e8ded79491dac94.json` | 3887 | `119e146dea1450a888ad272dc3686612df5cd3aef59e8a498dee0f2792b53cf4` |
| `preview/checked/pz-dbbebc72556d4f0c9a37ab69275480e9.json` | 3860 | `4b588ff2b3e075bc24977411a5afcd0cc65cc25b8dec95e23002b086743680b6` |
| `preview/checked/pz-e2e5092925ce4821a9219be7816b5931.json` | 3770 | `fb0c11c8a40aacf8009e6543978cf9343a4f3989dd38d228d8d23620b78c6773` |
| `preview/checked/pz-e45e2e0d67a34f6aa8368f477454.json` | 3891 | `73ae68d91359a6cdb150537afd955ebbf58ba0f2b8a8536042c80e8d2ad1e901` |
| `preview/checked/pz-eedd1fe72af54714908d5b5aff34.json` | 3826 | `509a8256f7952e1c348ea6d3e0f49d9529004a924d0b59708bc1a4d07b37acf7` |
| `preview/checked/pz-f68e79ef419a4322b68d06817b39330d.json` | 3766 | `b4d06456fe8e61fda42fffb5b7bac72c8a1eeb5484bc26a5b9d62f20011522b1` |
| `preview/report.json` | 107863 | `17ae791ae9e9c44d6828d9ff2f15e22fe1f340fc4e1f36d17e825d1840ec21cb` |
| `preview/report.md` | 88618 | `690fa527186a790a4ec3caab94cd78cb22f9e16f41d0b00fb6bf6ec37a3bc7f2` |
| `run_om01.py` | 5730 | `9fe0873c06e881f47ada48f9f1cd1ac9553fe06687e16b290f007c1edbe1d3f3` |
| `sd2-d-20261026-v01-full-evidence.zip` | 1318051 | `a5cec520dd6e382a778b1cb38477a521bfcd09fb95351ab5349ea01d4cc31aec` |
| `self-review-audit.json` | 845 | `1cf7ff2dd72f6a9c89e1ffe91da8c139779e4c4878eddd0b58381a91a98b1998` |
| `solve-command.json` | 490 | `5c62dc119805b4e00d87a750e246722b1e252fccc0ed923c85802a4619b45d77` |
| `solve-exit.json` | 63 | `49a349faedd5662d2f9f817b2669e37461be93c116761ce6ae976149c3a45197` |
| `solve-stderr.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `solve-stdout.json` | 1623 | `5b5d321b98a102642177d2c675d9c28dd86a7061f43e6a7054db25e2278a0f75` |
| `solve/assessment.json` | 789 | `fc8abc4e71c7418e7d46a3a3904b78d87006ac1a15837b73b0bec707ee6913df` |
| `solve/baseline-proof.json` | 16203 | `f2d5011080f17a6b7dec48546266c41d85754755290501b014e72d8e1832b828` |
| `solve/proof.json` | 78680 | `d740e93a7a975ad7ede1c41924710ef7a60428706062d8d0b70a61fd2427ed62` |
| `solve/result.json` | 1533 | `32a2958525482d7654dbe49360bda9b709290fa785f4a4233a043be0c448c3e2` |
