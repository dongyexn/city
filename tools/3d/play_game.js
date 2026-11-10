/* ===== game shell ===== */
const $=id=>document.getElementById(id),msg=(t,ms=1600)=>{$('msg').textContent=t;clearTimeout(msg.t);if(ms)msg.t=setTimeout(()=>$('msg').textContent='',ms);};
const b64d=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0)),b64e=u=>{let s='';const b=new Uint8Array(u.buffer,u.byteOffset,u.byteLength);for(let i=0;i<b.length;i+=8192)s+=String.fromCharCode.apply(null,b.subarray(i,i+8192));return btoa(s);};
const MAP=JSON.parse($('map').textContent),SKEY='isle3d-v1';
const fresh=()=>({N:MAP.N,HN:MAP.HN,K:MAP.K,TWA:MAP.TWA,H:b64d(MAP.H),terr:b64d(MAP.terr),kind:b64d(MAP.kind),lvl:b64d(MAP.lvl),deco:b64d(MAP.deco),ocean:b64d(MAP.ocean),LVL:b64d(MAP.LVL),lmkA:new Int32Array(b64d(MAP.lmkA).buffer)});
let GS=fresh();const ED=window.ED={fb:new Map(),big:null,frozen:false};
const N=GS.N,K=GS.K;
const cv=$('cv'),r=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true});r.setPixelRatio(Math.min(devicePixelRatio||1,2));r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;r.shadowMap.autoUpdate=false;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.08;r.outputColorSpace=THREE.SRGBColorSpace;r.debug.checkShaderErrors=false;
const cam=new THREE.OrthographicCamera(-1,1,1,-1,.1,900),V={tx:N/2,tz:N/2,k:38};let W=null,need=true;
const hi=new THREE.Group(),hm=new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:.45,depthTest:false}),hg=new THREE.BoxGeometry(.96,.06,.96);hi.renderOrder=99;
const setCam=()=>{const w=cv.clientWidth,h=cv.clientHeight,a=w/h;cam.left=-V.k*a/2;cam.right=V.k*a/2;cam.top=V.k/2;cam.bottom=-V.k/2;cam.position.set(V.tx+120,125,V.tz+120);cam.lookAt(V.tx,0,V.tz);cam.updateProjectionMatrix();cam.updateMatrixWorld();need=true;};
const resize=()=>{r.setSize(innerWidth,innerHeight,false);setCam();};addEventListener('resize',resize);
const dispose=()=>{if(!W)return;W.sc.remove(hi);W.sc.traverse(o=>{if(o.userData.keep)return;if(o.geometry)o.geometry.dispose();if(o.isInstancedMesh)o.dispose();});for(const t of window.__TEX)t.dispose();window.__TEX.length=0;};
const rebuild=()=>{const t0=performance.now();dispose();W=window.buildCity(GS,r);W.sc.add(hi);r.shadowMap.needsUpdate=true;need=true;return performance.now()-t0;};
const loop=()=>{if(need&&W){need=false;r.render(W.sc,cam);}requestAnimationFrame(loop);};
/* ---- save / load / undo ---- */
const snap=()=>({kind:GS.kind.slice(),deco:GS.deco.slice(),LVL:GS.LVL.slice(),lmkA:GS.lmkA.slice(),fb:[...ED.fb],big:ED.big.map(b=>b.slice())}),
 put=s=>{GS.kind.set(s.kind);GS.deco.set(s.deco);GS.LVL.set(s.LVL);GS.lmkA.set(s.lmkA);ED.fb=new Map(s.fb);ED.big=s.big.map(b=>b.slice());};
const UN=[],RE=[];const save=()=>{try{const s=snap();localStorage.setItem(SKEY,JSON.stringify({kind:b64e(s.kind),deco:b64e(s.deco),LVL:b64e(s.LVL),lmkA:b64e(s.lmkA),fb:s.fb,big:s.big}));}catch(e){}};
const load=()=>{try{const j=JSON.parse(localStorage.getItem(SKEY)||'null');if(!j)return false;put({kind:b64d(j.kind),deco:b64d(j.deco),LVL:b64d(j.LVL),lmkA:new Int32Array(b64d(j.lmkA).buffer),fb:j.fb,big:j.big});ED.frozen=true;return true;}catch(e){return false;}};
/* ---- picking ---- */
const ray=new THREE.Vector3(),org=new THREE.Vector3();
const pick=(cx,cy)=>{const b=cv.getBoundingClientRect();org.set((cx-b.left)/b.width*2-1,-((cy-b.top)/b.height*2-1),-1).unproject(cam);cam.getWorldDirection(ray);for(let l=5;l>=0;l--){const y=l*W.LH+.1,t=(y-org.y)/ray.y,x=Math.floor(org.x+ray.x*t),z=Math.floor(org.z+ray.z*t);if(x<1||z<1||x>=N-1||z>=N-1||!W.land(x,z))continue;if(Math.abs(W.hT(x,z)-l*W.LH)<.01)return [x,z];}return null;};
/* ---- tools ---- */
const CATS=[['res','주거',K.RES],['com','상업',K.COM],['off','업무',K.COM],['pub','공공',K.POWER]];let tool='move',selCat=0,selItem=-1,selBig=0;
const bigAt=i=>ED.big.findIndex(([,x0,y0,w,d])=>{const x=i%N,y=(i/N)|0;return x>=x0&&x<x0+w&&y>=y0&&y<y0+d;});
const free=(x,z)=>{const i=z*N+x;return W.land(x,z)&&!W.riv(x,z)&&GS.lmkA[i]<0&&bigAt(i)<0;};
const clearT=i=>{ED.fb.delete(i);GS.deco[i]=0;};
const bigFp=(x,z)=>{const e=window.__O.BIG[selBig],w=Math.ceil(e[2]),d=Math.ceil(e[3]);return [x-(w>>1),z-(d>>1),w,d];};
/* why a tool can't act on a tile ('' = ok) */
const why=(x,z)=>{const i=z*N+x;if(x<1||z<1||x>=N-1||z>=N-1||!W.land(x,z))return '땅이 아님';
 if(tool==='del')return W.riv(x,z)?'물':'';
 if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z),L=GS.LVL[i];if(x0<2||y0<2||x0+w>N-2||y0+d>N-2)return '자리 부족';for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++){const j=yy*N+xx;if(!free(xx,yy)||GS.kind[j]===K.ROAD)return '빈 땅 '+w+'×'+d+'칸 필요';if(GS.LVL[j]!==L)return '평지 '+w+'×'+d+'칸 필요';}return '';}
 if(W.riv(x,z))return '물 위';if(GS.lmkA[i]>=0||bigAt(i)>=0)return '먼저 철거';
 if(tool==='up'&&GS.LVL[i]>=5)return '최고 높이';if(tool==='down'&&GS.LVL[i]<=1)return '최저 높이';
 if((tool==='tree'||tool==='bld')&&GS.kind[i]===K.ROAD)return '도로 위';return '';};
const apply=tiles=>{let n=0,bad='';for(const [x,z] of tiles){const i=z*N+x,w=why(x,z);if(w){bad=w;continue;}
  if(tool==='road'){clearT(i);GS.kind[i]=K.ROAD;}
  else if(tool==='del'){const b=bigAt(i),a=GS.lmkA[i];if(b>=0)ED.big.splice(b,1);else if(a>=0){for(let j=0;j<N*N;j++)if(GS.lmkA[j]===a){GS.lmkA[j]=-1;GS.kind[j]=K.EMPTY;}}else{clearT(i);GS.kind[i]=K.EMPTY;}}
  else if(tool==='up'||tool==='down')GS.LVL[i]+=tool==='up'?1:-1;
  else if(tool==='tree'){clearT(i);GS.kind[i]=K.EMPTY;GS.deco[i]=1;}
  else if(tool==='bld'){const c=CATS[selCat],L=window.__O.CAT[c[0]];clearT(i);GS.kind[i]=c[2];ED.fb.set(i,[c[0],selItem<0?(Math.random()*L.length)|0:selItem]);}
  else if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z);for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++){const j=yy*N+xx;clearT(j);GS.kind[j]=K.EMPTY;}ED.big.push([selBig,x0,y0,w,d]);}
  n++;}
 if(!n&&bad)msg(bad);return n;};
const busy=(t,fn)=>{msg(t,0);setTimeout(()=>{fn();hi.clear();save();syncTop();msg('');},16);};
const commit=tiles=>{if(!tiles.length)return;const before=snap();if(!apply(tiles)){hi.clear();need=true;return;}UN.push(before);if(UN.length>20)UN.shift();RE.length=0;busy('반영 중',rebuild);};
const undo=()=>{const s=UN.pop();if(!s)return;RE.push(snap());put(s);busy('되돌리는 중',rebuild);},redo=()=>{const s=RE.pop();if(!s)return;UN.push(snap());put(s);busy('다시 적용 중',rebuild);};
const info=(x,z)=>{const i=z*N+x,b=bigAt(i),f=ED.fb.get(i);return b>=0?window.__O.BIG[ED.big[b][0]][0]:GS.lmkA[i]>=0?'단지·공원':f?window.__O.CAT[f[0]][f[1]][0]:GS.kind[i]===K.ROAD?'도로':W.riv(x,z)?'강':'빈 땅 · 높이 '+GS.LVL[i];};
/* ---- view ---- */
const ray2=new THREE.Vector3(),org2=new THREE.Vector3();
const ground=(cx,cy)=>{const b=cv.getBoundingClientRect();org2.set((cx-b.left)/b.width*2-1,-((cy-b.top)/b.height*2-1),-1).unproject(cam);cam.getWorldDirection(ray2);const t=-org2.y/ray2.y;return [org2.x+ray2.x*t,org2.z+ray2.z*t];};
const clampV=()=>{V.tx=Math.max(0,Math.min(N,V.tx));V.tz=Math.max(0,Math.min(N,V.tz));};
const DPR=Math.min(devicePixelRatio||1,2);let lowT=0,low=false;
const moving=()=>{if(DPR>1&&!low){low=true;r.setPixelRatio(1);r.setSize(innerWidth,innerHeight,false);}clearTimeout(lowT);lowT=setTimeout(()=>{if(low){low=false;r.setPixelRatio(DPR);r.setSize(innerWidth,innerHeight,false);need=true;}},220);};
const panPx=(dx,dy)=>{const a=ground(0,0),b=ground(dx,dy);V.tx-=b[0]-a[0];V.tz-=b[1]-a[1];clampV();moving();setCam();};
const zoomAt=(f,cx,cy)=>{const a=ground(cx,cy);V.k=Math.max(6,Math.min(120,V.k*f));setCam();const b=ground(cx,cy);V.tx+=a[0]-b[0];V.tz+=a[1]-b[1];clampV();moving();setCam();};
const fit=()=>{let sx=0,sz=0,n=0;for(let i=0;i<N*N;i++)if(GS.kind[i]===K.ROAD){sx+=i%N;sz+=(i/N)|0;n++;}if(n){V.tx=sx/n;V.tz=sz/n;}V.k=innerWidth<700?34:50;setCam();};
/* ---- highlight ---- */
const hmOk=new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:.5,depthTest:false}),hmNo=new THREE.MeshBasicMaterial({color:'#ff5a4a',transparent:true,opacity:.55,depthTest:false});
const box=(x,z,ok)=>{const m=new THREE.Mesh(hg,ok?hmOk:hmNo);m.position.set(x+.5,W.hT(x,z)+.16,z+.5);m.renderOrder=99;hi.add(m);};
const show=(tiles)=>{hi.clear();for(const [x,z] of tiles){if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z),ok=!why(x,z);for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++)if(xx>0&&yy>0&&xx<N&&yy<N&&W.land(xx,yy))box(xx,yy,ok);}else box(x,z,!why(x,z));}need=true;};
/* ---- pointer ---- */
const P=new Map();let stroke=null,pan=null,pinch=null,space=false,hov=null;
const line=(a,b)=>{const o=[],sx=Math.sign(b[0]-a[0]),sz=Math.sign(b[1]-a[1]);let x=a[0],z=a[1];o.push([x,z]);const xf=Math.abs(b[0]-a[0])>=Math.abs(b[1]-a[1]);
 if(xf){while(x!==b[0]){x+=sx;o.push([x,z]);}while(z!==b[1]){z+=sz;o.push([x,z]);}}else{while(z!==b[1]){z+=sz;o.push([x,z]);}while(x!==b[0]){x+=sx;o.push([x,z]);}}return o;};
const strokeTo=t=>{if(!t||!stroke)return;if(stroke.mode==='one'){stroke.tiles=[t];}else if(stroke.mode==='line'){stroke.tiles=line(stroke.start,t);}else if(!stroke.set.has(t[1]*N+t[0])){stroke.set.add(t[1]*N+t[0]);stroke.tiles.push(t);}show(stroke.tiles);};
cv.addEventListener('pointerdown',e=>{cv.focus();cv.setPointerCapture(e.pointerId);P.set(e.pointerId,[e.clientX,e.clientY]);
 if(P.size===2){stroke=null;hi.clear();pan=null;const [a,b]=[...P.values()];pinch={d:Math.hypot(a[0]-b[0],a[1]-b[1]),mx:(a[0]+b[0])/2,my:(a[1]+b[1])/2};return;}
 if(tool==='move'||e.button!==0||space){pan={x:e.clientX,y:e.clientY,sx:e.clientX,sy:e.clientY,tap:tool==='move'&&e.button===0};return;}
 const t=pick(e.clientX,e.clientY);if(!t)return;stroke={start:t,tiles:[],set:new Set(),mode:tool==='road'?'line':(tool==='big'||tool==='tree'||(tool==='bld'&&selItem>=0))?'one':'brush'};strokeTo(t);});
cv.addEventListener('pointermove',e=>{
 if(!P.has(e.pointerId)){if(e.pointerType==='mouse'&&tool!=='move'&&W){const t=pick(e.clientX,e.clientY),k=t?t[1]*N+t[0]:-1;if(k!==hov){hov=k;show(t?[t]:[]);}}return;}
 P.set(e.pointerId,[e.clientX,e.clientY]);
 if(pinch&&P.size===2){const [a,b]=[...P.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]),mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;panPx(mx-pinch.mx,my-pinch.my);zoomAt(pinch.d/d,mx,my);pinch={d,mx,my};return;}
 if(pan){panPx(e.clientX-pan.x,e.clientY-pan.y);pan.x=e.clientX;pan.y=e.clientY;return;}
 if(stroke)strokeTo(pick(e.clientX,e.clientY));});
const up=e=>{if(!P.has(e.pointerId))return;P.delete(e.pointerId);if(P.size<2)pinch=null;
 if(pan){if(pan.tap&&Math.hypot(e.clientX-pan.sx,e.clientY-pan.sy)<6){const t=pick(e.clientX,e.clientY);if(t)msg(info(t[0],t[1]));}pan=null;}
 if(stroke){const t=stroke.tiles;stroke=null;hov=null;commit(t);}};
cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',e=>{P.delete(e.pointerId);pinch=null;pan=null;if(stroke){stroke=null;hi.clear();need=true;}});
cv.addEventListener('pointerleave',()=>{if(!stroke&&hov!==null){hov=null;hi.clear();need=true;}});cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{e.preventDefault();zoomAt(Math.exp(e.deltaY*.0012),e.clientX,e.clientY);},{passive:false});
/* ---- UI ---- */
const TOOLS=[['move','이동','탭하면 정보'],['road','도로','드래그로 긋기'],['bld','건물','무작위는 드래그'],['big','시설','평지에 탭'],['tree','나무','탭'],['up','높이 ▲','드래그'],['down','높이 ▼','드래그'],['del','철거','드래그']];
const mkb=(t,on,fn,lab)=>{const b=document.createElement('button');b.textContent=t;if(on!==null)b.setAttribute('aria-pressed',on?'true':'false');if(lab)b.setAttribute('aria-label',lab);b.onclick=fn;return b;};
const setTool=id=>{tool=id;stroke=null;hov=null;hi.clear();need=true;drawUI();const t=TOOLS.find(t=>t[0]===id);msg(t[1]+' · '+t[2]);};
const drawUI=()=>{const bar=$('bar');bar.replaceChildren(...TOOLS.map(([id,t])=>mkb(t,tool===id,()=>setTool(id))));const on=bar.querySelector('[aria-pressed="true"]');if(on&&on.scrollIntoView)on.scrollIntoView({block:'nearest',inline:'nearest'});
 const pk=$('pick');pk.hidden=!(tool==='bld'||tool==='big');if(pk.hidden)return;const O=window.__O;
 if(tool==='bld'){$('cats').hidden=false;$('cats').replaceChildren(...CATS.map((c,i)=>mkb(c[1],selCat===i,()=>{selCat=i;selItem=-1;drawUI();})));$('items').replaceChildren(mkb('무작위',selItem<0,()=>{selItem=-1;drawUI();}),...O.CAT[CATS[selCat][0]].map((e,i)=>mkb(e[0],selItem===i,()=>{selItem=i;drawUI();})));}
 else{$('cats').hidden=true;$('items').replaceChildren(...O.BIG.map((e,i)=>mkb(e[0]+' '+Math.ceil(e[2])+'×'+Math.ceil(e[3]),selBig===i,()=>{selBig=i;drawUI();})));}};
const syncTop=()=>{$('undo').disabled=!UN.length;$('redo').disabled=!RE.length;};
$('undo').onclick=undo;$('redo').onclick=redo;$('zin').onclick=()=>zoomAt(.75,innerWidth/2,innerHeight/2);$('zout').onclick=()=>zoomAt(1.33,innerWidth/2,innerHeight/2);$('fit').onclick=fit;
let rs=0;$('reset').onclick=()=>{if(Date.now()-rs>2500){rs=Date.now();msg('한 번 더 누르면 처음 도시로',2500);return;}rs=0;try{localStorage.removeItem(SKEY);}catch(e){}GS=fresh();ED.fb=new Map();ED.big=null;ED.frozen=false;UN.length=0;RE.length=0;msg('처음 도시로',0);setTimeout(()=>{boot();syncTop();},16);};
addEventListener('keydown',e=>{if(e.target.tagName==='INPUT')return;const k=e.key;
 if((e.ctrlKey||e.metaKey)&&k.toLowerCase()==='z'){e.preventDefault();e.shiftKey?redo():undo();return;}if((e.ctrlKey||e.metaKey)&&k.toLowerCase()==='y'){e.preventDefault();redo();return;}if(e.ctrlKey||e.metaKey||e.altKey)return;
 if(k===' '){space=true;e.preventDefault();}else if(k==='Escape'){if(stroke){stroke=null;hi.clear();need=true;}else setTool('move');}
 else if(k>='1'&&k<='8')setTool(TOOLS[+k-1][0]);else if(k==='+'||k==='=')zoomAt(.8,innerWidth/2,innerHeight/2);else if(k==='-')zoomAt(1.25,innerWidth/2,innerHeight/2);else if(k==='0')fit();
 else if(k.startsWith('Arrow')){e.preventDefault();const s=90;panPx(k==='ArrowLeft'?s:k==='ArrowRight'?-s:0,k==='ArrowUp'?s:k==='ArrowDown'?-s:0);}});
addEventListener('keyup',e=>{if(e.key===' ')space=false;});
const boot=()=>{const had=load();rebuild();if(!had){ED.fb=new Map(W.PLACED.map(p=>[p[0],[p[1],p[2]]]));ED.big=W.BIGP.map(b=>b.slice());ED.frozen=true;}drawUI();msg('');};
resize();setTimeout(()=>{boot();fit();syncTop();loop();window.__ready=1;},30);
window.__dbg={pick,cam,V,W:()=>W,GS:()=>GS,go:(x,z,k)=>{V.tx=x;V.tz=z;V.k=k;setCam();},rebuild};
