"""Fabricated negative controls for the independent original-pixel gate."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import at_evidence as gate
from at_test_fixtures import browser_row, fixture_record, png


class OriginalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_native_rejects_changed_originals_rgba_and_missing_matrix_rows(self):
        fixture={'test_only':True,'image_revision':1,'samples':{k:{'rgba':list(v)} for k,v in gate.SAMPLES.items()}}
        (self.root/'at-fixture.json').write_text(json.dumps(fixture))
        report={'at_measurements':[]}
        for window in gate.MATRIX:
            samples=[];pixels=[]
            for x,(kind,source) in enumerate(gate.SAMPLES.items()):
                alpha=source[3]/255
                actual=[round(240*(1-alpha)+source[c]*alpha) for c in range(3)]
                pixels.append(actual)
                samples.append(dict(kind=kind,point=[x,0],source=[v/255 for v in source],
                                    actual=[v/255 for v in actual],background=[240/255]*3,opacity=1))
            name=f'at-catalog-{window[0]}'
            png(self.root/(name+'.png'),pixels);png(self.root/(name+'-paper.png'),[[240]*3]*5)
            report['at_measurements'].append(dict(window=window,small=dict(file=name+'.png',
                background_file=name+'-paper.png',bounds=[0,0,5,1],framebuffer=window[:2],samples=samples)))
        self.assertEqual(gate.native(self.root,report,('small',)),15)
        for mutate in [lambda r:r['at_measurements'].pop(),
                       lambda r:r['at_measurements'][0]['small']['samples'][1]['source'].__setitem__(3,0),
                       lambda r:r['at_measurements'][0]['small']['samples'][3].update(opacity=.5)]:
            candidate=deepcopy(report);mutate(candidate)
            with self.assertRaises(ValueError):gate.native(self.root,candidate,('small',))
        # Even a matching JSON assertion cannot bless a removed white detail.
        item=report['at_measurements'][0]['small'];pixels[1]=[240]*3
        png(self.root/item['file'],pixels);item['samples'][1]['actual']=[240/255]*3
        with self.assertRaisesRegex(ValueError,'composition'):gate.native(self.root,report,('small',))

    def test_browser_rejects_finished_frame_reported_as_blend(self):
        report={'group':'completion'};browser_row(self.root,report)
        gate.browser(self.root,report,{})
        item=report['at_completion'][0]['blend']
        pixels=[s['actual'] for s in item['samples']]
        pixels[4]=list(gate.SAMPLES['ink'][:3])
        png(self.root/item['file'],pixels);item['samples'][4]['actual']=pixels[4]
        with self.assertRaisesRegex(ValueError,'intermediate blend'):gate.browser(self.root,report,{})

    def test_browser_rejects_white_loss_and_unbound_export_or_save_changes(self):
        report={'group':'catalog'};browser_row(self.root,report)
        gate.browser(self.root,report,{})
        item=report['at_catalog'][0]['small']
        pixels=[s['actual'] for s in item['samples']];pixels[1]=[240]*3
        png(self.root/item['file'],pixels);item['samples'][1]['actual']=[240]*3
        with self.assertRaisesRegex(ValueError,'white'):gate.browser(self.root,report,{})
        report={'group':'persistence'};browser_row(self.root,report)
        builds={name:{'manifest':{'build_id':str(i),'files':{f'releases/{i}/at-fixture.json':fixture_record(i)}}}
                for i,name in enumerate(('web-test','web-test-update'),1)}
        gate.browser(self.root,report,builds)
        for mutate in [lambda r:r['at_update']['second'].update(registry_sha256='f'*64),
                       lambda r:r['at_update'].update(slots_after=[]),
                       lambda r:r['at_update']['second'].update(image_sha256='f'*64),
                       lambda r:r['at_update']['restart']['samples'][4].update(actual=[0,0,0])]:
            candidate=deepcopy(report);mutate(candidate)
            with self.assertRaises(ValueError):gate.browser(self.root,candidate,builds)


if __name__=='__main__':unittest.main()
