import unittest,tempfile
from pathlib import Path
from pipeline import *

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.state={'version':1,'cases':{}}; self.c=add_case(self.state,'DEMO','operator','2030-01-01')
    def next(self,target):
        for t in self.c['tasks']:
            if not t['done']: complete_task(self.c,t['id'])
        advance(self.c,target,'2030-01-01')
    def diagnosed(self): self.next(STAGES[1]); self.next(STAGES[2])
    def won(self):
        self.diagnosed(); record_payment(self.c,'DEMO-RECEIPT'); self.next(STAGES[3]); self.next(STAGES[4]); self.next(STAGES[5]); self.next(STAGES[6])
    def test_new_task(self): self.assertEqual(self.c['tasks'][0]['owner'],'operator')
    def test_gate(self):
        self.diagnosed(); self.assertRaises(ValueError,self.next,STAGES[3]); self.assertEqual(self.c['stage'],STAGES[2]); record_payment(self.c,'DEMO-RECEIPT'); self.next(STAGES[3]); self.assertEqual(self.c['stage'],STAGES[3])
    def test_skip(self): self.assertRaises(ValueError,advance,self.c,STAGES[2],'2030-01-01')
    def test_open_task_gate(self): self.assertRaises(ValueError,advance,self.c,STAGES[1],'2030-01-01')
    def test_overdue(self): self.assertEqual(report(self.state,'2030-01-02')['cases'][0]['overdue_task_ids'],['1'])
    def test_no_task_alert(self): complete_task(self.c,'1'); self.assertIn('No pending task: review and advance or add task',report(self.state,'2030-01-01')['cases'][0]['blockers'])
    def test_lost(self): advance(self.c,STAGES[-1],reason='Synthetic cancellation'); self.assertRaises(ValueError,record_payment,self.c,'X')
    def test_ops_gate(self): self.assertRaises(ValueError,start_operations,self.c,'operator','2030-01-01'); self.won(); start_operations(self.c,'operator','2030-01-01'); self.assertEqual(self.c['operations']['stage'],OPS[0]); advance_operations(self.c,OPS[1],'operator','2030-01-02','Synthetic checklist complete'); self.assertEqual(self.c['operations']['stage'],OPS[1])
    def test_backup(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json'; save(p,self.state); self.assertEqual(load(p),self.state)
    def test_invalid_due_no_mutation(self):
        complete_task(self.c,'1'); self.assertRaises(ValueError,advance,self.c,STAGES[1],'not-a-date'); self.assertEqual(self.c['stage'],STAGES[0])
    def test_payment_idempotent(self): record_payment(self.c,'X'); n=len(self.c['history']); record_payment(self.c,'X'); self.assertEqual(len(self.c['history']),n); self.assertRaises(ValueError,record_payment,self.c,'Y')
