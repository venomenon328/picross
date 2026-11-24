"""Small synthetic current inputs, with no authoring ZIP or producer metadata."""
from io import BytesIO
from pathlib import Path
from PIL import Image, PngImagePlugin
from tools.puzzle_production import current_content as content, integration_input, catalog_rating, catalog_analysis, current_rating
from tools.puzzle_production import categories, background_contract
from tools.puzzle_production.contract import Budget
from tools.puzzle_production.solver import solve


def put(root,name,raw):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    return content.ref(name,raw)


def json_file(root,name,value):
    return put(root,name,content.encoded(value))


def checkout(root):
    root.mkdir(parents=True,exist_ok=True)
    from tools.puzzle_production.catalog_integration import TEST_CATALOG
    put(root, *TEST_CATALOG)
    cats={"format":categories.FORMAT,"categories":[{"id":"test","name":"Test","order":1}]}
    json_file(root,categories.PATH,cats)
    json_file(root,content.REGISTRY,{"format":content.FORMAT,"entries":[],"metadata":[],"backgrounds":[]})
    json_file(root,content.RUNTIME,{"format":content.RUNTIME_FORMAT,"categories":cats["categories"],"entries":[]})
    json_file(root,"game/data/background-capability.json",{"format":"picross-runtime-background-capability-v1",
              "runtime_format":"picross-runtime-registry-v6","profile_id":background_contract.PROFILE["id"],"enabled":True})
    json_file(root,"content/authoring/index.json",{"format":"picross-authoring-index-v1","entries":[]})
    return root


def approve(root,value):
    value["approval"]={"actor":"Synthetic test","timestamp_utc":"2026-11-16T00:00:00Z",
        "statement":"Approve only this synthetic final input.","selection_sha256":integration_input.selection(value),
        "evidence":put(root,"approval.txt",b"Synthetic content and integration decision.\n"),
        "checks":dict.fromkeys(integration_input.CHECKS,True)}
    json_file(root,"manifest.json",value)
    return value


def make(root,*,identifier="pz-current",mode="mono",background="standard",method="picross-difficulty-0.3",colors=1,
         mono_size=(3, 3), primary_rgb="202020"):
    width, height = mono_size if colors == 1 else (3, 3)
    root.mkdir(parents=True,exist_ok=True)
    matrix=[[0,1,0],[1,1,1],[1,1,1]] if colors==1 else [[1,2,1],[2,0,2],[1,2,1]]
    if mono_size != (3, 3) and colors == 1:
        matrix = [[0] * width] + [[1] * width for _ in range(height - 1)]
    from tools.puzzle_production.editor_raster import clues
    data={"schema":2,"id":identifier,"revision":1,"width":width,"height":height,
          "palette":[{"id":1,"color":primary_rgb,"symbol":"A"}]+([{ "id":2,"color":"DD6600","symbol":"B"}] if colors==2 else []),"solution":matrix,
          "rows":[clues(r) for r in matrix],"columns":[clues(r) for r in zip(*matrix)],
          "reveal":{"definition_id":identifier,"image":"res://art/content/"+identifier+".png","name":"Synthetic","version":1}}
    definition=json_file(root,"definition.json",data)
    proof=json_file(root,"proof.json",solve(catalog_rating.definition(content.encoded(data))[1],Budget()))
    # Analyzer is a fixture producer, never called by the integration consumer.
    checked=catalog_analysis.analyze_single(root/"definition.json",root/"analysis",production_mode=mode,method=method)
    difficulty=json_file(root,"difficulty.json",current_rating.from_checked(checked))
    stream=BytesIO();Image.new("RGBA",(width*4,height*4),(30,30,30,255)).save(stream,format="PNG")
    asset=put(root,"reveal.png",stream.getvalue())
    notice=put(root,"notice.txt",b"Author: synthetic test. Usage basis: repository test pixels.\n")
    rights={"author":"synthetic test","usage_basis":"repository test pixels","source":"synthetic test","changes":"synthetic test"}
    image={"asset":asset,"notice":notice,"rights":rights}
    bg=None
    if background=="selected":
        stream=BytesIO();info=PngImagePlugin.PngInfo();info.add(b"sRGB",b"\0")
        im=Image.new("RGBA",(2304,576),(0,0,0,0))
        im.putpixel((100,500),(90,90,90,90));im.save(stream,format="PNG",pnginfo=info)
        bg={"asset":put(root,"background.png",stream.getvalue()),"notice":notice,"rights":rights}
    entry={"id":identifier,"key":identifier,"save_slot":identifier,"definition":"data/content/"+identifier+".json",
           "reveal":"art/content/"+identifier+".png","visible":True,"mode":mode,"category_id":"test"}
    value={"format":integration_input.FORMAT,"entry":entry,"metadata":{"id":identifier,"name":"Synthetic","category_id":"test"},
           "definition":definition,"reveal":image,"background":{"status":background,"image":bg},
           "difficulty":difficulty,"proof":proof,"quality":{"review":json_file(root,"review.json",{"actor":"Synthetic test","timestamp_utc":"2026-11-16T00:00:00Z","statement":"Synthetic visual review.","criteria":{k:{"result":"fulfilled","accepted":False,"reason":"Synthetic criterion checked."} for k in ("Q-R04","Q-H01","Q-H02")}}),
           "exceptions":[]},"test_only":True}
    approve(root,value)
    return root


def fingerprints(root):
    return {p.relative_to(root).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
