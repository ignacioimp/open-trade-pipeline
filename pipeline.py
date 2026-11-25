"""Local trade pipeline with explicit payment gates, task ownership and audit history."""
import argparse,json,os,tempfile
from datetime import date, datetime, timezone
from pathlib import Path

STAGES=('New Inquiry','Diagnostic Started','Diagnostic Completed','Cost Estimate Started','Cost Estimate Sent','Proposal Accepted','Closed Won','Closed Lost')
TASKS={STAGES[0]:'Confirm initial inquiry',STAGES[1]:'Review product, planning, supplier and legal readiness',STAGES[2]:'Confirm diagnostic and receive costing payment',STAGES[3]:'Prepare and validate cost estimate',STAGES[4]:'Review estimate with customer',STAGES[5]:'Confirm engagement and handoff',STAGES[6]:None,STAGES[7]:None}
OPS=('Documentation','Supplier readiness','Production','Booking','Transit','Customs','Delivery','Closed')

def timestamp(): return datetime.now(timezone.utc).isoformat()
def nonempty(s):
    if not isinstance(s,str) or not s.strip(): raise ValueError('Nonempty text required')
    return s.strip()
def day(s): return date.fromisoformat(s).isoformat()
def event(case,kind,**details): case['history'].append({'at':timestamp(),'kind':kind,**details})
def active(case): return case['stage'] not in STAGES[-2:]
def task(case,title,owner,due):
    t={'id':str(len(case['tasks'])+1),'title':nonempty(title),'owner':nonempty(owner),'due':day(due),'stage':case['stage'],'done':False}; case['tasks'].append(t); return t

def add_case(state,case_id,owner,due):
    case_id=nonempty(case_id)
    if case_id in state['cases']: raise ValueError('Case ID already exists')
    case={'id':case_id,'stage':STAGES[0],'owner':nonempty(owner),'payment_ref':None,'tasks':[],'history':[],'operations':None}; task(case,TASKS[STAGES[0]],owner,due); event(case,'created'); state['cases'][case_id]=case; return case

def record_payment(case,reference):
    if not active(case): raise ValueError('Case is closed')
    reference=nonempty(reference)
    if case['payment_ref'] is not None and case['payment_ref']!=reference: raise ValueError('Payment already recorded; review correction manually')
    if case['payment_ref']==reference: return
    case['payment_ref']=reference; event(case,'costing_payment_confirmed',reference=reference)

def add_task(case,title,owner,due):
    if not active(case): raise ValueError('Commercial case is closed')
    t=task(case,title,owner,due); event(case,'task_added',task_id=t['id']); return t

def complete_task(case,task_id):
    if not active(case): raise ValueError('Commercial case is closed')
    for t in case['tasks']:
        if t['id']==task_id:
            if not t['done']: t['done']=True; event(case,'task_completed',task_id=task_id)
            return
    raise ValueError('Task not found')

def advance(case,target,due=None,reason=None):
    current=case['stage']
    if not active(case): raise ValueError('Commercial case is closed')
    if target==STAGES[-1]:
        reason=nonempty(reason); case['stage']=target; event(case,'closed_lost',reason=reason); return
    if target not in STAGES or STAGES.index(target)!=STAGES.index(current)+1: raise ValueError('Only the next commercial stage is permitted')
    if target==STAGES[3] and not case['payment_ref']: raise ValueError('Cost estimate requires confirmed payment, not customer interest')
    if any(not t['done'] for t in case['tasks']): raise ValueError('Complete outstanding commercial tasks before advancing')
    if TASKS[target]: day(due)
    case['stage']=target; event(case,'stage_changed',previous=current,target=target)
    if TASKS[target]: task(case,TASKS[target],case['owner'],due)

def start_operations(case,owner,due):
    if case['stage']!=STAGES[6] or case['operations'] is not None: raise ValueError('Operations can only be started once after Closed Won')
    case['operations']={'stage':OPS[0],'owner':nonempty(owner),'due':day(due)}; event(case,'operations_started')

def advance_operations(case,target,owner,due,evidence):
    o=case['operations']; evidence=nonempty(evidence)
    if case['stage']!=STAGES[6] or not o or o['stage']==OPS[-1]: raise ValueError('No active execution')
    if target not in OPS or OPS.index(target)!=OPS.index(o['stage'])+1: raise ValueError('Only the next execution milestone is permitted')
    next_due=None if target==OPS[-1] else day(due); next_owner=nonempty(owner)
    previous=o['stage']; o.update(stage=target,owner=next_owner,due=next_due); event(case,'operations_advanced',previous=previous,target=target,evidence=evidence)

def report(state,as_of):
    day(as_of); rows=[]
    for c in state['cases'].values():
        pending=[t for t in c['tasks'] if not t['done']] if active(c) else []
        blockers=[]
        if c['stage']==STAGES[2] and not c['payment_ref']: blockers.append('Awaiting confirmed costing payment')
        if active(c) and not pending: blockers.append('No pending task: review and advance or add task')
        o=c['operations']; rows.append({'id':c['id'],'stage':c['stage'],'owner':c['owner'],'pending_tasks':pending,'overdue_task_ids':[t['id'] for t in pending if t['due']<as_of],'blockers':blockers,'operations':o,'operations_overdue':bool(o and o['due'] and o['due']<as_of)})
    return {'as_of':as_of,'cases':rows}

def load(path):
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('version')!=1 or not isinstance(data.get('cases'),dict): raise ValueError('Unsupported state format')
    return data

def save(path,state):
    # Single-process local demo; not a concurrency-safe multi-user database.
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:
        temp=Path(f.name); json.dump(state,f,indent=2); f.write('\n')
    try: os.replace(temp,path)
    finally: temp.unlink(missing_ok=True)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--file',type=Path,default=Path('state.json')); s=p.add_subparsers(dest='cmd',required=True)
    s.add_parser('init'); a=s.add_parser('add'); a.add_argument('id'); a.add_argument('owner'); a.add_argument('due')
    a=s.add_parser('payment'); a.add_argument('id'); a.add_argument('reference')
    a=s.add_parser('task'); a.add_argument('id'); a.add_argument('title'); a.add_argument('owner'); a.add_argument('due')
    a=s.add_parser('done'); a.add_argument('id'); a.add_argument('task_id')
    a=s.add_parser('advance'); a.add_argument('id'); a.add_argument('target',choices=STAGES); a.add_argument('--due'); a.add_argument('--reason')
    a=s.add_parser('start-ops'); a.add_argument('id'); a.add_argument('owner'); a.add_argument('due')
    a=s.add_parser('advance-ops'); a.add_argument('id'); a.add_argument('target',choices=OPS); a.add_argument('owner'); a.add_argument('--due'); a.add_argument('--evidence',required=True)
    a=s.add_parser('status'); a.add_argument('--as-of',default=date.today().isoformat())
    args=p.parse_args(); path=args.file
    try:
        if args.cmd=='init':
            if path.exists(): raise ValueError('State file already exists')
            save(path,{'version':1,'cases':{}}); return
        state=load(path)
        if args.cmd=='status': print(json.dumps(report(state,args.as_of),indent=2)); return
        if args.cmd=='add': add_case(state,args.id,args.owner,args.due)
        else:
            c=state['cases'][args.id]
            if args.cmd=='payment': record_payment(c,args.reference)
            elif args.cmd=='task': add_task(c,args.title,args.owner,args.due)
            elif args.cmd=='done': complete_task(c,args.task_id)
            elif args.cmd=='advance': advance(c,args.target,args.due,args.reason)
            elif args.cmd=='start-ops': start_operations(c,args.owner,args.due)
            elif args.cmd=='advance-ops': advance_operations(c,args.target,args.owner,args.due,args.evidence)
        save(path,state)
    except (ValueError,KeyError,TypeError,OSError) as e: p.exit(2,f'Invalid operation: {e}\n')
if __name__=='__main__': main()
