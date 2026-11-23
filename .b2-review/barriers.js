(() => {
  const s=window.picrossStorage;
  const pending=new Map(), released=new Map(), events=[], wanted=new Set();
  const original=s.accountSync.bind(s);
  const bridge=window.b2Gates={
    events,wanted,pending,
    replay:stage=>{released.get(stage)(null);events.push({stage,action:"late callback from prior profile replayed"})},
    arm:stage=>wanted.add(stage),
    release:(stage,failed=false)=>{
      const f=pending.get(stage);
      if(!f)throw Error('Missing held '+stage);
      pending.delete(stage);released.set(stage,f);
      events.push({stage,action:failed?'fault delivered':'real callback delivered'});
      f(failed?new Error('synthetic account callback failure'):null);
    }
  };
  s.accountSync=function(ticket){
    const payload=JSON.parse(ticket)[1];
    const stage=typeof payload==='object' && payload!==null?payload.stage || 'dirty':'identity';
    if(!wanted.delete(stage))return original(ticket);
    const sync=s.fs.syncfs;
    s.fs.syncfs=function(populate,done){
      return sync.call(this,populate,err=>{
        if(err)return done(err);
        events.push({stage,action:'real IDBFS sync complete, callback held'});
        pending.set(stage,done);
      });
    };
    try{return original(ticket)}finally{s.fs.syncfs=sync}
  };
})()