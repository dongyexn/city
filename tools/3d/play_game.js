/* ===== game shell ===== */
const $=id=>document.getElementById(id),msg=(t,ms=1600)=>{$('msg').textContent=t;clearTimeout(msg.t);if(ms)msg.t=setTimeout(()=>$('msg').textContent='',ms);};
const b64d=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0)),b64e=u=>{let s='';const b=new Uint8Array(u.buffer,u.byteOffset,u.byteLength);for(let i=0;i<b.length;i+=8192)s+=String.fromCharCode.apply(null,b.subarray(i,i+8192));return btoa(s);};
const MAP=JSON.parse($('map').textContent),SKEY='isle3d-v1';
const fresh=()=>({N:MAP.N,HN:MAP.HN,K:MAP.K,TWA:MAP.TWA,H:b64d(MAP.H),terr:b64d(MAP.terr),kind:b64d(MAP.kind),lvl:b64d(MAP.lvl),deco:b64d(MAP.deco),ocean:b64d(MAP.ocean),LVL:b64d(MAP.LVL),lmkA:new Int32Array(b64d(MAP.lmkA).buffer),man:new Uint8Array(MAP.N*MAP.N),pv:new Uint8Array(MAP.N*MAP.N)});
let GS=fresh();const ED=window.ED={fb:new Map(),big:null,frozen:false};
const N=GS.N,K=GS.K;
const cv=$('cv'),r=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true});r.setPixelRatio(Math.min(devicePixelRatio||1,2));r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;r.shadowMap.autoUpdate=false;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.08;r.outputColorSpace=THREE.SRGBColorSpace;r.debug.checkShaderErrors=false;
const cam=new THREE.OrthographicCamera(-1,1,1,-1,.1,900),V={tx:N/2,tz:N/2,k:38};let W=null,need=true;
const hi=new THREE.Group(),hm=new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:.45,depthTest:false}),hg=new THREE.BoxGeometry(.96,.06,.96);hi.renderOrder=99;
const setCam=()=>{const w=cv.clientWidth,h=cv.clientHeight,a=w/h;cam.left=-V.k*a/2;cam.right=V.k*a/2;cam.top=V.k/2;cam.bottom=-V.k/2;cam.position.set(V.tx+120,125,V.tz+120);cam.lookAt(V.tx,0,V.tz);cam.updateProjectionMatrix();cam.updateMatrixWorld();need=true;if(typeof lod==='function')lod();};
const resize=()=>{r.setSize(innerWidth,innerHeight,false);setCam();};addEventListener('resize',resize);
const dispose=()=>{if(!W)return;W.sc.remove(hi);W.sc.remove(GH);W.sc.remove(clouds);W.sc.traverse(o=>{if(o.userData.keep)return;if(o.geometry)o.geometry.dispose();if(o.isInstancedMesh)o.dispose();});for(const t of window.__TEX)t.dispose();window.__TEX.length=0;};
const rebuild=()=>{const t0=performance.now();dispose();W=window.buildCity(GS,r);W.sc.add(hi);W.sc.add(GH);W.sc.add(clouds);mkFly();mkPeople();lod();r.shadowMap.needsUpdate=true;need=true;return performance.now()-t0;};
/* ---- living things: clouds, butterflies, water, wind ---- */
let motion=true;try{const v=localStorage.getItem('isle3d-motion');motion=v?v==='1':!matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(e){}
if(location.hash==='#still')motion=false;
const clouds=new THREE.Group();clouds.userData.keep=1;{const cm0=new THREE.MeshStandardMaterial({color:'#ffffff',roughness:1,emissive:'#dfeeff',emissiveIntensity:.35,transparent:true,opacity:.93});let sd=9;const R=()=>{sd=(sd*16807)%2147483647;return sd/2147483647;};
 for(let i=0;i<6;i++){const ps=[],n=4+((R()*3)|0);for(let k=0;k<n;k++){const w=2.2+R()*2.2,h=1+R()*.9,d=1.8+R()*1.6,g=new RoundedBoxGeometry(w,h,d,4,.45);g.translate((k-(n-1)/2)*1.7+R()*.6,h/2+(k%2)*.35,(R()-.5)*1.2);ps.push(g);}
  const m=new THREE.Mesh(mergeGeometries(ps),cm0.clone());m.castShadow=true;m.userData.keep=1;m.userData.u=R()*140-70;m.userData.v=R()*80-40;m.userData.sp=.22+R()*.2;m.position.y=6.5+R()*3;m.scale.setScalar(.8+R()*.6);clouds.add(m);}}
let fly=null;const FLC=['#ffd23d','#ffffff','#ff8fb1','#8fd0ff','#ffab5c'].map(c=>new THREE.Color(c));
/* fountain droplets */
let drops=null;const mkDrops=()=>{drops=null;const F=W.FNT;if(!F.length)return;const per=20,n=F.length*per,e=new THREE.InstancedMesh(new THREE.SphereGeometry(.036,6,4),new THREE.MeshBasicMaterial({color:'#c4e8ff',transparent:true,opacity:.92}),n);e.frustumCulled=false;W.sc.add(e);drops={e,F,per,n};dropTick(UT.value);};
const dropTick=t=>{if(!drops)return;const {e,F,per}=drops;let k=0;for(const [cx,cz,h] of F)for(let i=0;i<per;i++,k++){const u=(t*.85+i*.377)%1,a=i*2.399+Math.floor(t*.85+i*.377)*.7,tier=i%2,rr=tier?.3+.3*u:.03+.21*u,y=tier?.66+.25*u-.62*u*u:1.0+.45*u-.8*u*u,s=tier?1.15:.85;fp.set(cx+Math.cos(a)*rr,h+.13+y,cz+Math.sin(a)*rr);fm.compose(fp,fq.identity(),fs.set(s,s,s));e.setMatrixAt(k,fm);}fs.set(1,1,1);e.instanceMatrix.needsUpdate=true;};
/* waterfall spray: droplets falling beside the sheet + churning foam on the lip */
let spray=null;const mkSpray=()=>{spray=null;const F=W.FLIP;if(!F.length)return;const per=7,n=F.length*per,e=new THREE.InstancedMesh(new THREE.SphereGeometry(.5,6,4),new THREE.MeshBasicMaterial({color:'#f2fbff',transparent:true,opacity:.9}),n);e.frustumCulled=false;W.sc.add(e);spray={e,F,per};sprayTick(UT.value);};
const sprayTick=t=>{if(!spray)return;const {e,F,per}=spray;let k=0;for(let j=0;j<F.length;j++){const [cx,cz,dx,dz,fw_]=F[j],RTj=fw_??W.RT;for(let i=0;i<per;i++,k++){const ph=(j*.618+i*.377)%1,al=((j*7+i*3)%10)/10-.5;
   if(i<3){const b=.5+.5*Math.sin(t*5+ph*17),s=.16+.1*b;fp.set(cx+dx*(.2+.06*b)+(dx?0:al),RTj-.02+.05*b,cz+dz*(.2+.06*b)+(dz?0:al));fm.compose(fp,fq.identity(),fs.set(s,s*.7,s));}
   else{const u=(t*(.55+ph*.25)+ph)%1,s=.05+.07*(1-u);fp.set(cx+dx*(.34+.25*u)+(dx?0:al),RTj-.2-u*u*9,cz+dz*(.34+.25*u)+(dz?0:al));fm.compose(fp,fq.identity(),fs.set(s,s*1.6,s));}
   e.setMatrixAt(k,fm);}}fs.set(1,1,1);e.instanceMatrix.needsUpdate=true;};
/* cars drive themselves: tile-to-tile on land roads, keep right, random turns */
const DIRS=[[1,0],[0,1],[-1,0],[0,-1]];let carSeq=0,CARS=[];
const roadH=(px,pz)=>{const x=Math.floor(px),z=Math.floor(pz),c=W.RD.cH(x,z),u=px-x,v=pz-z;return (c[0]*(1-u)+c[1]*u)*(1-v)+(c[3]*(1-u)+c[2]*u)*v;};
const blobTex=(()=>{const c=document.createElement('canvas');c.width=64;c.height=32;const g=c.getContext('2d'),q=g.createRadialGradient(32,16,2,32,16,30);q.addColorStop(0,'rgba(0,0,0,.55)');q.addColorStop(.6,'rgba(0,0,0,.3)');q.addColorStop(1,'rgba(0,0,0,0)');g.setTransform(1,0,0,.5,0,8);g.fillStyle=q;g.fillRect(0,-16,64,64);return new THREE.CanvasTexture(c);})(),blobM=new THREE.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,color:'#0b1626'}),blobG=new THREE.PlaneGeometry(1.05,.62);blobG.rotateX(-Math.PI/2);
const carInit=G=>{if(!G.userData.blob){const b=new THREE.Mesh(blobG,blobM);b.position.set(.04,.022,.05);b.renderOrder=2;b.userData.keep=1;G.add(b);G.userData.blob=1;}const x=Math.floor(G.position.x),z=Math.floor(G.position.z),R=W.RD.isRL;let o=DIRS.filter(d=>R(x+d[0],z+d[1]));if(!o.length)o=DIRS;const d=o[(Math.random()*o.length)|0];G.userData.s={x,z,dx:d[0],dz:d[1],f:Math.random(),sx:d[0],sz:d[1],sp:.9+Math.random()*.6,v:0,wait:0,id:carSeq++,off:G.position.y-W.hT(x,z)};G.rotation.order='YZX';};
/* yield: stop for a car close ahead in my lane; at crossings the lower id goes first; give up waiting after a while so nothing deadlocks */
const blocked=G=>{const s=G.userData.s,l=Math.hypot(s.sx,s.sz)||1,ux=s.sx/l,uz=s.sz/l;for(const O of CARS){if(O===G||!O.visible||!O.userData.s)continue;const o=O.userData.s,ex=O.position.x-G.position.x,ez=O.position.z-G.position.z,fw=ex*ux+ez*uz;if(fw<=.05||fw>1.15)continue;const lat=Math.abs(ex*uz-ez*ux);if(lat>.42)continue;const ol=Math.hypot(o.sx,o.sz)||1,dot=(o.sx*ux+o.sz*uz)/ol;if(dot>.5||(dot>-.5&&s.id>o.id))return true;}return false;};
const pedStop=G=>{if(!CWB.size)return false;const s=G.userData.s,l=Math.hypot(s.sx,s.sz)||1,ux=s.sx/l,uz=s.sz/l;for(const ci of CWB){const ex=ci%N+.5-G.position.x,ez=((ci/N)|0)+.5-G.position.z,fw=ex*ux+ez*uz;if(fw<.15||fw>1.3)continue;if(Math.abs(ex*uz-ez*ux)<.7)return true;}return false;};
const carTick=(G,dt)=>{const s=G.userData.s,R=W.RD.isRL;if(!R(s.x,s.z)){G.visible=false;return;}G.visible=true;let tv=s.sp;if(pedStop(G)){tv=0;}else if(s.wait<5&&blocked(G)){tv=0;s.wait+=dt;}else if(s.wait>=5){s.wait+=dt;if(s.wait>6.5)s.wait=0;}else s.wait=0;s.v+=(tv-s.v)*Math.min(1,dt*(tv?2.5:9));s.f+=dt*s.v;
 while(s.f>=1){s.f-=1;if(R(s.x+s.dx,s.z+s.dz)){s.x+=s.dx;s.z+=s.dz;}const o=DIRS.filter(d=>!(d[0]===-s.dx&&d[1]===-s.dz)&&R(s.x+d[0],s.z+d[1])),st=o.find(d=>d[0]===s.dx&&d[1]===s.dz);const d=o.length?(st&&Math.random()<.72?st:o[(Math.random()*o.length)|0]):[-s.dx,-s.dz];s.dx=d[0];s.dz=d[1];}
 const k=1-Math.exp(-dt*7);s.sx+=(s.dx-s.sx)*k;s.sz+=(s.dz-s.sz)*k;const l=Math.hypot(s.sx,s.sz)||1,ux=s.sx/l,uz=s.sz/l,nx=R(s.x+s.dx,s.z+s.dz)?s.f:Math.min(s.f,.3);
 const px=s.x+.5+s.dx*nx-uz*.2,pz=s.z+.5+s.dz*nx+ux*.2,h0=roadH(px-ux*.25,pz-uz*.25),h1=roadH(px+ux*.25,pz+uz*.25);G.position.set(px,(h0+h1)/2+s.off,pz);G.rotation.y=Math.atan2(-uz,ux);G.rotation.z=Math.atan2(h1-h0,.5);};
const mkFly=()=>{fly=null;const F=W.FL;if(!F.length)return;const n=Math.min(60,F.length),wg=s=>{const a=new THREE.CircleGeometry(.07,12);a.scale(1.15,.95,1);a.translate(s*.075,.03,0);const b=new THREE.CircleGeometry(.05,10);b.translate(s*.055,-.055,0);const g=mergeGeometries([a,b]);g.rotateX(-Math.PI/2);return g;},mat=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),A=new THREE.InstancedMesh(wg(1),mat,n),B=new THREE.InstancedMesh(wg(-1),mat,n),src=[];
 for(let i=0;i<n;i++){const f=F[(i*7919)%F.length];src.push([f[0],f[2],f[1],i*2.399]);A.setColorAt(i,FLC[i%5]);B.setColorAt(i,FLC[i%5]);}A.frustumCulled=B.frustumCulled=false;W.sc.add(A);W.sc.add(B);fly={A,B,src,n};flyTick(UT.value);};
const fm=new THREE.Matrix4(),fq=new THREE.Quaternion(),fq2=new THREE.Quaternion(),fp=new THREE.Vector3(),fs=new THREE.Vector3(1,1,1),FY=new THREE.Vector3(0,1,0),FZ=new THREE.Vector3(0,0,1);
const flyTick=t=>{if(!fly)return;for(let i=0;i<fly.n;i++){const [x,y,z,ph]=fly.src[i],a=t*.55+ph,px=x+Math.cos(a)*.55+Math.sin(a*2.3)*.18,pz=z+Math.sin(a*1.3)*.55,py=y+.28+.12*Math.sin(t*1.9+ph),hd=Math.atan2(-Math.sin(a)*.55,Math.cos(a*1.3)*.72),fl=.25+1.0*Math.abs(Math.sin(t*13+ph*5));
  fp.set(px,py,pz);fq.setFromAxisAngle(FY,hd);fq2.setFromAxisAngle(FZ,fl);fm.compose(fp,fq.clone().multiply(fq2),fs);fly.A.setMatrixAt(i,fm);fq2.setFromAxisAngle(FZ,-fl);fm.compose(fp,fq.clone().multiply(fq2),fs);fly.B.setMatrixAt(i,fm);}fly.A.instanceMatrix.needsUpdate=true;fly.B.instanceMatrix.needsUpdate=true;};
/* ---- people: clay residents walking on paved tiles ---- */
const PPLD=JSON.parse($('ppl').textContent),pplM=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.8,metalness:0}),s2l=c=>{c/=255;return c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4);};
const PG=Object.keys(PPLD).map(k=>{const o={};for(const [g,d] of Object.entries(PPLD[k])){const p=new Int16Array(b64d(d.p).buffer),n=new Int8Array(b64d(d.n).buffer),c=b64d(d.c),ix=new Uint16Array(b64d(d.i).buffer),P=new Float32Array(p.length),Nn=new Float32Array(n.length),C=new Float32Array(c.length);for(let j=0;j<p.length;j++)P[j]=p[j]/16384;for(let j=0;j<n.length;j++)Nn[j]=n[j]/127;for(let j=0;j<c.length;j++)C[j]=s2l(c[j]);const G=new THREE.BufferGeometry();G.setAttribute('position',new THREE.BufferAttribute(P,3));G.setAttribute('normal',new THREE.BufferAttribute(Nn,3));G.setAttribute('color',new THREE.BufferAttribute(C,3));G.setIndex(new THREE.BufferAttribute(ix,1));G.computeBoundingSphere();o[g]={G,piv:new THREE.Vector3(...d.piv)};}return o;});
const pblG=new THREE.CircleGeometry(.13,16).rotateX(-Math.PI/2),PS=.44,PY=.125;let PPL=null,CWM=new Map(),CWB=new Set();
const pWalk=(x,z)=>{if(x<0||z<0||x>=N||z>=N||!window.__WALK)return false;const v=window.__WALK[z*N+x];return v===1||v===3;};
/* crosswalk: step across a zebra tile to the walkable tile on the far side (only along the crossing axis) */
const pCross=(p,dx,dz)=>{const ci=(p.z+dz)*N+p.x+dx,hor=CWM.get(ci);if(hor===undefined||(hor?dx!==0:dz!==0))return false;const fx=p.x+2*dx,fz=p.z+2*dz;return pWalk(fx,fz)&&Math.abs(W.hT(fx,fz)-W.hT(p.x,p.z))<.01;};
/* obstacles (trees, benches, lamps, planters…) are circles; a target spot is accepted only if it and the straight walk to it keep clear of them */
const segD=(ax,az,bx,bz,px,pz)=>{const vx=bx-ax,vz=bz-az,l=vx*vx+vz*vz||1e-9,t=Math.max(0,Math.min(1,((px-ax)*vx+(pz-az)*vz)/l));return Math.hypot(ax+vx*t-px,az+vz*t-pz);};
const clearAt=(ax,az,bx,bz,tiles)=>{const OB=window.__OBS;if(!OB)return true;for(const k of tiles){const L=OB.get(k);if(!L)continue;for(const [ox,oz,r] of L){if(Math.hypot(bx-ox,bz-oz)<r+.15)return false;if(segD(ax,az,bx,bz,ox,oz)<r+.12)return false;}}return true;};
const spot=(p,nx,nz)=>{const tl=[p.z*N+p.x,nz*N+nx];for(let k=0;k<8;k++){const sx=nx+.15+Math.random()*.7,sz=nz+.15+Math.random()*.7;if(clearAt(p.px,p.pz,sx,sz,tl))return [sx,sz];}return null;};
const pNext=p=>{const h=W.hT(p.x,p.z),o=[];for(const [dx,dz] of DIRS){const nx=p.x+dx,nz=p.z+dz;if(pWalk(nx,nz)&&Math.abs(W.hT(nx,nz)-h)<.01){const sp=spot(p,nx,nz);if(sp)o.push([dx,dz,0,sp]);}else if(pCross(p,dx,dz))o.push([dx,dz,1]);}
 const f=o.filter(([dx,dz])=>!(dx===-p.dx&&dz===-p.dz)),c=(f.length&&Math.random()<.92?f:o);if(!c.length){p.wait=2+Math.random()*3;return;}
const [dx,dz,cr,sp]=c.find(([dx,dz])=>dx===p.dx&&dz===p.dz&&Math.random()<.6)||c[(Math.random()*c.length)|0];p.dx=dx;p.dz=dz;
 if(cr){const ci=(p.z+dz)*N+p.x+dx,ft=(p.z+2*dz)*N+p.x+2*dx,me=p.z*N+p.x;for(let q=0;q<8;q++){const l=.25+Math.random()*.5;let ax,az,bx,bz,cx2,cz2;if(dx){ax=dx>0?p.x+.97:p.x+.03;az=p.z+l;bx=p.x+2*dx+(dx>0?.03:.97);bz=az;cx2=p.x+2*dx+.5;cz2=az;}else{az=dz>0?p.z+.97:p.z+.03;ax=p.x+l;bz=p.z+2*dz+(dz>0?.03:.97);bx=ax;cx2=ax;cz2=p.z+2*dz+.5;}
  if(clearAt(p.px,p.pz,ax,az,[me])&&clearAt(bx,bz,cx2,cz2,[ft])){p.cw=ci;p.tx=ax;p.tz=az;p.q=[[cx2,cz2]];return;}}p.wait=.5;return;}
 p.x+=dx;p.z+=dz;[p.tx,p.tz]=sp;};
const carNear=ci=>{const cx=ci%N+.5,cz=((ci/N)|0)+.5;for(const C of CARS)if(C.visible&&Math.hypot(C.position.x-cx,C.position.z-cz)<1.25)return true;return false;};
const mkPeople=()=>{if(PPL){for(const m of PPL.meshes)m.dispose();PPL=null;}CWM=new Map((window.__CWL||[]).map(([x,z,h])=>[z*N+x,h]));const WK=window.__WALK;if(!WK)return;const tiles=[],gt=[];for(let i=0;i<N*N;i++){if(WK[i]===1)tiles.push(i);else if(WK[i]===3)gt.push(i);}if(!tiles.length&&!gt.length)return;
 let sd=11;const Rn=()=>{sd=(sd*16807)%2147483647;return sd/2147483647;};const NV=PG.length,n=Math.min(180,Math.max(12,Math.round(tiles.length*.25+gt.length*.015))),cnt=new Array(NV).fill(0),P=[];
 for(let k=0;k<n;k++){const L=(gt.length&&(!tiles.length||Rn()<.2))?gt:tiles,v=k%NV;let i=0,x=0,z=0,px=-1,pz=0;for(let q=0;q<40&&px<0;q++){i=L[(Rn()*L.length)|0];x=i%N;z=(i/N)|0;const ax=x+.15+Rn()*.7,az=z+.15+Rn()*.7;if(clearAt(ax,az,ax,az,[i])&&!P.some(o=>Math.abs(o.px-ax)<.3&&Math.abs(o.pz-az)<.3)){px=ax;pz=az;}}if(px<0)continue;P.push({v,slot:cnt[v]++,on:-1,cw:-1,q:null,x,z,dx:0,dz:0,px,pz,tx:px,tz:pz,hd:Rn()*6.283,ph:Rn()*6.283,sp:.32+Rn()*.16,wait:Rn()*4,mv:0});}
 const meshes=[],IM=[];for(let v=0;v<NV;v++){IM[v]={};if(!cnt[v])continue;for(const [g,o] of Object.entries(PG[v])){const m=new THREE.InstancedMesh(o.G,pplM,cnt[v]);m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);m.frustumCulled=false;m.userData.keep=1;m.receiveShadow=true;W.sc.add(m);meshes.push(m);IM[v][g]=m;}}
 const blob=new THREE.InstancedMesh(pblG,blobM,n);blob.userData.keep=1;blob.frustumCulled=false;blob.renderOrder=2;W.sc.add(blob);meshes.push(blob);PPL={P,IM,meshes,blob};pplPose(0);};
const _M=new THREE.Matrix4(),_B=new THREE.Matrix4(),_L=new THREE.Matrix4(),_R=new THREE.Matrix4(),_q=new THREE.Quaternion(),_Y=new THREE.Vector3(0,1,0),_v=new THREE.Vector3(),_s=new THREE.Vector3();
const pplPose=()=>{if(!PPL)return;const on=V.k<=40;for(const m of PPL.meshes)m.visible=on;if(!on)return;
 for(let k=0;k<PPL.P.length;k++){const p=PPL.P[k],G=PG[p.v],I=PPL.IM[p.v],y=p.on>=0?roadH(p.px,p.pz)+.004:W.hT(p.x,p.z)+PY,sw=Math.sin(p.ph)*.65*p.mv,bob=Math.abs(Math.cos(p.ph))*.025*p.mv;
  _q.setFromAxisAngle(_Y,p.hd);_B.compose(_v.set(p.px,y+bob*PS,p.pz),_q,_s.set(PS,PS,PS));
  for(const g in I){const m=I[g];if(g==='body'){m.setMatrixAt(p.slot,_B);continue;}const a=g==='armL'?-sw:g==='armR'?sw:g==='legL'?sw*.8:-sw*.8;_L.makeRotationX(a).setPosition(G[g].piv);_R.multiplyMatrices(_B,_L);m.setMatrixAt(p.slot,_R);}
  _M.makeTranslation(p.px,y+.006,p.pz);PPL.blob.setMatrixAt(k,_M);}
 for(const m of PPL.meshes)m.instanceMatrix.needsUpdate=true;};
const pplTick=(dt,t)=>{if(!PPL)return;CWB.clear();for(const p of PPL.P){if(p.wait>0){p.wait-=dt;p.mv=Math.max(0,p.mv-dt*4);if(p.on>=0)CWB.add(p.on);continue;}const ddx=p.tx-p.px,ddz=p.tz-p.pz,d=Math.hypot(ddx,ddz);
  let blk=false;if(p.on<0)for(const o of PPL.P){if(o===p)continue;const ex=o.px-p.px,ez=o.pz-p.pz;if(ex>.3||ex<-.3||ez>.3||ez<-.3)continue;if(ex*ex+ez*ez<.08&&ex*ddx+ez*ddz>0){blk=true;break;}}
  if(blk){p.mv=Math.max(0,p.mv-dt*4);p.bw=(p.bw||0)+dt;if(p.bw>.8){p.bw=0;const cx=Math.floor(p.px),cz=Math.floor(p.pz);p.q=null;p.cw=-1;p.x=cx;p.z=cz;const sp=spot({x:cx,z:cz,px:p.px,pz:p.pz},cx,cz);if(sp){p.tx=sp[0];p.tz=sp[1];}else{p.tx=p.px;p.tz=p.pz;p.wait=1;}}continue;}p.bw=0;
  if(d<.04){if(p.q&&p.q.length){if(p.cw>=0&&p.on<0&&carNear(p.cw)){p.wait=.4;p.mv=0;continue;}[p.tx,p.tz]=p.q.shift();continue;}p.q=null;if(p.cw>=0){p.cw=-1;}if(Math.random()<.08)p.wait=1+Math.random()*4;pNext(p);continue;}p.mv=Math.min(1,p.mv+dt*4);const st=Math.min(d,p.sp*dt);p.px+=ddx/d*st;p.pz+=ddz/d*st;const th=Math.atan2(ddx,ddz);let dh=th-p.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));p.hd+=dh*Math.min(1,dt*8);p.ph+=dt*p.sp*28;
  const cx=Math.floor(p.px),cz=Math.floor(p.pz),ci=cz*N+cx;p.on=CWM.has(ci)?ci:-1;if(p.on>=0)CWB.add(ci);if(cx!==p.x||cz!==p.z){if(pWalk(cx,cz)&&Math.abs(W.hT(cx,cz)-W.hT(p.x,p.z))<.01){p.x=cx;p.z=cz;}}}
 pplPose();};
const UT=window.__UT||(window.__UT={value:0});let lastT=0,lastF=0,lastS=0;const lod=()=>{if(!W)return;const on=V.k<=40;if(typeof PPL!=='undefined'&&PPL){for(const m of PPL.meshes)m.visible=on;if(on)pplPose();}for(const m of W.DET)m.visible=on;if(fly)fly.A.visible=fly.B.visible=on&&motion;if(drops)drops.e.visible=on&&motion;};
const tick=(now)=>{const dt=Math.min(.1,(now-lastT)/1000);lastT=now;UT.value+=dt;const t=UT.value;if(W.water.map){W.water.map.offset.x=t*.02;W.water.map.offset.y=t*.035;}if(W.fw.map)W.fw.map.offset.y=t*.7;flyTick(t);if(window.__FOAM){window.__FOAM[0].map.offset.x=Math.sin(t*1.1)*.05;window.__FOAM[1].map.offset.x=Math.sin(t*.8+1)*.03;}{const J=window.__O.JET;J[0].map.offset.y=t*1.15;J[1].map.offset.x=-t*1.4;}pplTick(dt,t);CARS=W.DYN.filter(D=>D.userData.dyn==='car');for(const D of W.DYN){const k=D.userData.dyn;if(k==='car'){if(!D.userData.s)carInit(D);carTick(D,dt);}else if(k==='wheel'){D.rotation.z=t*.18;for(const c of D.children)if(c.userData.dyn==='gond')c.rotation.z=-t*.18;}}
 for(const c of clouds.children){c.userData.u+=dt*c.userData.sp;if(c.userData.u>75)c.userData.u=-75;const u=c.userData.u,v=c.userData.v;c.position.x=N/2+(u+v)/2;c.position.z=N/2+(v-u)/2;const tg=W.land(Math.round(c.position.x),Math.round(c.position.z))?.4:.93;c.material.opacity+=(tg-c.material.opacity)*Math.min(1,dt*1.2);}};
const loop=now=>{requestAnimationFrame(loop);if(!W)return;if(motion&&!document.hidden){if(now-lastF<32)return;lastF=now;tick(now);if(now-lastS>500){lastS=now;r.shadowMap.needsUpdate=true;}need=false;r.render(W.sc,cam);return;}lastT=now;if(need){need=false;r.render(W.sc,cam);}};
/* ---- save / load / undo ---- */
const snap=()=>({pv:GS.pv.slice(),terr:GS.terr.slice(),man:GS.man.slice(),kind:GS.kind.slice(),deco:GS.deco.slice(),LVL:GS.LVL.slice(),lmkA:GS.lmkA.slice(),fb:[...ED.fb],big:ED.big.map(b=>b.slice())}),
 put=s=>{if(s.pv)GS.pv.set(s.pv);if(s.terr)GS.terr.set(s.terr);if(s.man)GS.man.set(s.man);GS.kind.set(s.kind);GS.deco.set(s.deco);GS.LVL.set(s.LVL);GS.lmkA.set(s.lmkA);ED.fb=new Map(s.fb);ED.big=s.big.map(b=>b.slice());};
const UN=[],RE=[];const save=()=>{try{const s=snap();localStorage.setItem(SKEY,JSON.stringify({pv:b64e(s.pv),terr:b64e(s.terr),man:b64e(s.man),kind:b64e(s.kind),deco:b64e(s.deco),LVL:b64e(s.LVL),lmkA:b64e(s.lmkA),fb:s.fb,big:s.big}));}catch(e){}};
const load=()=>{try{const j=JSON.parse(localStorage.getItem(SKEY)||'null');if(!j)return false;put({pv:j.pv?b64d(j.pv):null,terr:j.terr?b64d(j.terr):null,man:j.man?b64d(j.man):null,kind:b64d(j.kind),deco:b64d(j.deco),LVL:b64d(j.LVL),lmkA:new Int32Array(b64d(j.lmkA).buffer),fb:j.fb,big:j.big});ED.frozen=true;return true;}catch(e){return false;}};
/* ---- picking ---- */
const ray=new THREE.Vector3(),org=new THREE.Vector3();
const pick=(cx,cy)=>{const b=cv.getBoundingClientRect();org.set((cx-b.left)/b.width*2-1,-((cy-b.top)/b.height*2-1),-1).unproject(cam);cam.getWorldDirection(ray);
 const ok=(x,z)=>x>=1&&z>=1&&x<N-1&&z<N-1&&W.land(x,z),H=(x,z)=>W.hT(x,z)+.135;let tin=(6*W.LH-org.y)/ray.y,px=org.x+ray.x*tin,pz=org.z+ray.z*tin,x=Math.floor(px),z=Math.floor(pz);
 const sx=Math.sign(ray.x)||1,sz=Math.sign(ray.z)||1,dX=Math.abs(1/(ray.x||1e-9)),dZ=Math.abs(1/(ray.z||1e-9));let tx=tin+(sx>0?x+1-px:px-x)*dX,tz=tin+(sz>0?z+1-pz:pz-z)*dZ,prev=null;
 for(let k=0;k<600;k++){const tout=Math.min(tx,tz);if(ok(x,z)){const h=H(x,z),yi=org.y+ray.y*tin,yo=org.y+ray.y*tout;if(yo<=h){if(yi>h||!prev)return [x,z];const [qx,qz]=prev,hq=W.hT(qx,qz);return W.hT(qx+1,qz)>hq+.01&&W.hT(qx,qz+1)>hq+.01?prev:[x,z];}prev=[x,z];}else prev=null;
  tin=tout;if(tx<tz){x+=sx;tx+=dX;}else{z+=sz;tz+=dZ;}if(org.y+ray.y*tin<-2)break;}return null;};
/* ---- tools ---- */
const CATS=[['res','주거',K.RES],['com','상업',K.COM],['off','업무',K.COM],['pub','공공',K.POWER]];let tool='move',selCat=0,selItem=-1,selBig=0,selTer=0,selRoad=0,selH=0,bs=1,flatL=1,rot=0,pendRand=0;const ROADS=[['차도','T:road'],['보도 A','T:p1'],['보도 B','T:p2'],['보도 C','T:p3']],HGT=['올리기','내리기','평탄화'];const DIRN=[null,'z+','x+','z-','x-'],TERS=[['잔디',0,'T:grass'],['흙',5,'T:dirt'],['물',-1,'T:water']];
const rollRand=()=>{const L=window.__O.CAT[CATS[selCat][0]];pendRand=(Math.random()*L.length)|0;};
const bigAt=i=>ED.big.findIndex(([,x0,y0,w,d])=>{const x=i%N,y=(i/N)|0;return x>=x0&&x<x0+w&&y>=y0&&y<y0+d;});
const free=(x,z)=>{const i=z*N+x;return W.land(x,z)&&!W.riv(x,z)&&GS.lmkA[i]<0&&bigAt(i)<0;};
const clearT=i=>{ED.fb.delete(i);GS.deco[i]=0;};
const bigDir=()=>DIRN[rot]||'z+',bigFp=(x,z)=>{const e=window.__O.BIG[selBig],sw=bigDir()[0]==='x';let w=Math.ceil(e[2]),d=Math.ceil(e[3]);if(sw)[w,d]=[d,w];return [x-(w>>1),z-(d>>1),w,d];};
const rdirP=(x,z)=>{for(let r=1;r<4;r++)for(const [dx,dy,n] of [[0,1,'z+'],[1,0,'x+'],[0,-1,'z-'],[-1,0,'x-']]){const xx=x+dx*r,yy=z+dy*r;if(xx>=0&&yy>=0&&xx<N&&yy<N&&GS.kind[yy*N+xx]===K.ROAD&&W.land(xx,yy))return n;}return 'z+';};
/* why a tool can't act on a tile ('' = ok) */
const why=(x,z)=>{const i=z*N+x;if(x<1||z<1||x>=N-1||z>=N-1||!W.land(x,z))return '땅이 아님';
 if(tool==='del')return W.riv(x,z)&&GS.kind[i]!==K.ROAD?'물':'';
 if(tool==='road'||tool==='hgt'){if(GS.lmkA[i]>=0||bigAt(i)>=0)return '먼저 철거';if(tool==='hgt'){const L=GS.LVL[i];if(selH===0&&L>=5)return '최고 높이';if(selH===1&&L<=1)return '최저 높이';}return '';}
 if(tool==='ter')return GS.lmkA[i]>=0||bigAt(i)>=0?'먼저 철거':'';
 if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z),L=GS.LVL[i];if(x0<2||y0<2||x0+w>N-2||y0+d>N-2)return '자리 부족';for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++){const j=yy*N+xx;if(!free(xx,yy)||GS.kind[j]===K.ROAD)return '빈 땅 '+w+'×'+d+'칸 필요';if(GS.LVL[j]!==L)return '평지 '+w+'×'+d+'칸 필요';}return '';}
 if(W.riv(x,z))return '물 위';if(GS.lmkA[i]>=0||bigAt(i)>=0)return '먼저 철거';
 if((tool==='tree'||tool==='bld')&&GS.kind[i]===K.ROAD)return '도로 위';return '';};
const apply=tiles=>{let n=0,bad='';for(const [x,z] of tiles){const i=z*N+x,w=why(x,z);if(w){bad=w;continue;}
  if(tool==='road'){clearT(i);if(selRoad===0){GS.kind[i]=K.ROAD;GS.pv[i]=0;}else{GS.kind[i]=K.EMPTY;if(W.riv(x,z))GS.terr[i]=0;GS.pv[i]=selRoad;}}
  else if(tool==='del'){const b=bigAt(i),a=GS.lmkA[i];if(b>=0)ED.big.splice(b,1);else if(a>=0){for(let j=0;j<N*N;j++)if(GS.lmkA[j]===a){GS.lmkA[j]=-1;GS.kind[j]=K.EMPTY;}}else{clearT(i);if(GS.kind[i]===K.EMPTY&&window.__PAVE&&window.__PAVE[i])GS.pv[i]=9;GS.kind[i]=K.EMPTY;}}
  else if(tool==='hgt'){GS.LVL[i]=selH===2?flatL:GS.LVL[i]+(selH===0?1:-1);GS.man[i]=1;}
  else if(tool==='ter'){const t=TERS[selTer][1];clearT(i);GS.kind[i]=K.EMPTY;GS.terr[i]=t<0?GS.TWA:t;GS.pv[i]=t<0?0:9;}
  else if(tool==='tree'){clearT(i);GS.kind[i]=K.EMPTY;GS.deco[i]=1;}
  else if(tool==='bld'){const c=CATS[selCat],L=window.__O.CAT[c[0]];clearT(i);GS.kind[i]=c[2];const it=selItem>=0?selItem:n===0?pendRand:(Math.random()*L.length)|0,f=[c[0],it];if(rot)f.push(DIRN[rot]);ED.fb.set(i,f);}
  else if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z);for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++){const j=yy*N+xx;clearT(j);GS.kind[j]=K.EMPTY;}ED.big.push([selBig,x0,y0,w,d,bigDir()]);}
  n++;}
 if(!n&&bad)msg(bad);return n;};
const busy=(t,fn)=>{msg(t,0);setTimeout(()=>{fn();clrH();save();syncTop();msg('');},16);};
const commit=tiles=>{if(!tiles.length)return;const before=snap();if(!apply(tiles)){clrH();need=true;return;}if(tool==='bld')rollRand();UN.push(before);if(UN.length>20)UN.shift();RE.length=0;busy('반영 중',rebuild);};
const undo=()=>{const s=UN.pop();if(!s)return;RE.push(snap());put(s);busy('되돌리는 중',rebuild);},redo=()=>{const s=RE.pop();if(!s)return;UN.push(snap());put(s);busy('다시 적용 중',rebuild);};
const info=(x,z)=>{const i=z*N+x,b=bigAt(i),f=ED.fb.get(i);return b>=0?window.__O.BIG[ED.big[b][0]][0]:GS.lmkA[i]>=0?'단지·공원':f?window.__O.CAT[f[0]][f[1]][0]:GS.kind[i]===K.ROAD?'도로':W.riv(x,z)?'물':window.__PAVE&&window.__PAVE[i]?'보도':(GS.terr[i]===5?'흙':'빈 땅')+' · 높이 '+GS.LVL[i];};
/* ---- view ---- */
const ray2=new THREE.Vector3(),org2=new THREE.Vector3();
const ground=(cx,cy)=>{const b=cv.getBoundingClientRect();org2.set((cx-b.left)/b.width*2-1,-((cy-b.top)/b.height*2-1),-1).unproject(cam);cam.getWorldDirection(ray2);const t=-org2.y/ray2.y;return [org2.x+ray2.x*t,org2.z+ray2.z*t];};
const clampV=()=>{V.tx=Math.max(0,Math.min(N,V.tx));V.tz=Math.max(0,Math.min(N,V.tz));};
const DPR=Math.min(devicePixelRatio||1,2);let lowT=0,low=false;
const moving=()=>{if(DPR>1&&!low){low=true;r.setPixelRatio(1);r.setSize(innerWidth,innerHeight,false);}clearTimeout(lowT);lowT=setTimeout(()=>{if(low){low=false;r.setPixelRatio(DPR);r.setSize(innerWidth,innerHeight,false);need=true;}},220);};
const panPx=(dx,dy)=>{const a=ground(0,0),b=ground(dx,dy);V.tx-=b[0]-a[0];V.tz-=b[1]-a[1];clampV();moving();setCam();};
const zoomAt=(f,cx,cy)=>{const a=ground(cx,cy);V.k=Math.max(2.4,Math.min(120,V.k*f));setCam();const b=ground(cx,cy);V.tx+=a[0]-b[0];V.tz+=a[1]-b[1];clampV();moving();setCam();};
const fit=()=>{let sx=0,sz=0,n=0;for(let i=0;i<N*N;i++)if(GS.kind[i]===K.ROAD){sx+=i%N;sz+=(i/N)|0;n++;}if(n){V.tx=sx/n;V.tz=sz/n;}V.k=innerWidth<700?34:50;setCam();};
/* ---- ghost preview + thumbnails: a private OBJ factory builds one prototype per item/direction ---- */
const GH=new THREE.Group();GH.userData.keep=1;const clrH=()=>{hi.clear();GH.clear();};let O2=null,R2=null;const PRO=new Map(),GHO=new Map(),GMAT=new Map(),TH=new Map();
const o2=()=>{if(!O2){const k=window.__KEEPTX;window.__KEEPTX=true;R2=new THREE.Group();const ob=window.OBC;window.OBC=undefined;try{O2=OBJ(THREE,RoundedBoxGeometry,R2);}finally{window.OBC=ob;}window.__KEEPTX=k;}return O2;};
const blockProto=k=>{const X=window.__BTX,tx=t=>{const c=t.clone();c.repeat.set(.5,.5);c.needsUpdate=true;return c;},M=(t,col)=>new THREE.MeshStandardMaterial({map:t?tx(t):null,color:col||'#ffffff',roughness:.85}),g=new THREE.Group();
 const top={grass:M(X.TT,'#c4e2a0'),dirt:M(X.DT2,'#f5ccA8'),water:M(X.DT2,'#c49a78'),road:M(X.AT),p1:M(X.PT1),p2:M(X.PT2),p3:M(X.PT3)}[k],side={grass:M(X.ST),dirt:M(X.DT2,'#e2b48e'),water:M(X.ST)}[k]||M(X.CT);
 const b=new THREE.Mesh(new THREE.BoxGeometry(1,.6,1),[side,side,top,side,side,side]);g.add(b);
 if(k==='water'){const w=new THREE.Mesh(new THREE.BoxGeometry(.98,.44,.98),new THREE.MeshStandardMaterial({color:'#36b2ee',roughness:.15,transparent:true,opacity:.9}));w.position.y=.1;g.add(w);b.scale.y=.5;b.position.y=-.15;}return g;};
const proto=key=>{let g=PRO.get(key);if(g)return g;if(key.startsWith('T:')){g=blockProto(key.slice(2));PRO.set(key,g);return g;}const o=o2(),[t,a,dir]=key.split(':'),k0=window.__KEEPTX;window.__KEEPTX=true;o.lift(0);
 try{if(t==='B'){const bi=+a;if(dir!=='z+')o.rotd(0,0,dir,()=>o.BIG[bi][1](0,0));else o.BIG[bi][1](0,0);}else{const e=o.CAT[t][+a];if(e[1]==='house')o.house(.16,.84,.16,.84,e[2],dir);else o.bld(.16,.84,.16,.84,e[1],e[2],dir);}}finally{window.__KEEPTX=k0;}
 g=R2.children[R2.children.length-1];R2.remove(g);g.position.set(0,0,0);PRO.set(key,g);return g;};
const gm=m=>{let c=GMAT.get(m);if(!c){c=m.clone();c.transparent=true;c.opacity=.5;c.depthWrite=false;c.onBeforeCompile=m.onBeforeCompile;if(m.customProgramCacheKey)c.customProgramCacheKey=m.customProgramCacheKey;GMAT.set(m,c);}return c;};
const ghostOf=key=>{let g=GHO.get(key);if(g)return g;g=proto(key).clone(true);g.traverse(o=>{if(o.isMesh){o.material=Array.isArray(o.material)?o.material.map(gm):gm(o.material);o.castShadow=false;o.receiveShadow=false;o.renderOrder=97;}});GHO.set(key,g);return g;};
const ghostAt=(x,z)=>{let g;if(tool==='bld'){const it=selItem>=0?selItem:pendRand;g=ghostOf(CATS[selCat][0]+':'+it+':'+(DIRN[rot]||rdirP(x,z))).clone();g.position.set(x,W.hT(x,z),z);}
 else if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z);g=ghostOf('B:'+selBig+':'+bigDir()).clone();g.position.set(x0+w/2,W.hT(x0,y0),y0+d/2);}if(g)GH.add(g);};
let TR=null;const thumbR=()=>{if(TR)return TR;const c=document.createElement('canvas');c.width=c.height=128;const rr=new THREE.WebGLRenderer({canvas:c,antialias:true,alpha:true,preserveDrawingBuffer:true});rr.toneMapping=THREE.ACESFilmicToneMapping;rr.toneMappingExposure=1.08;rr.outputColorSpace=THREE.SRGBColorSpace;
 const sc=new THREE.Scene();sc.environment=new THREE.PMREMGenerator(rr).fromScene(new RoomEnvironment(),.04).texture;sc.add(new THREE.HemisphereLight('#ffffff','#b8c4d0',1.3));const L=new THREE.DirectionalLight('#fff6e8',2.4);L.position.set(-2,8,7);sc.add(L);TR={rr,sc,cm:new THREE.OrthographicCamera(-1,1,1,-1,.1,100),c};return TR;};
const thumb=key=>{let u=TH.get(key);if(u)return u;const {rr,sc,cm,c}=thumbR(),g=proto(key),bx=new THREE.Box3().setFromObject(g),ce=bx.getCenter(new THREE.Vector3()),sz=bx.getSize(new THREE.Vector3()),hh=Math.max(sz.x*.75+sz.z*.75,sz.y*1.1)*.55+.04;
 cm.left=-hh;cm.right=hh;cm.top=hh;cm.bottom=-hh;cm.position.copy(ce).add(new THREE.Vector3(6,5.6,6));cm.lookAt(ce);cm.updateProjectionMatrix();sc.add(g);rr.render(sc,cm);sc.remove(g);u=c.toDataURL();TH.set(key,u);return u;};
const TQ=[];let tqOn=false;const pump=()=>{if(window.__NOTHUMB){tqOn=false;return;}const t=TQ.shift();if(!t){tqOn=false;return;}if(t.img.isConnected)try{t.img.src=thumb(t.key);}catch(e){}setTimeout(pump,0);};
const card=(key,label,on,fn,sw)=>{const b=mkb('',on,fn,label);b.className='card';b.title=label;const v=document.createElement(key?'img':'span');if(key&&key.startsWith('T:')&&!window.__BTX)key=null;v.className='ic';if(key){v.alt='';const u=TH.get(key);if(u)v.src=u;else{TQ.push({key,img:v});if(!tqOn){tqOn=true;setTimeout(pump,0);}}}else if(sw){v.alt='';v.style.background=sw;}else v.textContent='?';const t=document.createElement('span');t.textContent=label;b.append(v,t);return b;};
/* ---- highlight ---- */
const hmOk=new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:.5,depthTest:false}),hmNo=new THREE.MeshBasicMaterial({color:'#ff5a4a',transparent:true,opacity:.55,depthTest:false});
const box=(x,z,ok)=>{const m=new THREE.Mesh(hg,ok?hmOk:hmNo);m.position.set(x+.5,W.hT(x,z)+.16,z+.5);m.renderOrder=99;hi.add(m);};
const show=(tiles)=>{clrH();let ng=0;for(const [x,z] of tiles){if((tool==='bld'||tool==='big')&&ng<16&&!why(x,z)){ghostAt(x,z);ng++;}if(tool==='big'){const [x0,y0,w,d]=bigFp(x,z),ok=!why(x,z);for(let yy=y0;yy<y0+d;yy++)for(let xx=x0;xx<x0+w;xx++)if(xx>0&&yy>0&&xx<N&&yy<N&&W.land(xx,yy))box(xx,yy,ok);}else box(x,z,!why(x,z));}need=true;};
/* ---- pointer ---- */
const P=new Map();let stroke=null,pan=null,pinch=null,space=false,hov=null,hovT=null;
const line=(a,b)=>{const o=[],sx=Math.sign(b[0]-a[0]),sz=Math.sign(b[1]-a[1]);let x=a[0],z=a[1];o.push([x,z]);const xf=Math.abs(b[0]-a[0])>=Math.abs(b[1]-a[1]);
 if(xf){while(x!==b[0]){x+=sx;o.push([x,z]);}while(z!==b[1]){z+=sz;o.push([x,z]);}}else{while(z!==b[1]){z+=sz;o.push([x,z]);}while(x!==b[0]){x+=sx;o.push([x,z]);}}return o;};
const brushOn=()=>tool==='ter'||tool==='hgt'||tool==='del'||(tool==='road'&&selRoad>0),brush=t=>{if(!brushOn()||bs<2)return [t];const o=[],a=-((bs-1)>>1);for(let dz=0;dz<bs;dz++)for(let dx=0;dx<bs;dx++){const x=t[0]+a+dx,z=t[1]+a+dz;if(x>0&&z>0&&x<N-1&&z<N-1&&W.land(x,z))o.push([x,z]);}return o;};
const strokeTo=t=>{if(!t||!stroke)return;if(stroke.mode==='one'){stroke.tiles=[t];}else if(stroke.mode==='line'){stroke.tiles=line(stroke.start,t);}else for(const u of brush(t))if(!stroke.set.has(u[1]*N+u[0])){stroke.set.add(u[1]*N+u[0]);stroke.tiles.push(u);}show(stroke.tiles);};
cv.addEventListener('pointerdown',e=>{cv.focus();cv.setPointerCapture(e.pointerId);P.set(e.pointerId,[e.clientX,e.clientY]);
 if(P.size===2){stroke=null;clrH();pan=null;const [a,b]=[...P.values()];pinch={d:Math.hypot(a[0]-b[0],a[1]-b[1]),mx:(a[0]+b[0])/2,my:(a[1]+b[1])/2};return;}
 if(tool==='move'||e.button!==0||space){pan={x:e.clientX,y:e.clientY,sx:e.clientX,sy:e.clientY,tap:tool==='move'&&e.button===0,rt:e.button===2&&tool!=='move'};return;}
 const t=pick(e.clientX,e.clientY);if(!t)return;flatL=GS.LVL[t[1]*N+t[0]];stroke={start:t,tiles:[],set:new Set(),mode:tool==='road'&&selRoad===0?'line':(tool==='big'||tool==='tree'||(tool==='bld'&&selItem>=0))?'one':'brush'};strokeTo(t);});
cv.addEventListener('pointermove',e=>{
 if(!P.has(e.pointerId)){if(e.pointerType==='mouse'&&tool!=='move'&&W){const t=pick(e.clientX,e.clientY),k=t?t[1]*N+t[0]:-1;if(k!==hov){hov=k;hovT=t;show(t?brush(t):[]);}}return;}
 P.set(e.pointerId,[e.clientX,e.clientY]);
 if(pinch&&P.size===2){const [a,b]=[...P.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]),mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;panPx(mx-pinch.mx,my-pinch.my);zoomAt(pinch.d/d,mx,my);pinch={d,mx,my};return;}
 if(pan){panPx(e.clientX-pan.x,e.clientY-pan.y);pan.x=e.clientX;pan.y=e.clientY;return;}
 if(stroke)strokeTo(pick(e.clientX,e.clientY));});
const up=e=>{if(!P.has(e.pointerId))return;P.delete(e.pointerId);if(P.size<2)pinch=null;
 if(pan){const tp=Math.hypot(e.clientX-pan.sx,e.clientY-pan.sy)<6;if(pan.tap&&tp){const t=pick(e.clientX,e.clientY);if(t)msg(info(t[0],t[1]));}else if(pan.rt&&tp)setTool('move');pan=null;}
 if(stroke){const t=stroke.tiles;stroke=null;hov=null;commit(t);}};
cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',e=>{P.delete(e.pointerId);pinch=null;pan=null;if(stroke){stroke=null;clrH();need=true;}});
cv.addEventListener('pointerleave',()=>{if(!stroke&&hov!==null){hov=null;clrH();need=true;}});cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{e.preventDefault();zoomAt(Math.exp(e.deltaY*.0012),e.clientX,e.clientY);},{passive:false});
/* ---- UI ---- */
const TOOLS=[['move','이동','탭하면 정보'],['road','길','차도는 직선 · 물 위엔 다리'],['bld','건물','R 회전 · ESC 취소'],['big','시설','R 회전 · ESC 취소'],['ter','지형','드래그로 칠하기'],['hgt','높이','구덩이는 벽을 눌러도 선택'],['tree','나무','탭'],['del','철거','드래그']];
const mkb=(t,on,fn,lab)=>{const b=document.createElement('button');b.textContent=t;if(on!==null)b.setAttribute('aria-pressed',on?'true':'false');if(lab)b.setAttribute('aria-label',lab);b.onclick=fn;return b;};
const setTool=id=>{if(id==='bld'&&tool!=='bld')rollRand();tool=id;stroke=null;hov=null;clrH();need=true;drawUI();const t=TOOLS.find(t=>t[0]===id);msg(t[1]+' · '+t[2]);};
const drawUI=()=>{const bar=$('bar');bar.replaceChildren(...TOOLS.map(([id,t])=>mkb(t,tool===id,()=>setTool(id))));const on=bar.querySelector('[aria-pressed="true"]');if(on&&on.scrollIntoView)on.scrollIntoView({block:'nearest',inline:'nearest'});
 const pk=$('pick');pk.hidden=!['bld','big','ter','road','hgt','del'].includes(tool);if(pk.hidden)return;const O=window.__O,re=()=>{drawUI();if(hovT)show(brush(hovT));};
 $('cats').hidden=false;const sizes=()=>{const l=document.createElement('span');l.className='sep';return [l,...[1,2,3].map(v=>{const b=mkb(v+'×'+v,bs===v,()=>{bs=v;re();},'붓 크기 '+v);b.className='dir';return b;})];};
 if(tool==='ter'){$('cats').replaceChildren(...sizes().slice(1));$('items').replaceChildren(...TERS.map(([t,,k],i)=>card(k,t,selTer===i,()=>{selTer=i;re();})));return;}
 if(tool==='road'){$('cats').replaceChildren(...(selRoad?sizes().slice(1):[]));$('cats').hidden=!selRoad;$('items').replaceChildren(...ROADS.map(([t,k],i)=>card(k,t,selRoad===i,()=>{selRoad=i;re();})));return;}
 if(tool==='hgt'){$('items').replaceChildren(...HGT.map((t,i)=>mkb(t,selH===i,()=>{selH=i;re();})));$('cats').replaceChildren(...sizes().slice(1));return;}
 if(tool==='del'){$('items').replaceChildren(...sizes().slice(1));$('cats').hidden=true;return;}
 const dirs=(tool==='bld'?[['자동',0]]:[]).concat([['↙',1],['↘',2],['↗',3],['↖',4]]),cur=tool==='big'?(rot||1):rot,dl=document.createElement('span');dl.className='sep';
 const db=dirs.map(([t,v])=>{const b=mkb(t,cur===v,()=>{rot=v;re();},v?'방향 '+t:'방향 자동');b.className='dir';b.title='방향 (R)';return b;});
 if(tool==='bld'){$('cats').replaceChildren(...CATS.map((c,i)=>mkb(c[1],selCat===i,()=>{selCat=i;selItem=-1;rollRand();re();})),dl,...db);const c=CATS[selCat][0];
  $('items').replaceChildren(card(null,'무작위',selItem<0,()=>{selItem=-1;rollRand();re();}),...O.CAT[c].map((e,i)=>card(c+':'+i+':z+',e[0],selItem===i,()=>{selItem=i;re();})));}
 else{$('cats').replaceChildren(...db);$('items').replaceChildren(...O.BIG.map((e,i)=>card('B:'+i+':z+',e[0],selBig===i,()=>{selBig=i;re();})));}};
const syncTop=()=>{$('undo').disabled=!UN.length;$('redo').disabled=!RE.length;};
const syncMo=()=>{$('mo').setAttribute('aria-pressed',motion?'true':'false');clouds.visible=motion;lod();r.shadowMap.needsUpdate=true;need=true;};$('mo').onclick=()=>{motion=!motion;try{localStorage.setItem('isle3d-motion',motion?'1':'0');}catch(e){}syncMo();};
$('undo').onclick=undo;$('redo').onclick=redo;$('zin').onclick=()=>zoomAt(.75,innerWidth/2,innerHeight/2);$('zout').onclick=()=>zoomAt(1.33,innerWidth/2,innerHeight/2);$('fit').onclick=fit;
let rs=0;$('reset').onclick=()=>{if(Date.now()-rs>2500){rs=Date.now();msg('한 번 더 누르면 처음 도시로',2500);return;}rs=0;try{localStorage.removeItem(SKEY);}catch(e){}GS=fresh();ED.fb=new Map();ED.big=null;ED.frozen=false;UN.length=0;RE.length=0;msg('처음 도시로',0);setTimeout(()=>{boot();syncTop();},16);};
addEventListener('keydown',e=>{if(e.target.tagName==='INPUT')return;const k=e.key;
 if((e.ctrlKey||e.metaKey)&&k.toLowerCase()==='z'){e.preventDefault();e.shiftKey?redo():undo();return;}if((e.ctrlKey||e.metaKey)&&k.toLowerCase()==='y'){e.preventDefault();redo();return;}if(e.ctrlKey||e.metaKey||e.altKey)return;
 if(k===' '){space=true;e.preventDefault();}else if(k==='Escape'){if(stroke){stroke=null;clrH();need=true;}else setTool('move');}
 else if(k>='1'&&k<='9'&&TOOLS[+k-1])setTool(TOOLS[+k-1][0]);
 else if((k==='['||k===']')&&brushOn()){bs=Math.max(1,Math.min(3,bs+(k===']'?1:-1)));drawUI();if(hovT)show(brush(hovT));msg('붓 '+bs+'×'+bs,800);}
 else if((k==='r'||k==='R')&&(tool==='bld'||tool==='big')){rot=(tool==='big'?(rot||1):rot)%4+1;drawUI();if(hovT)show([hovT]);msg('방향 '+['','↙','↘','↗','↖'][rot],900);}else if(k==='+'||k==='=')zoomAt(.8,innerWidth/2,innerHeight/2);else if(k==='-')zoomAt(1.25,innerWidth/2,innerHeight/2);else if(k==='0')fit();
 else if(k.startsWith('Arrow')){e.preventDefault();const s=90;panPx(k==='ArrowLeft'?s:k==='ArrowRight'?-s:0,k==='ArrowUp'?s:k==='ArrowDown'?-s:0);}});
addEventListener('keyup',e=>{if(e.key===' ')space=false;});
const boot=()=>{const had=load();rebuild();if(!had){ED.fb=new Map(W.PLACED.map(p=>[p[0],[p[1],p[2]]]));ED.big=W.BIGP.map(b=>b.slice());ED.frozen=true;}drawUI();msg('');};
resize();setTimeout(()=>{boot();fit();syncTop();syncMo();requestAnimationFrame(loop);window.__ready=1;},30);

window.__dbg={show:(t,x,z,r)=>{tool=t;rot=r||0;drawUI();show([[x,z]]);need=true;return GH.children.length+' '+why(x,z);},sim:s=>{for(let k=0;k<Math.round(s/.1);k++){lastT=performance.now()-100;tick(performance.now());}},edit:(t,tiles,sel,o={})=>{tool=t;if(sel!==undefined)selTer=sel;if(o.road!==undefined)selRoad=o.road;if(o.h!==undefined)selH=o.h;if(o.L!==undefined)flatL=o.L;commit(tiles);return why(tiles[0][0],tiles[0][1])||"ok";},ppl:()=>PPL,thumb:k=>{try{return thumb(k).length}catch(e){return String(e.stack||e)}},ghost:(x,z)=>{try{tool="bld";ghostAt(x,z);return GH.children.length}catch(e){return String(e.stack||e)}},cars:()=>CARS,step:s=>{lastT=performance.now()-s*1000;const m=motion;motion=true;syncMo();for(let k=0;k<Math.ceil(s/.1);k++){lastT=performance.now()-100;tick(performance.now());}r.shadowMap.needsUpdate=true;r.render(W.sc,cam);motion=m;},clouds,pick,cam,V,W:()=>W,GS:()=>GS,go:(x,z,k)=>{V.tx=x;V.tz=z;V.k=k;setCam();},rebuild};
