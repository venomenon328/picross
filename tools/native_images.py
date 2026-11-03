"""Measured lossless native crops; optional old-codec comparison on identical frames."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time


def rgba_identity(path):
    from PIL import Image
    with Image.open(path) as image:
        rgba = image.convert('RGBA')
        return dict(size=list(rgba.size), rgba_sha256=hashlib.sha256(rgba.tobytes()).hexdigest())


def require_identical(reference, actual):
    if rgba_identity(reference) != rgba_identity(actual):
        raise ValueError('Native PNG dimensions/RGBA including alpha changed')


def crop_native(directory: Path, reports: list, compare: bool = False):
    from PIL import Image, __version__
    metrics = dict(format='picross-native-images-v1', status='running', pillow=__version__,
                   codec=dict(optimize=False, compress_level=6), comparison=compare,
                   input_frames=0, crops=0, input_bytes=0, output_bytes=0,
                   read_decode_seconds=0., crop_seconds=0., png_write_seconds=0.,
                   reference_png_write_seconds=0., reference_bytes=0, comparison_seconds=0.,
                   source_binding_seconds=0.,
                   entries=[])
    started = time.perf_counter()
    cpu = time.process_time()
    report_path = directory / 'image-costs.json'
    def flush():
        metrics.update(elapsed_seconds=time.perf_counter()-started, cpu_seconds=time.process_time()-cpu)
        report_path.write_text(json.dumps(metrics, indent=2)+'\n', encoding='utf-8')
    flush()
    crops = []
    seen = set()
    try:
        for report in reports:
            for capture in report['captures']:
                path = directory / capture['file']
                if path.name != capture['file'] or path.name in seen:
                    raise ValueError('Unsafe/duplicate native input frame')
                seen.add(path.name)
                context = path.with_name(path.stem+'-context.png')
                path.rename(context)
                metrics['input_bytes'] += context.stat().st_size
                began = time.perf_counter()
                source_sha256 = hashlib.sha256(context.read_bytes()).hexdigest()
                metrics['source_binding_seconds'] += time.perf_counter()-began
                began = time.perf_counter()
                with Image.open(context) as image:
                    image.load()
                    metrics['read_decode_seconds'] += time.perf_counter()-began
                    metrics['input_frames'] += 1
                    for name, rectangle in capture['regions'].items():
                        target = path.with_name(path.stem+'-'+name+'.png')
                        if target.name in seen:
                            raise ValueError('Duplicate native crop')
                        seen.add(target.name)
                        began = time.perf_counter()
                        stored = capture.get('stored_region')
                        if stored is not None:
                            if (stored != rectangle or image.size != (stored[2]-stored[0],stored[3]-stored[1])
                                    or hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest() != capture['stored_rgba_sha256']):
                                raise ValueError('Native crop pixels/dimensions differ from original readback')
                            crop = image.copy()
                            if 'full_reference' in capture:
                                reference_name = capture['full_reference']
                                if not compare or Path(reference_name).name != reference_name:
                                    raise ValueError('Unexpected/unsafe same-frame crop reference')
                                full_reference = directory/reference_name
                                with Image.open(full_reference) as full:
                                    rgba = full.convert('RGBA')
                                    if (list(rgba.size) != capture['framebuffer']
                                            or hashlib.sha256(rgba.tobytes()).hexdigest() != capture['source_rgba_sha256']
                                            or rgba.crop(rectangle).tobytes() != crop.convert('RGBA').tobytes()):
                                        raise ValueError('Native crop differs from independent same-frame crop')
                        else:
                            crop = image.crop(rectangle)
                        metrics['crop_seconds'] += time.perf_counter()-began
                        reference = directory / (target.stem+'.reference.png')
                        if compare:
                            began = time.perf_counter()
                            crop.save(reference, optimize=True)
                            metrics['reference_png_write_seconds'] += time.perf_counter()-began
                            metrics['reference_bytes'] += reference.stat().st_size
                        began = time.perf_counter()
                        if stored is not None:
                            # The source is already the exact original native crop.
                            # Deliver those bytes once; no second PNG encoder/copy.
                            context.rename(target)
                        else:
                            crop.save(target, optimize=False, compress_level=6)
                        metrics['png_write_seconds'] += time.perf_counter()-began
                        metrics['output_bytes'] += target.stat().st_size
                        metrics['crops'] += 1
                        entry = dict(file=target.name, source=capture['file'], source_sha256=source_sha256,
                                     source_size=capture['framebuffer'] if stored is not None else list(image.size), region=rectangle)
                        if stored is not None:
                            entry.update(source_rgba_sha256=capture['source_rgba_sha256'],
                                         stored_rgba_sha256=capture['stored_rgba_sha256'],
                                         stored_region=stored, native_png=True)
                        if compare:
                            began = time.perf_counter()
                            require_identical(reference, target)
                            entry.update(reference=rgba_identity(reference), actual=rgba_identity(target), identical=True)
                            metrics['comparison_seconds'] += time.perf_counter()-began
                            reference.unlink()
                        if stored is not None and 'full_reference' in capture:
                            entry['full_reference_identical'] = True
                            full_reference.unlink()
                        crops.append(dict(entry))
                        metrics['entries'].append(entry)
                flush()
        metrics['status'] = 'success'
    except BaseException as error:
        metrics.update(status='failure', error=str(error))
        raise
    finally:
        flush()
    return crops, metrics
