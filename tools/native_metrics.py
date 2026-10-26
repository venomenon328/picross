"""CI2-D work measurements, separate generated originals from delivered copies."""
from collections import Counter
import json


def measure(output, technical, report):
    phases = list(report['checks'])
    worker = technical/'vs2-worker/technical/product-report.json'
    if worker.is_file():
        phases += json.loads(worker.read_text(encoding='utf-8'))['checks']
    processes = [row for row in phases if 'log' in row]
    generated = [p for p in output.rglob('*') if p.is_file() and not p.is_relative_to(technical)]
    delivered = report['selected_evidence']['files']
    roles = Counter(row['process_role'] for row in processes)
    return dict(format='picross-native-work-v1', processes=dict(roles),
                process_seconds={role:round(sum(r['seconds'] for r in processes if r['process_role']==role),6)
                                 for role in roles},
                rendered_processes=sum(r['rendered'] for r in processes),
                rendered_seconds=round(sum(r['seconds'] for r in processes if r['rendered']),6),
                setup_seconds=report['setup_seconds'],
                generated_files=len(generated), generated_pngs=sum(p.suffix=='.png' for p in generated),
                generated_bytes=sum(p.stat().st_size for p in generated),
                delivered_files=len(delivered), delivered_pngs=sum(r['file'].endswith('.png') for r in delivered),
                delivered_bytes=sum(r['bytes'] for r in delivered),
                boundary='Generated: files present in group output before packaging, excluding technical copies; '
                         'delivered: selected mandatory originals/crops. Phase seconds are cumulative, not wall time. '
                         'Import includes editor setup; render includes assertions/readback/encoding in that process.')
