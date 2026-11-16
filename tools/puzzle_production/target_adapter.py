"""The current integration CLI; creative preparation uses authoring_inspection."""
import argparse
import json
import sys
from pathlib import Path
from .contract import InvalidInput,InvalidProof,Aborted
from . import operation_diagnostics as diagnostic
from .image_validation import validate_reveal

def inspect(source):
    from .integration_input import Input
    value=Input(source)
    return {"status":"valid","id":value.entry["id"],"technical":True,"editorial_approved":True,"registered":False}


def export(source,output):
    from .integration_input import export as current_export
    return current_export(source,output)


def verify_export(directory):
    from .integration_input import Input
    value=Input(directory)
    return value.value, {"status":"valid","id":value.entry["id"],"technical":True,"editorial_approved":True}


def main(argv=None):
    parser=argparse.ArgumentParser(description="Aktuellen Integrationseingang prüfen und übernehmen")
    sub=parser.add_subparsers(dest="command",required=True)
    for command in ("inspect","export","verify-export","plan","register"):
        p=sub.add_parser(command)
        p.add_argument("--input",required=True,type=Path)
        if command=="export":p.add_argument("--output-dir",required=True,type=Path)
        if command in ("plan","register"):p.add_argument("--checkout",required=True,type=Path)
        if command=="register":
            p.add_argument("--publication-seconds",type=diagnostic.cli_seconds)
            p.add_argument("--recovery-seconds",type=diagnostic.cli_seconds)
    for command in ("recover-registration","check-registry","sync-runtime"):
        p=sub.add_parser(command);p.add_argument("--checkout",required=True,type=Path)
        if command=="recover-registration":p.add_argument("--recovery-seconds",type=diagnostic.cli_seconds)
    p=sub.add_parser("retire-production")
    p.add_argument("--checkout",required=True,type=Path)
    p.add_argument("--integrated-commit",required=True)
    p.add_argument("--puzzle-id",action="append",required=True)
    p.add_argument("--completed-revision",nargs=2,action="append",default=[])
    p.add_argument("--completed-work",nargs=2,action="append",default=[])
    for child in sub.choices.values():
        child.add_argument("--operation-report",type=Path)
    args=parser.parse_args(argv)
    from . import content_registry as registry
    report_path=None
    observation=diagnostic.Diagnostics(args.command,stderr=sys.stderr)
    token=diagnostic.current.set(observation)
    try:
        if args.operation_report:
            report_path=diagnostic.report_target(args.operation_report,[getattr(args,"input",None),getattr(args,"checkout",None),getattr(args,"output_dir",None)])
        observation.environment["tool_commit"]=diagnostic.source_commit()
        if args.command=="inspect": result=inspect(args.input)
        elif args.command=="export": result=export(args.input,args.output_dir)
        elif args.command=="verify-export":result=verify_export(args.input)[1]
        elif args.command in ("plan","register"):
            result=registry.registration(args.input,args.checkout,apply=args.command=="register",
                publication_seconds=getattr(args,"publication_seconds",None),
                recovery_seconds=getattr(args,"recovery_seconds",None))
        elif args.command=="recover-registration":result=registry.recover(args.checkout,recovery_seconds=args.recovery_seconds)
        elif args.command=="check-registry":result=registry.check_checkout(args.checkout)
        elif args.command=="sync-runtime":result=registry.sync_runtime(args.checkout)
        else:
            from .integrated_content import retire
            result=retire(args.checkout,args.puzzle_id,args.integrated_commit,
                          completed_revisions=args.completed_revision,completed_work=args.completed_work)
        observation.outcome=result.get("status","completed")
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (InvalidInput,InvalidProof,ValueError,OSError,KeyError,TypeError,Aborted) as exc:
        print(json.dumps({"status":"blocked","registered":False,"error":str(exc)},ensure_ascii=False))
        observation.outcome="blocked"
        return 4 if isinstance(exc,Aborted) else 2
    finally:
        diagnostic.current.reset(token)
        if report_path is not None:
            try: diagnostic.write_report(report_path,observation.result())
            except (ValueError,OSError) as exc: print("Operation report could not be written: "+str(exc),file=sys.stderr)


if __name__=="__main__":
    raise SystemExit(main())
