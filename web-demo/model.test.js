// Domain tests for the browser demo. Run from repo root: node web-demo/model.test.js
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const html=fs.readFileSync(__dirname+"/index.html","utf8");
const source=html.split("const createModel=")[1].split(";\nconst M=createModel()")[0];
const M=vm.runInNewContext("("+source+")")();
const make=()=>M.make("DEMO","Synthetic sample","Demo owner"),finish=c=>c.tasks.forEach(t=>t.done=true);
function diagnostic(){const c=make();finish(c);M.advance(c);finish(c);M.advance(c);finish(c);return c}
function won(){const c=diagnostic();M.payment(c);M.advance(c);while(c.stage!=="Closed Won"){finish(c);M.advance(c)}return c}
assert.equal(make().stage,"New Inquiry");
assert.throws(()=>M.advance(make()));
{const c=diagnostic();assert.throws(()=>M.advance(c));assert.equal(c.stage,"Diagnostic Completed")}
{const c=diagnostic();M.payment(c);M.advance(c);assert.equal(c.stage,"Cost Estimate Started")}
assert.throws(()=>M.handoff(make()));
{const c=won();M.handoff(c);assert.equal(c.mode,"operations");assert.equal(c.stage,"Intake")}
{const c=make();M.lose(c,"Synthetic cancellation");assert.equal(c.stage,"Closed Lost");assert.throws(()=>M.advance(c))}
{const c=won();M.handoff(c);finish(c);M.advance(c);c.tasks[0].done=true;M.request(c,"Details");finish(c);assert.throws(()=>M.advance(c));c.validated=true;M.advance(c);assert.equal(c.stage,"Technical Review");assert.equal(c.tasks[0].done,true);assert.equal(c.tasks[1].done,false)}
{const c=won();M.handoff(c);finish(c);M.advance(c);M.request(c,"Details");assert.throws(()=>M.request(c,"More"))}
{const c=won();M.handoff(c);while(c.stage!=="Post Operation"){finish(c);M.advance(c)}assert.throws(()=>M.advance(c))}
console.log("10 domain checks passed");
