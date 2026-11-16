"""Small current catalog prerequisites, with no production receipt fixture."""
import json
import shutil
from tests.puzzle_production.current_fixtures import checkout, make, approve, json_file
from tools.puzzle_production import current_content as content, catalog_integration, catalog_analysis, current_rating


def registered(home,*,stem,save_slot,revision=1):
    home.mkdir(parents=True,exist_ok=True)
    root=checkout(home/"base")
    source=make(home/"export")
    value=json.loads((source/"manifest.json").read_bytes())
    definition=json.loads((source/"definition.json").read_bytes())
    definition["revision"]=revision
    definition["reveal"]["image"]="res://art/content/"+stem+".png"
    value["definition"]=json_file(source,"definition.json",definition)
    value["entry"].update(save_slot=save_slot,definition="data/content/"+stem+".json",reveal="art/content/"+stem+".png",category_id="voegel")
    value["metadata"]["category_id"]="voegel"
    checked=catalog_analysis.analyze_single(source/"definition.json",home/"analysis",production_mode="mono")
    current=current_rating.from_checked(checked)
    value["difficulty"]=json_file(source,"difficulty.json",current)
    approve(source,value)
    cats=json.loads((root/"content/categories.json").read_bytes());cats["categories"][0]["id"]="voegel"
    json_file(root,"content/categories.json",cats)
    runtime=json.loads((root/content.RUNTIME).read_bytes());runtime["categories"]=cats["categories"]
    json_file(root,content.RUNTIME,runtime)
    catalog_integration.integrate(source,root,apply=True)
    shutil.copytree(root,home/"full-base")
    return current


def pre_metadata(root, *, runtime_version=5):
    """Explicit frozen native-loader fixture, never a content writer."""
    from tools.puzzle_production import current_content as current, catalog_io
    from tools.puzzle_production.content_registry import check_checkout
    check_checkout(root)
    value = catalog_io.json_bytes((root/current.REGISTRY).read_bytes(),8*1024*1024)
    if any(not e['id'].startswith('pz-test-') for e in value['entries']):
        raise ValueError('Historical runtime fixture requires synthetic IDs')
    runtime = catalog_io.json_bytes((root/current.RUNTIME).read_bytes(),8*1024*1024)
    runtime['format'] = 'picross-runtime-registry-v5'
    for entry in runtime['entries']:
        if entry['background']['status'] != 'standard': raise ValueError('Cannot discard selected background')
        del entry['background']
    (root/current.RUNTIME).write_bytes(current.encoded(runtime))
