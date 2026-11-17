const fs=require('fs');
const html=fs.readFileSync('../docs/index.html','utf8');
const src=html.split('/*ENGINE-START*/')[1].split('/*ENGINE-END*/')[0];
const E=new Function(src+';return {repertoire,optimize};')();
const rep=E.repertoire('r1',{x:1.3,y:-5.1,h:2.7});
let t=Date.now(); for(let i=0;i<20;i++) E.optimize('blue',rep,{b1:{fixed:{x:0.5+i*0.05,y:3}},b2:{prev:{x:-1,y:3},hyst:0.025}}); console.log('partner drag ms/call', (Date.now()-t)/20);
t=Date.now(); for(let i=0;i<5;i++) E.optimize('blue',rep,{},{cur:{b1:{x:1,y:3},b2:{x:-1,y:3}},fast:true}); console.log('holder drag (fast) ms/call', (Date.now()-t)/5);
t=Date.now(); for(let i=0;i<5;i++) E.optimize('blue',rep,{},{}); console.log('full ms/call', (Date.now()-t)/5);
