const fs=require('fs');
const html=fs.readFileSync('../docs/index.html','utf8');
const src=html.split('/*ENGINE-START*/')[1].split('/*ENGINE-END*/')[0];
const E=new Function(src+';return {makeShot,repertoire,optimize,evalTeam,planPhase,formationOf,FORM,holderPartner,sideOf,teamOf,MATES,partnerOf,bandOf,NAMES};')();
// уроки из UI-скрипта
const ui=html.split('const LESSONS=')[1].split('];\nfunction lessonStart')[0]+']';
const LESSONS=eval(ui);
const f=p=>`(${p.x.toFixed(1)},${Math.abs(p.y).toFixed(1)})`;
for(const Ls of LESSONS){
  console.log('\n### '+(Ls.title.ru||Ls.title));
  const st=Ls.start, team=E.teamOf(st.holder), s=E.sideOf(team);
  let c={x:st.contact.x,y:s*st.contact.d,h:st.contact.h}; if(st.contact.serve)c.serve=true;
  let pos={};
  if(st.pos) for(const id in st.pos) pos[id]={x:st.pos[id].x,y:E.sideOf(E.teamOf(id))*st.pos[id].d};
  let holder=st.holder;
  if(!pos[holder]) pos[holder]={x:c.x*0.95,y:c.y+s*0.38};
  const hp=E.partnerOf(holder); if(!pos[hp]) pos[hp]=E.holderPartner(holder,pos[holder],c,null);
  const wt=team==='blue'?'red':'blue';
  if(!pos[E.MATES[wt][0]]){const r=E.optimize(wt,E.repertoire(holder,c),{});for(const id of E.MATES[wt])pos[id]=r[id];}
  console.log('  start', Object.entries(pos).map(([k,v])=>k+f(v)).join(' '), 'blue:',E.FORM[E.formationOf(pos,'blue')],'red:',E.FORM[E.formationOf(pos,'red')]);
  let incoming=null;
  for(const [i,stp] of Ls.steps.entries()){
    const t0=Date.now();
    const sh=E.makeShot(holder,c,stp.type,stp.dir);
    const ph=E.planPhase(pos,sh,{hitterTo:stp.hitterTo,late:stp.late});
    console.log(`  ${i+1}. ${holder} ${sh.name} -> ${ph.lost?'LOST':'resp '+ph.R+' m='+ph.margin.toFixed(2)+' h='+ph.c2.h.toFixed(2)+' at '+f(ph.c2)}  [${Date.now()-t0}ms]`);
    console.log('     after', Object.entries(ph.newPos).map(([k,v])=>k+f(v)).join(' '), '| blue:',E.FORM[E.formationOf(ph.newPos,'blue')],'| red:',E.FORM[E.formationOf(ph.newPos,'red')]);
    if(ph.lost) break;
    pos=ph.newPos; holder=ph.R; c=ph.c2; incoming=sh.type;
  }
}
