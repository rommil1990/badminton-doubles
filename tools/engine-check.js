// Проверка модели: какие позиции она даёт в типовых ситуациях.
const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const src=html.split('/*ENGINE-START*/')[1].split('/*ENGINE-END*/')[0];
const E=new Function(src+';return {C,PH,makeShot,repertoire,optimize,evalTeam,planPhase,formationOf,FORM,holderPartner,predictNext,sideOf,teamOf,MATES,partnerOf,bandOf};')();
const f=p=>`(${p.x.toFixed(2)}, ${Math.abs(p.y).toFixed(2)})`;
function ready(holder,c,label){
  const t0=Date.now();
  const rep=E.repertoire(holder,c);
  const wt=E.teamOf(holder)==='blue'?'red':'blue';
  const res=E.optimize(wt,rep,{});
  const ev=E.evalTeam(res,wt,rep);
  const [A,B]=E.MATES[wt];
  console.log(`\n== ${label}: holder ${holder} c=(${c.x}, d=${Math.abs(c.y)}, h=${c.h})  [${Date.now()-t0} ms]`);
  console.log(`  ${A} ${f(res[A])}  ${B} ${f(res[B])}  -> ${E.FORM[E.formationOf(res,wt)]}  cost=${res.cost.toFixed(3)} cover=${(ev.cover*100).toFixed(0)}%`);
  for(const r of ev.rows) console.log(`   ${r.shot.name.padEnd(26)} w=${r.w.toFixed(2)} resp=${r.resp} m=${r.bm.toFixed(2)} v=${r.v.toFixed(2)} at d=${r.j>=0?Math.abs(r.shot.hit[r.j].y).toFixed(1):'-'} h=${r.j>=0?r.shot.hit[r.j].h.toFixed(1):'-'}`);
  const hp=E.holderPartner(holder,{x:c.x,y:c.y+E.sideOf(E.teamOf(holder))*0.38},c,null);
  console.log(`  holder partner ${E.partnerOf(holder)} -> ${f(hp)}`);
  return res;
}
ready('r1',{x:1.3,y:-5.1,h:2.7},'Red smashes from rear right');
ready('r1',{x:0,y:-5.3,h:2.7},'Red overhead rear center');
ready('r1',{x:-2.2,y:-5.6,h:2.7},'Red overhead rear left corner');
ready('r1',{x:-0.8,y:-1.0,h:0.45},'Red at net low');
ready('r1',{x:1.5,y:-1.2,h:0.5},'Red at net low right');
ready('r1',{x:-1.1,y:-3.2,h:1.35},'Red midcourt chest height');
ready('r1',{x:-1.5,y:-3.8,h:0.6},'Red defending low mid (after our smash)');
ready('r1',{x:0.5,y:-3.0,h:2.6},'Red overhead midcourt');
ready('r1',{x:-0.3,y:-2.15,h:1.1,serve:true},'Red serve');

// Запланированный удар: партнёр бьющего готовится именно к нему.
{
  const c={x:1.3,y:-5.1,h:2.7}, body={x:c.x,y:c.y-0.38};
  const dep=(plan)=>Math.abs(E.holderPartner('r1',body,c,null,undefined,plan).y);
  const dSmash=dep({type:'smash',dir:'line'}), dClear=dep({type:'clear',dir:'line'}), dAuto=dep(null);
  console.log(`\n== Planned shot, red r1 overhead from the back: partner r2 depth: smash ${dSmash.toFixed(2)} m, clear ${dClear.toFixed(2)} m, auto ${dAuto.toFixed(2)} m`);
  if(!(dClear>dSmash+1.0)){console.log('FAIL: with a planned clear the partner must stand clearly farther from the net than with a planned smash');process.exit(1);}
  if(Math.abs(dAuto-dSmash)>0.01){console.log('FAIL: without a plan the partner must stay where the typical reply (smash) puts them');process.exit(1);}
  console.log('planned-shot check ok');
}
