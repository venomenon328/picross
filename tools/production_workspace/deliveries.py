"""Hide only concretely completed deliveries in freshly confirmed main."""
from tools.puzzle_production import current_delivery as current
from tools.puzzle_production.authoring_package import require
from .sources import JSON_LIMIT
from tools.puzzle_production import catalog_io as io

UNREADABLE=(ValueError,OSError,KeyError,TypeError,AttributeError)
COMPLETION_STEP="5 · Lokal registriert; unabhängiges Review und Git-/Mainabschluss prüfen"


class Deliveries:
    def __init__(self,repository,sources):
        self.repository=repository
        self.main=next((s["commit"] for s in sources if s["source"]=="remote" and
                        s["ref"]=="main" and s["commit"]==repository.confirmed_main),None)
        self.main_results={}

    def result(self,source,commit,identifier):
        return current.snapshot(lambda name,limit:source.read(commit,name,limit),identifier)

    def same_delivery(self,job):
        identifier=job["puzzle_id"]
        if identifier not in self.main_results:
            self.main_results[identifier]=self.result(self.repository.cached,self.main,identifier)
        # An uncompleted or resumed record cannot borrow a previous registration.
        record=job["_record"]
        require(record.get("state")=="registered" and not job.get("_current_invalid"),
                "Current work remains open")
        observed=self.result(job["_source"],job["commit"],identifier)
        require(current.same(observed,self.main_results[identifier]),"Main contains another current delivery")
        integration=record.get("integration")
        require(isinstance(integration,dict) and integration.get("operation")=="register","Completion missing")
        if "result" in integration:
            require(current.same(integration["result"],observed),"Work record describes another delivery")
        else:
            # Read the actual selected delivery at the work record's commit,
            # never its obsolete export/receipt claims or another puzzle tree.
            completed=self.result(job["_source"],integration["commit"],identifier)
            require(current.same(completed,observed),"Later raster/image work remains open")
        return True

    def filter(self,jobs):
        result={"confirmed":bool(self.main),"main_commit":self.main,"hidden_count":0,
                "completed_ids":[],"hidden_jobs":[],"note":"","unresolved":[]}
        if not self.main:
            result["note"]="Main ist nicht aktuell bestätigt. Vorhandene Arbeit bleibt sichtbar."
            return jobs,result
        remaining,hidden,closed=[],[],[]
        for job in jobs:
            if job["_record"].get("state")!="registered" or job.get("_current_invalid"):
                remaining.append(job);continue
            try:
                self.same_delivery(job)
            except UNREADABLE as exc:
                remaining.append(job)
                result["unresolved"].append(job["puzzle_id"]+"/"+job["revision"]+": "+str(exc))
            else:
                closed.append(job)
                hidden.append({k:job[k] for k in ("puzzle_id","revision","binding","commit","source","ref")})
        # Match unchanged earlier phase metadata to the actual completed work
        # snapshot. A currently selected earlier phase is always a resumption.
        visible=[]
        for job in remaining:
            matched=False
            if not job.get("current_view") and not job.get("_current_invalid") and job["_record"].get("state")!="registered":
                for done in closed:
                    if done["puzzle_id"]!=job["puzzle_id"] or not done.get("current_view"):continue
                    try:
                        source=done["_source"];at=done["_record"]["integration"]["commit"]
                        record_name=job["_projection"]["record"]["file"]
                        projection=source.read(at,job["file"],JSON_LIMIT)
                        record=source.read(at,record_name,JSON_LIMIT)
                        matched=io.checksum(projection+record)==job["binding"]
                    except UNREADABLE:continue
                    if matched:break
            if matched:hidden.append({k:job[k] for k in ("puzzle_id","revision","binding","commit","source","ref")})
            else:visible.append(job)
        remaining=visible
        result.update(hidden_count=len(hidden),hidden_jobs=hidden,
                      completed_ids=sorted({j["puzzle_id"] for j in hidden}-{j["puzzle_id"] for j in remaining}),
                      note=f"Main aktuell bestätigt: {len(hidden)} abgeschlossene Quellen ausgeblendet. Offene Arbeit bleibt sichtbar.")
        return remaining,result


def active(repository,sources,jobs):
    return Deliveries(repository,sources).filter(jobs)
