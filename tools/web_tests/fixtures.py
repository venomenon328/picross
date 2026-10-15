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
    # Force overflow on both axes at the bounded browser fallback geometry.
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
