"""Independent V1 geometry/type acceptance and deliberately bad report controls."""
from __future__ import annotations
import copy
import math
from p1_preflight import PreflightError


def require(ok, message):
    if not ok:
        raise PreflightError("V1: " + message)


def close(a, b):
    return abs(a-b) < .025


def font_size(cell, ui):
    # Unchanged board -> selected Chalkboard scale, independently transcribed.
    rnd = lambda x: math.floor(x + .5)
    nominal = min(rnd((13 if cell < 24 else 14)*ui), max(8, math.floor(cell-4)))
    return min(rnd(nominal*1.35), max(rnd(8*1.35), math.floor(cell-4)))


def sidebar_axes(r, ui):
    axes = r.get('sidebar_axes', {})
    material = axes.get('material', [])
    buttons = axes.get('navigation_buttons', [])
    frames, controls = axes.get('frames', []), axes.get('controls', [])
    require(len(material)==4 and len(buttons)==3 and all(len(b)==4 for b in buttons)
            and len(frames)==3 and len(controls)==4, 'complete upper/lower axis evidence')
    require(all(math.isfinite(v) for v in [*material,*frames,*controls,axes['navigation'],
                                          *(v for b in buttons for v in b)]), 'finite axes')
    x,y,w,h = material
    for i,b in enumerate(buttons):
        expected = [x+w-(187.5 if w<1700 else 150)-(2-i)*58*ui-20*ui,
                    y+h/30+12*ui,44*ui,44*ui]
        require(all(close(a,e) for a,e in zip(b,expected)), 'unchanged upper navigation')
    upper = (buttons[0][0]+buttons[2][0]+buttons[2][2])/2
    require(close(axes['navigation'],upper), 'actual navigation union')
    require(all(close(v,upper) for v in frames+controls), 'lower alpha/actual controls vs upper axis')


def record(r):
    ui = r['ui_scale']
    require(close(r['row_pitch'],24*ui) and close(r['column_pitch'],18*ui), 'pitch')
    require(r['font_px'] == font_size(r['actual_cell'],ui), 'unchanged type policy')
    safe, grid, shift, used = r['safe'], r['grid'], r['translation'], r['occupied']
    minimum, dims = r['minimum_reserve'], r['dimensions']
    fit = min((safe[2]-minimum[0]*24*ui-14)/dims[0], (safe[3]-minimum[1]*18*ui-14)/dims[1])
    require(close(fit,r['raw_fit']) and close(fit,r['independent_fit']), 'original safe fit budget')
    ceiling = max(1, math.floor(fit*100+.000001)/100)
    require(close(r['actual_cell'],ceiling if r['overview'] else min(r['requested_cell'],ceiling)), 'cell scale')
    for axis, pitch in enumerate((24*ui,18*ui)):
        require(minimum[axis] <= r['reserve'][axis] <= r['max_hints'][axis], 'no empty reserve padding')
        require(close(grid[axis]-shift[axis],r['reserve'][axis]*pitch+7), 'whole block translation')
        require(close(grid[axis],r['untranslated_grid'][axis]+shift[axis]), 'untranslated grid binding')
        require(close(used[axis],r['untranslated_occupied'][axis]+shift[axis]), 'untranslated ink binding')
        require(close(grid[axis+2],dims[axis]*r['actual_cell']), 'grid size')
        if fit > 4:
            desired = (safe[axis+2]-r['untranslated_occupied'][axis+2])/2-r['untranslated_occupied'][axis]
            room = max(0,safe[axis+2]-sum(r['untranslated_occupied'][axis::2]))
            expected = min(max(0,math.floor(desired+.5)),math.floor(room))
            require(close(shift[axis],expected), 'balance actual occupied envelope')
    require(close(r['rows'][0],shift[0]) and close(r['columns'][1],shift[1]), 'hint hits translated')
    require(close(r['rows'][1],grid[1]) and close(r['columns'][0],grid[0]), 'hint cross axes translated')
    require(all(close(v,0) for v in r['group_delta']), 'SL aligned visible frames')
    sidebar_axes(r,ui)


def verify(matrix, focused):
    require(not focused['failures'] and len(focused['records']) == 80, 'focused and recovery coverage')
    for r in matrix['records']:
        record(r['v1'])
    for r in focused['records']:
        record(r)
    require({(g['ui_scale'],g['status']) for g in focused['glyphs']} == {(u,s) for u in (1,1.25) for s in range(3)}, 'native glyph/status coverage')
    require(all(not g['clipped'] and not g['collisions'] for g in focused['glyphs']), 'glyph bounds')
    for ui in (1,1.25):
        require(len({g['sha256'] for g in focused['glyphs'] if g['ui_scale'] == ui}) == 3, 'three distinct rendered statuses')
    # Apply failures to a REAL generous-case report, not a hand-built passing fixture.
    source = next(r for r in focused['records'] if r['id']=='F-01' and r['ui_scale']==1 and not r['overview'] and not r['recovery'])
    mutations = {
        'old pitch26': lambda r: r.update(row_pitch=26),
        'smaller font': lambda r: r.update(font_px=r['font_px']-1),
        'old left placement': lambda r: r.update(translation=[0,0]),
        'empty reserve padding': lambda r: r.update(reserve=[r['max_hints'][0]+1,r['reserve'][1]]),
        'grid-only translation': lambda r: r.update(rows=[0,*r['rows'][1:]],columns=[r['columns'][0],0,*r['columns'][2:]]),
        'old group placement': lambda r: r.update(group_delta=[16,0]),
        'jointly shifted lower groups': lambda r: r['sidebar_axes'].update(
            frames=[v+16 for v in r['sidebar_axes']['frames']],controls=[v+16 for v in r['sidebar_axes']['controls']]),
        'shifted actual controls': lambda r: r['sidebar_axes'].update(controls=[v+16 for v in r['sidebar_axes']['controls']]),
        'shifted frames': lambda r: r['sidebar_axes'].update(frames=[v+16 for v in r['sidebar_axes']['frames']]),
        'shifted upper reference': lambda r: r['sidebar_axes'].update(navigation=r['sidebar_axes']['navigation']+16,
            navigation_buttons=[[b[0]+16,*b[1:]] for b in r['sidebar_axes']['navigation_buttons']],
            frames=[v+16 for v in r['sidebar_axes']['frames']],controls=[v+16 for v in r['sidebar_axes']['controls']]),
    }
    rejected=[]
    for name, mutate in mutations.items():
        bad=copy.deepcopy(source)
        mutate(bad)
        try:
            record(bad)
        except PreflightError:
            rejected.append(name)
        else:
            raise PreflightError('V1 negative control escaped: '+name)
    return dict(matrix_records=304,focused_records=80,glyph_status_images=6,negative_controls=rejected)
