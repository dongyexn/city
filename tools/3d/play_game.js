/* ===== game shell ===== */
const $=id=>document.getElementById(id),msg=(t,ms=1600)=>{$('msg').textContent=t;clearTimeout(msg.t);if(ms)msg.t=setTimeout(()=>$('msg').textContent='',ms);};
const b64d=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0)),b64e=u=>{let s='';const b=new Uint8Array(u.buffer,u.byteOffset,u.byteLength);for(let i=0;i<b.length;i+=8192)s+=String.fromCharCode.apply(null,b.subarray(i,i+8192));return btoa(s);};
const MAP=JSON.parse($('map').textContent),SKEY='isle3d-v1';
const fresh=()=>({N:MAP.N,HN:MAP.HN,K:MAP.K,TWA:MAP.TWA,H:b64d(MAP.H),terr:b64d(MAP.terr),kind:b64d(MAP.kind),lvl:b64d(MAP.lvl),deco:b64d(MAP.deco),ocean:b64d(MAP.ocean),LVL:b64d(MAP.LVL),lmkA:new Int32Array(b64d(MAP.lmkA).buffer)});
let GS=fresh();const ED=window.ED={fb:new Map(),big:null,frozen:false};
const N=GS.N,K=GS.K;
const cv=$('cv'),r=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true});r.setPixelRatio(Math.min(devicePixelRatio||1,2));r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;r.shadowMap.autoUpdate=false;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.08;r.outputColorSpace=THREE.SRGBColorSpace;
const cam=new THREE.OrthographicCamera(-1,1,1,-1,.1,900),V={tx:N/2,tz:N/2,k:38};let W=null,need=true;
const hi=new THREE.Group(),hm=new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:.45,depthTest:false}),hg=new THREE.BoxGeometry(.96,.06,.96);hi.renderOrder=99;
const setCam=()=>{const w=cv.clientWidth,h=cv.clientHeight,a=w/h;cam.left=-V.k*a/2;cam.right=V.k*a/2;cam.top=V.k/2;cam.bottom=-V.k/2;cam.position.set(V.tx+120,125,V.tz+120);cam.lookAt(V.tx,0,V.tz);cam.updateProjectionMatrix();cam.updateMatrixWorld();need=true;};
const resize=()=>{r.setSize(innerWidth,innerHeight,false);setCam();};addEventListener('resize',resize);
const dispose=()=>{if(!W)return;W.sc.remove(hi);W.sc.traverse(o=>{if(o.geometry)o.geometry.dispose();const m=o.material;if(m)(Array.isArray(m)?m:[m]).forEach(x=>x.dispose());});for(const t of window.__TEX)t.dispose();window.__TEX.length=0;};
const rebuild=()=>{const t0=performance.now();dispose();W=window.buildCity(GS,r);W.sc.add(hi);r.shadowMap.needsUpdate=true;need=true;return performance.now()-t0;};
const loop=()=>{if(need&&W){need=false;r.render(W.sc,cam);}requestAnimationFrame(loop);};
/* ---- save / load / undo ---- */
const snap=()=>({kind:GS.kind.slice(),deco:GS.deco.slice(),LVL:GS.LVL.slice(),lmkA:GS.lmkA.slice(),fb:[...ED.fb],big:ED.big.map(b=>b.slice())}),
 put=s=>{GS.kind.set(s.kind);GS.deco.set(s.deco);GS.LVL.set(s.LVL);GS.lmkA.set(s.lmkA);ED.fb=new Map(s.fb);ED.big=s.big.map(b=>b.slice());};
const UN=[];const save=()=>{try{const s=snap();localStorage.setItem(SKEY,JSON.stringify({kind:b64e(s.kind),deco:b64e(s.deco),LVL:b64e(s.LVL),lmkA:b64e(s.lmkA),fb:s.fb,big:s.big}));}catch(e){}};
const load=()=>{try{const j=JSON.parse(localStorage.getItem(SKEY)||'null');if(!j)return false;put({kind:b64d(j.kind),deco:b64d(j.deco),LVL:b64d(j.LVL),lmkA:new Int32Array(b64d(j.lmkA).buffer),fb:j.fb,big:j.big});ED.frozen=true;return true;}catch(e){return false;}};
/* ---- picking ---- */
const ray=new THREE.Vector3(),org=new THREE.Vector3();
const pick=(cx,cy)=>{const b=cv.getBoundingClientRect();org.set((cx-b.left)/b.width*2-1,-((cy-b.top)/b.height*2-1),-1).unproject(cam);cam.getWorldDirection(ray);for(let l=5;l>=0;l--){const y=l*W.LH+.1,t=(y-org.y)/ray.y,x=Math.floor(org.x+ray.x*t),z=Math.floor(org.z+ray.z*t);if(x<1||z<1||x>=N-1||z>=N-1||!W.land(x,z))continue;if(Math.abs(W.hT(x,z)-l*W.LH)<.01)return [x,z];}return null;};
/* ---- tools ---- */
const CATS=[['res','주거',K.RES],['com','상업',K.COM],['off','업무',K.COM],['pub','공공',K.POWER]];let tool='move',selCat=0,selItem=0,selBig=0;
const bigAt=i=>ED.big.findIndex(([,x0,y0,w,d])=>{const x=i%N,y=(i/N)|0;return x>=x0&&x<x0+w&&y>=y0&&y<y0+d;});
const free=(x,z)=>{const i=z*N+x;return W.land(x,z)&&!W.riv(x,z)&&GS.lmkA[i]<0&&bigAt(i)<0;};
const clearT=i=>{ED.fb.delete(i);GS.deco[i]=0;};
const apply=(tiles)=>{let n=0;for(const [x,z] of tiles){const i=z*N+x;
  if(tool==='road'){if(!free(x,z))continue;clearT(i);GS.kind[i]=K.ROAD;n++;}
  else if(tool==='del'){const b=bigAt(i);if(b>=0){ED.big.splice(b,1);n++;continue;}const a=GS.lmkA[i];if(a>=0){for(let j=0;j<N*N;j++)if(GS.lmkA[j]===a){GS.lmkA[j]=-1;GS.kind[j]=K.EMPTY;}n++;continue;}if(!W.land(x,z)||W.riv(x,z))continue;clearT(i);GS.kind[i]=K.EMPTY;n++;}
  else if(tool==='up'||tool==='down'){if(!free(x,z))continue;const v=GS.LVL[i]+(tool==='up'?1:-1);if(v<1||v>5)continue;GS.LVL[i]=v;n++;}
  else if(tool==='tree'){if(!free(x,z)||GS.kind[i]===K.ROAD)continue;clearT(i);GS.kind[i]=K.EMPTY;GS.deco[i]=1;n++;}
  else if(tool==='bld'){if(!free(x,z)||GS.kind[i]===K.ROAD)continue;const c=CATS[selCat];clearT(i);GS.kind[i]=c[2];ED.fb.set(i,[c[0],selItem]);n++;}
  else if(tool==='big'){const e=window.__O.BIG[selBig],w=Math.ceil(e[2]),d=Math.ceil(e[3]),x0=x-(w>>1),y0=z-(d>>1),L=GS.LVL[i];let ok=x0>1&&y0>1&&x0+w<N-1&&y0+d<N-1;for(let yy=y0;yy<y0+d&&ok;yy++)for(let xx=x0;xx<x0+w;xx++){const j=yy*N+xx;if(!free(xx,yy)||GS.kind[j]===K.ROAD||GS.LVL[j]!==L){ok=false;break;}}
   if(!ok){msg('평평한 빈 땅 '+w+'×'+d+'칸 필요');continue;}for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++){const j=yy*N+xx;clearT(j);GS.kind[j]=K.EMPTY;}ED.big.push([selBig,x0,y0,w,d]);n++;}}
 return n;};
const commit=tiles=>{if(!tiles.length)return;const before=snap();if(!apply(tiles)){hi.clear();need=true;return;}UN.push(before);if(UN.length>12)UN.shift();$('undo').disabled=false;msg('반영 중',0);setTimeout(()=>{rebuild();hi.clear();save();msg('');},20);};
/* ---- pointer ---- */
const P=new Map();let stroke=null,pan=null,pinch=null;
const panBy=(dx,dy)=>{const u=V.k/cv.clientHeight,R=new THREE.Vector3(),U=new THREE.Vector3(),F=new THREE.Vector3();cam.matrixWorld.extractBasis(R,U,F);const a=-dx*u,b=dy*u,det=R.x*U.z-R.z*U.x;V.tx+=(a*U.z-R.z*b)/det;V.tz+=(R.x*b-a*U.x)/det;V.tx=Math.max(0,Math.min(N,V.tx));V.tz=Math.max(0,Math.min(N,V.tz));setCam();};
const zoomBy=f=>{V.k=Math.max(6,Math.min(110,V.k*f));setCam();};
const mark=t=>{if(!t||stroke.set.has(t[1]*N+t[0]))return;stroke.set.add(t[1]*N+t[0]);stroke.tiles.push(t);const m=new THREE.Mesh(hg,hm);m.position.set(t[0]+.5,W.hT(t[0],t[1])+.16,t[1]+.5);m.renderOrder=99;hi.add(m);need=true;};
cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);P.set(e.pointerId,[e.clientX,e.clientY]);
 if(P.size===2){stroke=null;hi.clear();pan=null;const [a,b]=[...P.values()];pinch={d:Math.hypot(a[0]-b[0],a[1]-b[1]),mx:(a[0]+b[0])/2,my:(a[1]+b[1])/2};return;}
 if(tool==='move'||e.button!==0){pan=[e.clientX,e.clientY];return;}
 stroke={tiles:[],set:new Set(),one:tool==='bld'||tool==='big'||tool==='tree'};mark(pick(e.clientX,e.clientY));});
cv.addEventListener('pointermove',e=>{if(!P.has(e.pointerId))return;P.set(e.pointerId,[e.clientX,e.clientY]);
 if(pinch&&P.size===2){const [a,b]=[...P.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]),mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;zoomBy(pinch.d/d);panBy(mx-pinch.mx,my-pinch.my);pinch={d,mx,my};return;}
 if(pan){panBy(e.clientX-pan[0],e.clientY-pan[1]);pan=[e.clientX,e.clientY];return;}
 if(stroke&&!stroke.one)mark(pick(e.clientX,e.clientY));});
const up=e=>{P.delete(e.pointerId);if(P.size<2)pinch=null;pan=null;if(stroke){const t=stroke.tiles;stroke=null;commit(t);}};
cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{e.preventDefault();zoomBy(Math.exp(e.deltaY*.0012));},{passive:false});
/* ---- UI ---- */
const TOOLS=[['move','이동'],['road','도로'],['bld','건물'],['big','시설'],['tree','나무'],['up','높이 ▲'],['down','높이 ▼'],['del','철거']];
const mkb=(t,on,fn)=>{const b=document.createElement('button');b.textContent=t;b.setAttribute('aria-pressed',on?'true':'false');b.onclick=fn;return b;};
const drawUI=()=>{const bar=$('bar');bar.replaceChildren(...TOOLS.map(([id,t])=>mkb(t,tool===id,()=>{tool=id;drawUI();})));
 const pk=$('pick');pk.hidden=!(tool==='bld'||tool==='big');if(pk.hidden)return;const O=window.__O;
 if(tool==='bld'){$('cats').hidden=false;$('cats').replaceChildren(...CATS.map((c,i)=>mkb(c[1],selCat===i,()=>{selCat=i;selItem=0;drawUI();})));$('items').replaceChildren(...O.CAT[CATS[selCat][0]].map((e,i)=>mkb(e[0],selItem===i,()=>{selItem=i;drawUI();})));}
 else{$('cats').hidden=true;$('items').replaceChildren(...O.BIG.map((e,i)=>mkb(e[0]+' '+Math.ceil(e[2])+'×'+Math.ceil(e[3]),selBig===i,()=>{selBig=i;drawUI();})));}};
$('undo').onclick=()=>{const s=UN.pop();if(!s)return;put(s);$('undo').disabled=!UN.length;msg('되돌리는 중',0);setTimeout(()=>{rebuild();save();msg('');},20);};
let rs=0;$('reset').onclick=()=>{if(Date.now()-rs>2500){rs=Date.now();msg('한 번 더 누르면 처음 도시로');return;}rs=0;try{localStorage.removeItem(SKEY);}catch(e){}GS=fresh();ED.fb=new Map();ED.big=null;ED.frozen=false;UN.length=0;$('undo').disabled=true;msg('처음 도시로',0);setTimeout(boot,20);};
const boot=()=>{const had=load();rebuild();if(!had){ED.fb=new Map(W.PLACED.map(p=>[p[0],[p[1],p[2]]]));ED.big=W.BIGP.map(b=>b.slice());ED.frozen=true;}drawUI();msg('');};
resize();setTimeout(()=>{boot();{let sx=0,sz=0,n=0;for(let i=0;i<N*N;i++)if(GS.kind[i]===K.ROAD){sx+=i%N;sz+=(i/N)|0;n++;}if(n){V.tx=sx/n;V.tz=sz/n;}V.k=innerWidth<700?34:50;}setCam();loop();window.__ready=1;},30);
window.__dbg={pick,cam,V,W:()=>W,GS:()=>GS,go:(x,z,k)=>{V.tx=x;V.tz=z;V.k=k;setCam();},rebuild};
