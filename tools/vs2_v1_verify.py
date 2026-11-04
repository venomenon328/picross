"""Independent current geometry and typography mathematics."""
from __future__ import annotations
import math
from p1_preflight import PreflightError


def require(ok, message):
    if not ok:
        raise PreflightError("V1: " + message)


def close(a, b):
    return abs(a-b) < .025


def typography(r):
    """Reconstruct bounds from native RID ink/advance, independently of layout."""
    data = r['typography']
    require(data['sha256'] == '4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23', 'original font bytes')
    ui, cell = r['ui_scale'], r['actual_cell']
    padding, aa = 2*ui, max(.5, ui/4)
    def dimensions(sample):
        fs = sample['fs']
        ref = sample['reference']
        require({v['text'] for v in ref} == set('0123456789…–'), 'native digit/marker reference')
        baseline = -(min(v['ink'][1] for v in ref)+max(v['ink'][1]+v['ink'][3] for v in ref))/2
        require(close(baseline,sample['baseline']), 'native vertical centering')
        cross, pitches = 0, []
        for axis in ('row','column'):
            along = 0
            for token in sample[axis]:
                text = token['text']
                require(token['font'] == ('Delight Coffee' if text.isdecimal() else 'IBM Plex Sans'), 'explicit glyph source')
                require(all(g['index'] > 0 for g in token['glyphs']), 'no missing digit/marker')
                x,y,w,h = token['ink']
                left, right = x-token['advance']/2, x+w-token['advance']/2
                top, bottom = y+baseline,y+h+baseline
                # HS: every cross vertex is inside the native whole-token ink
                # rectangle. Reserve the largest pencil half-width, C1 and AA
                # for every status and identity (independent RID reconstruction).
                margin = aa
                if text.isdecimal():
                    radius = max(1,fs/18)*1.08/2 + ui/4
                    inset = min(radius+.5,max(0,min(w,h)/2-.05))
                    margin = max(aa,radius+1-inset)
                width = 2*max(-left+margin,right+margin)
                height = 2*max(-top+margin,bottom+margin)
                cross = max(cross,height,width if axis=='column' else 0)
                along = max(along,width if axis=='row' else height)
            pitches.append(math.ceil(along+padding))
        return cross,pitches
    extent,pitches = dimensions(data['selected'])
    next_extent,_ = dimensions(data['next'])
    require(data['selected']['fs'] == r['font_px'] and data['next']['fs'] == r['font_px']+1, 'measured selected/next grade')
    require(pitches == [r['row_pitch'],r['column_pitch']], 'measured shared pitch')
    if r.get('layout_valid', True):
        require(extent <= max(1,cell-padding)+.025, 'full ink/C1/X within cell')
        require(next_extent > max(1,cell-padding), 'largest measured grade')


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
    # Regular B-B: right-hand work camera, original pixel-scaled hit budgets.
    # Reconstruct the projected top rim from the fixed camera contract; do not
    # trust a producer-supplied expected button position.
    width, height = r['client']
    paper_top = .28*height/max(6.075,10.8*height/width)
    for i,b in enumerate(buttons):
        expected = [x+w-(187.5 if w<1700 else 150)-i*58*ui-20*ui,
                    max(y+h/30+12*ui,paper_top+5*ui),44*ui,44*ui]
        require(all(close(a,e) for a,e in zip(b,expected)), 'regular book upper navigation')
    upper = (buttons[2][0]+buttons[0][0]+buttons[0][2])/2
    require(close(axes['navigation'],upper), 'actual navigation union')
    require(all(close(v,upper) for v in frames+controls), 'lower alpha/actual controls vs upper axis')


def record(r):
    ui = r['ui_scale']
    typography(r)
    safe, grid, shift, used = r['safe'], r['grid'], r['translation'], r['occupied']
    minimum, dims = r['minimum_reserve'], r['dimensions']
    fit = ceiling = r['raw_fit']
    budget = [dims[i]*fit+r['fit_slots'][i]*r['fit_pitch'][i]+14 for i in range(2)]
    next_budget = [dims[i]*(fit+.01)+r['next_fit_slots'][i]*r['next_fit_pitch'][i]+14 for i in range(2)]
    require(all(v <= safe[i+2]+.025 for i,v in enumerate(budget)), 'ceiling native reserve fits')
    require(fit+.01<r['next_fit_minimum'] or any(v > safe[i+2]+.001 for i,v in enumerate(next_budget)), 'next hundredth cannot fit')
    require(close(r['actual_cell'],ceiling if r['overview'] else min(r['requested_cell'],ceiling)), 'cell scale')
    for axis, pitch in enumerate((r['row_pitch'],r['column_pitch'])):
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


# Independent expected coverage; mirrors the approved scope, not generated reports.
VISUAL_CONFIGURATIONS = ((1280, 720, 1.25), (1920, 1080, 1.0), (2560, 1440, 1.25))
