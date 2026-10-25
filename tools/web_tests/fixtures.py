"""Fixed tiny completion cases and an eight-colour rectangle, never production inputs."""
import json


def hints(line):
    result, previous = [], 0
    for value in line:
        if value:
            if value == previous:
                result[-1]['length'] += 1
            else:
                result.append(dict(length=1, color=value))
        previous = value
    return result


def adapt(project):
    # Fixed display metadata only: no analysis, production activation or catalog input.
    path = project/'data/registry.json'
    registry = json.loads(path.read_text(encoding='utf-8'))
    registry['format'] = 'picross-runtime-registry-v5'
    for index, entry in enumerate(registry['entries']):
        entry['added_at'] = None
        entry['difficulty'] = None if index == 0 else dict(
            method='picross-difficulty-0.4' if index % 2 else 'picross-difficulty-0.3',
            level=f'L{index}', assessment_type='instrumented', confidence='medium',
            plausible_range=[f'L{index}', f'L{index}'], r4_required=index == 5)
    path.write_text(json.dumps(registry)+'\n', encoding='utf-8', newline='\n')
    # Fixed long column; the rectangle below supplies the overflowing row.
    path = project/'data/fixtures/t02.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for i in range(40):
        data['solution'][11][i] = i % 4 + 1
        data['solution'][i][11] = i % 4 + 1
    data['rows'] = [hints(row) for row in data['solution']]
    data['columns'] = [hints(col) for col in zip(*data['solution'])]
    path.write_text(json.dumps(data)+'\n',encoding='utf-8',newline='\n')
    for key, width, height, colors in [('t04',5,5,1), ('t08',8,5,8), ('t09',50,30,8)]:
        path = project/'data/fixtures'/f'{key}.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        palette = ['#343f42','#edca78','#bd604a','#6c9aab','#7c589e','#529574','#e28a45','#b35280']
        matrix = [[(x % colors)+1 if y == 2 else 0 for x in range(width)] for y in range(height)]
        data.update(width=width, height=height, solution=matrix,
                    palette=[dict(id=i+1,color=c,symbol=chr(65+i)) for i,c in enumerate(palette[:colors])],
                    rows=[hints(row) for row in matrix], columns=[hints(col) for col in zip(*matrix)])
        path.write_text(json.dumps(data)+'\n', encoding='utf-8', newline='\n')
