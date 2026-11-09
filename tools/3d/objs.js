
const OBJ=(THREE,RoundedBoxGeometry,root)=>{let cur=root;const sc={add:o=>cur.add(o)};
const M=(c,o={})=>new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.6,metalness:0,envMapIntensity:.12},o));
const add=(g,m,x,y,z,sh=true)=>{const e=new THREE.Mesh(g,m);e.position.set(x,y,z);e.castShadow=sh;e.receiveShadow=true;cur.add(e);return e;};
const RB=(w,h,d,rad=.06)=>new RoundedBoxGeometry(w,h,d,3,Math.max(.001,Math.min(rad,w/2-.002,h/2-.002,d/2-.002)));
const bx=(x0,x1,y0,y1,z0,z1,m,rad=.06,sh=true)=>add(RB(x1-x0,y1-y0,z1-z0,rad),m,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,sh);
const at=(ax,az,ox,oz,fn)=>{const g=new THREE.Group();g.position.set(ax-ox,0,az-oz);root.add(g);cur=g;fn();cur=root;};
const TRK=M('#9a7556',{roughness:.7}),PIT=M('#8a6a4a',{roughness:.9}),LEAF=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.65,envMapIntensity:.4});let TI=0;
const PAL=[['#3fa83a','#7fdc5a'],['#2f9e4a','#6fd06a'],['#46b04a','#8ee06a']];
const crown=(r,sy,seed,pal)=>{const g=new THREE.IcosahedronGeometry(r,5);const p=g.attributes.position,col=[],c0=new THREE.Color(pal[0]),c1=new THREE.Color(pal[1]),v=new THREE.Vector3();
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);const n=v.clone().normalize();const d=1+.035*Math.sin(n.x*4+seed)*Math.cos(n.y*3+seed*1.3)+.02*Math.sin(n.z*5+n.y*3+seed*2.1);
  v.copy(n).multiplyScalar(r*d);v.y*=sy;p.setXYZ(i,v.x,v.y,v.z);const t=Math.min(1,Math.max(0,n.y*.5+.55));const c=c0.clone().lerp(c1,t);col.push(c.r,c.g,c.b);}
 g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.computeVertexNormals();return g;};
const bush=(x,z,r=.16)=>{ao(x-.08,x+.08,z-.08,z+.08,.143,.06);const B0=.13,k=.16/.16*1.35,v=3+0*(TI++),pal=PAL[(TI*5)%3],sd=TI*1.7;add(new THREE.CylinderGeometry(.08*k,.085*k,.025,24),PIT,x,B0+.012,z,false);
 if(v===3){add(new THREE.CylinderGeometry(.016*k,.02*k,.08*k,10),TRK,x,B0+.04*k,z);add(crown(.1*k,2.5,sd,pal),LEAF,x,B0+.32*k,z);return;}
 const tr=add(new THREE.CylinderGeometry(.014*k,.024*k,.26*k,10),TRK,x,B0+.13*k,z);
 add(new THREE.CylinderGeometry(.006*k,.01*k,.12*k,8),TRK,x+.03*k,B0+.24*k,z+.01*k).rotation.z=-.7;
 add(crown(.15*k,1.0,sd,pal),LEAF,x,B0+.37*k,z);
 if(v===1)add(crown(.1*k,1,sd+3,pal),LEAF,x+.08*k,B0+.3*k,z+.07*k);
 if(v===2){add(crown(.07*k,.9,sd+5,pal),LEAF,x+.12*k,B0+.07*k,z+.05*k);add(crown(.06*k,.9,sd+7,pal),LEAF,x-.1*k,B0+.06*k,z+.08*k);}};

const AOT=(()=>{const cv=document.createElement('canvas');cv.width=cv.height=128;const g=cv.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,128,128);g.filter='blur(12px)';g.fillStyle='#fff';g.fillRect(30,30,68,68);return new THREE.CanvasTexture(cv);})();
const AOM=new THREE.MeshBasicMaterial({color:'#1b2a3a',alphaMap:AOT,transparent:true,opacity:.6,depthWrite:false});
const ao=(x0,x1,z0,z1,y=.142,pad=.3)=>{const w=x1-x0+pad*2,d=z1-z0+pad*2,S2=128,cv=document.createElement('canvas');cv.width=cv.height=S2;const g=cv.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,S2,S2);g.filter='blur('+Math.round(S2*pad/Math.max(w,d)*.6)+'px)';g.fillStyle='#fff';g.fillRect(S2*pad/w*.6,S2*pad/d*.6,S2*(1-1.2*pad/w),S2*(1-1.2*pad/d));
 const mat=new THREE.MeshBasicMaterial({color:'#1d2836',alphaMap:new THREE.CanvasTexture(cv),transparent:true,opacity:.78,depthWrite:false});const m=new THREE.Mesh(new THREE.PlaneGeometry(w,d),mat);m.rotation.x=-Math.PI/2;m.position.set((x0+x1)/2,y,(z0+z1)/2);m.renderOrder=1;sc.add(m);};

const car=(x,z,alongX,c)=>{const g=new THREE.Group();const pm=M(c,{roughness:.25,metalness:.35,envMapIntensity:.9}),gl=new THREE.MeshPhysicalMaterial({color:'#1f2a3a',roughness:.05,metalness:.3,clearcoat:1,envMapIntensity:1.2}),tm=M('#1a1c20',{roughness:.7});
 const m=(geo,mat,px,py,pz)=>{const e=new THREE.Mesh(geo,mat);e.position.set(px,py,pz);e.castShadow=true;g.add(e);return e;};
 m(RB(.72,.13,.32,.05),pm,0,.12,0);m(RB(.4,.12,.29,.05),gl,-.04,.23,0);m(RB(.34,.03,.27,.012),pm,-.04,.295,0);
 for(const [wx,wz] of [[.22,.15],[-.22,.15],[.22,-.15],[-.22,-.15]]){const w=m(new THREE.CylinderGeometry(.07,.07,.06,16),tm,wx,.07,wz);w.rotation.x=Math.PI/2;const hub=m(new THREE.CylinderGeometry(.035,.035,.065,12),M('#cfd4db',{metalness:.6,roughness:.3}),wx,.07,wz);hub.rotation.x=Math.PI/2;}
 const hl=new THREE.MeshStandardMaterial({color:'#fff6d8',emissive:'#fff1c0',emissiveIntensity:.6});for(const zz of [.1,-.1]){m(new THREE.BoxGeometry(.02,.03,.06),hl,.36,.14,zz);m(new THREE.BoxGeometry(.02,.03,.06),M('#e0333a',{emissive:'#a01018',emissiveIntensity:.4}),-.36,.14,zz);}
 g.position.set(x,0,z);if(!alongX)g.rotation.y=Math.PI/2;sc.add(g);alongX?ao(x-.36,x+.36,z-.16,z+.16,.016,.06):ao(x-.16,x+.16,z-.36,z+.36,.016,.06);};
const FH=.32,B=.13;
 const FACC=new Map();const fac=(wu,fl,o)=>{const fk=(o.__k||(o.__k=Math.random()))+'|'+wu.toFixed(2)+'|'+fl;if(FACC.has(fk))return FACC.get(fk);const __t=(()=>{const W=Math.max(64,Math.round(wu*96)),H=fl*48,SS=2,cv=document.createElement('canvas');cv.width=W*SS;cv.height=H*SS;const g=cv.getContext('2d');g.scale(SS,SS);g.fillStyle=o.wall;g.fillRect(0,0,W,H);
  const cols=Math.max(1,Math.round(wu/(o.ww||.36)));const cw=W/cols;
  for(let f=0;f<fl;f++){const y=H-(f+1)*48;
   if(f===0&&o.shop){g.fillStyle='#9fd0f5';g.fillRect(4,y+14,W-8,34);g.fillStyle='rgba(255,255,255,.5)';for(let i=1;i<cols;i++)g.fillRect(i*cw-1,y+14,2,34);g.fillStyle=o.shop;g.fillRect(0,y+2,W,12);continue;}
   if(o.stone){g.fillStyle=o.wall;g.fillRect(0,y,W,48);if(f===0){g.fillStyle='#4b5462';g.fillRect(6,y+10,W-12,38);g.fillStyle='rgba(160,200,235,.6)';g.fillRect(10,y+14,W-20,30);continue;}
    for(let i=0;i<cols;i++){g.fillStyle='#4a5260';g.fillRect(i*cw+cw*.14,y+8,cw*.72,34);g.fillStyle='#93bfe2';g.fillRect(i*cw+cw*.2,y+11,cw*.6,28);g.fillStyle='rgba(255,255,255,.55)';g.fillRect(i*cw+cw*.2,y+11,cw*.6,4);}
    g.fillStyle='rgba(255,255,255,.35)';for(let i=0;i<=cols;i++)g.fillRect(i*cw-3,y,6,48);continue;}
   if(o.band){const gl=f%1===0;g.fillStyle='#f4f5f7';g.fillRect(0,y,W,48);g.fillStyle=f===0?'#6f6a64':'#7f95a8';g.fillRect(0,y+12,W,26);const gr=g.createLinearGradient(0,y+12,W,y+38);gr.addColorStop(0,'rgba(140,190,240,.55)');gr.addColorStop(.6,'rgba(140,190,240,.1)');g.fillStyle=gr;g.fillRect(0,y+12,W,26);continue;}
   if(o.brick){if(f===0&&o.piloti){g.fillStyle='#2e333b';g.fillRect(0,y,W,48);g.fillStyle='#d8d2c8';for(let i=0;i<=cols;i++)g.fillRect(Math.min(W-10,i*cw),y,10,48);g.fillStyle='#e8e2d8';g.fillRect(0,y,W,6);continue;}
    g.fillStyle=o.wall;g.fillRect(0,y,W,48);g.fillStyle='rgba(0,0,0,.12)';for(let r=0;r<6;r++){g.fillRect(0,y+r*8,W,1);for(let c=(r%2)*8;c<W;c+=16)g.fillRect(c,y+r*8,1,8);}
    for(let i=0;i<cols;i++){g.fillStyle='#ffffff';g.fillRect(i*cw+cw*.2-3,y+10,cw*.6+6,30);g.fillStyle='#8fc3ee';g.fillRect(i*cw+cw*.2,y+13,cw*.6,24);g.fillStyle='#ffffff';g.fillRect(i*cw+cw*.5-1,y+13,2,24);}
    if(o.balc){g.fillStyle='rgba(60,66,76,.85)';g.fillRect(cw*.1,y+30,cw*.8,10);}continue;}
   if(o.wood){g.fillStyle='#f7f5f1';g.fillRect(0,y,W,48);if(f===0){g.fillStyle='#9cc9ec';g.fillRect(6,y+6,W-12,42);g.fillStyle='rgba(255,255,255,.6)';for(let i=1;i<cols;i++)g.fillRect(i*cw-1,y+6,2,42);g.fillStyle='#3e434c';g.fillRect(0,y+2,W,5);continue;}
    g.fillStyle='#9cc9ec';g.fillRect(8,y+8,W*.55,36);g.fillStyle='#a8774f';for(let x=W*.62;x<W-6;x+=9)g.fillRect(x,y,5,48);continue;}
   if(o.signs2){g.fillStyle=o.wall;g.fillRect(0,y,W,48);if(f===0){g.fillStyle='#9fd0f5';g.fillRect(4,y+14,W-8,34);g.fillStyle=o.signs2[0];g.fillRect(0,y+2,W,12);if(o.cross){g.fillStyle='#fff';g.fillRect(W*.1,y+4,12,8);g.fillRect(W*.1+4,y,4,16);}continue;}
    for(let i=0;i<cols;i++){g.fillStyle='#ffffff';g.fillRect(i*cw+cw*.15-2,y+15,cw*.7+4,27);g.fillStyle='#8fc3ee';g.fillRect(i*cw+cw*.15,y+17,cw*.7,23);}
    g.fillStyle=o.signs2[f%o.signs2.length];g.fillRect(W*.06,y+2,W*.88,10);g.fillStyle='rgba(255,255,255,.85)';g.fillRect(W*.1,y+5,W*.3,4);continue;}
   if(o.gl){const lob=f===0;g.fillStyle=lob?'#5d6878':'#8db6d8';g.fillRect(0,y,W,48);if(!lob){const gr=g.createLinearGradient(0,y,W,y+48);gr.addColorStop(0,'rgba(255,255,255,.35)');gr.addColorStop(.5,'rgba(255,255,255,0)');g.fillStyle=gr;g.fillRect(0,y,W,48);}
    g.fillStyle=o.mull||'#3e434c';for(let i=0;i<=cols;i++)g.fillRect(Math.min(W-3,i*cw-1.5),y,o.mull?5:3,48);g.fillStyle='rgba(235,240,246,.9)';g.fillRect(0,y+44,W,4);if(f===fl-1){g.fillStyle='#c09a62';g.fillRect(0,y,W,6);}continue;}
   if(o.hs){const st=false,BR='#8a7562',BRd='#7a6655',WP='#f3f2ef';let s0=0;for(let i=0;i<W;i++);
    const gx0=W*.07,gx1=W*.40,px1=W*.47;
    g.fillStyle=st?BRd:BR;g.fillRect(0,y,W,48);
    /* glass curtain zone */const gr=g.createLinearGradient(gx0,y,gx1,y+48);gr.addColorStop(0,'#9fb9d2');gr.addColorStop(1,'#7f9cba');g.fillStyle=gr;g.fillRect(gx0,y,gx1-gx0,48);
    if(!st){const lit=((f*7+3)%5)<2;if(lit){g.fillStyle='rgba(255,214,150,.55)';g.fillRect(gx0+4,y+8,(gx1-gx0)*.55,34);}g.fillStyle='rgba(235,240,246,.9)';g.fillRect(gx0,y+44,gx1-gx0,4);g.fillStyle='rgba(255,255,255,.35)';g.fillRect((gx0+gx1)/2-1,y,2,44);}
    /* white pilasters */g.fillStyle=WP;g.fillRect(0,y,gx0,48);g.fillRect(gx1,y,px1-gx1,48);g.fillStyle='rgba(0,0,0,.06)';g.fillRect(gx1,y,3,48);
    /* bronze zone windows */const n=Math.max(2,Math.round((W-px1)/(cw*1.1)));const ww=(W-px1)/n;
    for(let i=0;i<n;i++){const wx=px1+i*ww+ww*.18,wW=ww*.64;g.fillStyle='#d8d2c8';g.fillRect(wx-2,y+7,wW+4,36);const lit=((i*5+f*3)%7)<2;g.fillStyle=lit?'#e7c48e':'#4a5866';g.fillRect(wx,y+9,wW,32);g.fillStyle='rgba(255,255,255,.25)';g.fillRect(wx,y+9,wW,4);g.fillStyle='#d8d2c8';g.fillRect(wx+wW/2-1,y+9,2,32);}
    if(st){g.fillStyle='#a7bccc';g.fillRect(px1+6,y+10,W-px1-12,38);}continue;}
   if(o.bal){g.fillStyle='#a9d4f5';g.fillRect(6,y+12,W-12,26);g.fillStyle='rgba(255,255,255,.85)';g.fillRect(6,y+30,W-12,10);g.fillStyle='rgba(0,0,0,.08)';for(let i=1;i<cols;i++)g.fillRect(i*cw-2,y+12,4,28);continue;}
   for(let i=0;i<cols;i++){g.fillStyle=o.frame||'#ffffff';g.fillRect(i*cw+cw*.18-2,y+11,cw*.64+4,28);g.fillStyle=(i*7+f*3)%5===0?'#cfe8fb':'#8fc3ee';g.fillRect(i*cw+cw*.18,y+13,cw*.64,24);}
   if(o.signs&&f>0&&f<fl){g.fillStyle=o.signs[f%o.signs.length];g.fillRect(cw*.1,y+2,Math.min(W*.5,cw*1.6),8);}}
  const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=16;t.generateMipmaps=true;t.minFilter=THREE.LinearMipmapLinearFilter;return t;})();FACC.set(fk,__t);return __t;};
 const bld=(x0,x1,z0,z1,fl,o)=>{const h=fl*FH,w=x1-x0,d=z1-z0;ao(x0,x1,z0,z1);const wm=M(o.wall,{roughness:.7,envMapIntensity:.3});const pf=o.pil||0,hp=pf*FH;const mx=new THREE.MeshStandardMaterial({map:fac(d,fl-pf,o),roughness:.6,envMapIntensity:.3}),mz=new THREE.MeshStandardMaterial({map:fac(w,fl-pf,o),roughness:.6,envMapIntensity:.3});
  add(new THREE.BoxGeometry(w,h-hp,d),[mx,wm,M(o.roof||'#cfd5de',{roughness:.8}),pf?M('#f1efea',{roughness:.5}):wm,mz,wm],(x0+x1)/2,B+hp+(h-hp)/2,(z0+z1)/2);
  if(pf){const lb=new THREE.MeshPhysicalMaterial({color:'#b7cfe2',roughness:.05,metalness:.2,clearcoat:1,envMapIntensity:1.2}),cw=M('#f3f2ef',{roughness:.35}),st=M('#8a7562',{roughness:.5});
   bx(x0+.28,x1-.28,B,B+hp-.02,z0+.28,z1-.28,st,.02);bx(x0+.6,x1-.6,B,B+hp-.04,z1-.29,z1-.27,lb,.005,false);bx(x1-.29,x1-.27,B,B+hp-.04,z0+.5,z1-.5,lb,.005,false);
   const cols=[];for(let t=x0+.08;t<=x1-.08+.001;t+=Math.max(.3,(x1-x0-.16)/Math.round((x1-x0-.16)/.45)))cols.push([t,z1-.08]);for(let t=z0+.08;t<z1-.1;t+=Math.max(.3,(z1-z0-.16)/Math.round((z1-z0-.16)/.45)))cols.push([x1-.08,t]);
   for(const [cx_,cz_] of cols)add(RB(.09,hp,.09,.03),cw,cx_,B+hp/2,cz_);
   const mz_=(x0+x1)/2;bx(mz_-.42,mz_+.42,B+hp*.62,B+hp*.62+.05,z1-.1,z1+.42,cw,.02);for(const px of [mz_-.38,mz_+.35])add(RB(.04,hp*.62,.04,.01),cw,px,B+hp*.31,z1+.38);
   bx(mz_-.46,mz_+.46,B,B+.025,z1-.3,z1+.48,M('#e6e0d6',{roughness:.6}),.01,false);}
  const pm=M(o.wall,{roughness:.7}),ph=.07,pt=.05;bx(x0,x1,B+h,B+h+ph,z0,z0+pt,pm,.01);bx(x0,x1,B+h,B+h+ph,z1-pt,z1,pm,.01);bx(x0,x0+pt,B+h,B+h+ph,z0,z1,pm,.01);bx(x1-pt,x1,B+h,B+h+ph,z0,z1,pm,.01);
  if(o.trim){const gm=M('#c09a62',{roughness:.3,metalness:.6});bx(x0-.005,x1+.005,B+h+.05,B+h+.075,z1-.055,z1+.005,gm,.005,false);bx(x1-.055,x1+.005,B+h+.05,B+h+.075,z0-.005,z1+.005,gm,.005,false);}
  if(o.crown===2){const wm=M('#f6f6f4',{roughness:.3,envMapIntensity:.6}),gz=new THREE.MeshPhysicalMaterial({color:'#c9dcea',roughness:.05,metalness:.15,transparent:true,opacity:.55,envMapIntensity:1.3}),lt=new THREE.MeshStandardMaterial({color:'#fff4dc',emissive:'#ffe2a8',emissiveIntensity:.6}),y=B+h,H2=.95,t=.09;
   bx(x0,x1,y,y+.06,z0,z1,M('#d9d6d0'),.02);
   /* tall portal frame on front face */bx(x0+.02,x0+.02+t,y,y+H2,z1-.28,z1,wm,.02);bx(x1-t,x1,y,y+H2,z1-.28,z1,wm,.02);bx(x0+.02,x1,y+H2-t,y+H2,z1-.28,z1,wm,.02);
   for(let i=1;i<9;i++){const xx=x0+.02+t+(x1-x0-.02-2*t)*i/9;bx(xx-.012,xx+.012,y+.06,y+H2-t,z1-.06,z1-.03,wm,.004);}
   bx(x0+.02+t,x1-t,y+.06,y+H2-t,z1-.2,z1-.18,gz,.003,false);bx(x0+.15,x1-.15,y+H2-t-.03,y+H2-t,z1-.02,z1+.005,lt,.004,false);
   /* side portal on +x face */bx(x1-.28,x1,y,y+H2*.7,z0+.02,z0+.02+t,wm,.02);bx(x1-.28,x1,y+H2*.7-t,y+H2*.7,z0+.02,z1-.28,wm,.02);
   for(let i=1;i<5;i++){const zz=z0+.02+t+(z1-.28-z0-.02-t)*i/5;bx(x1-.06,x1-.03,y+.06,y+H2*.7-t,zz-.012,zz+.012,wm,.004);}
   /* roof garden + pavilion */bx(x0+.15,x1-.45,y+.06,y+.1,z0+.15,z1-.4,M('#8fcf72',{roughness:.8}),.02,false);bx(x0+.35,x0+.95,y+.06,y+.36,z0+.2,z0+.55,M('#eeebe5'),.03);bx(x0+.3,x0+1.0,y+.36,y+.4,z0+.15,z0+.6,wm,.02);}
  else if(o.crown){const wm=M('#f6f6f4',{roughness:.3,envMapIntensity:.6}),dg=M('#5a6470',{roughness:.3,metalness:.3}),lt=new THREE.MeshStandardMaterial({color:'#fff4dc',emissive:'#ffe2a8',emissiveIntensity:.6}),y=B+h;
   bx(x0+.04,x1-.04,y,y+.06,z0+.04,z1-.04,M('#d9d6d0'),.02);bx(x0+.02,x0+.08,y,y+.12,z0,z1,M('#cfcbc4'),.01);bx(x0,x1,y,y+.12,z0,z0+.06,M('#cfcbc4'),.01);
   const cx0=x0+w*.04,cx1=x1,cz0=z0+d*.25,cz1=z1;const L=[[.04,.07],[.16,.05],[.26,.05],[.36,.05],[.46,.07]];
   add(RB(cx1-cx0-.1,.5,cz1-cz0-.1,.06),dg,(cx0+cx1)/2-.03,y+.25,(cz0+cz1)/2-.03);
   for(const [o,t] of L)add(RB(cx1-cx0+.02,t,cz1-cz0+.02,.22),wm,(cx0+cx1)/2,y+o+t/2,(cz0+cz1)/2);add(RB(cx1-cx0-.14,.02,cz1-cz0-.14,.1),dg,(cx0+cx1)/2,y+.535,(cz0+cz1)/2,false);
   add(RB(cx1-cx0+.04,.015,cz1-cz0+.04,.24),lt,(cx0+cx1)/2,y+.535,(cz0+cz1)/2,false);
   bx(cx0+.15,cx1-.25,y+.12,y+.36,cz1+.02,cz1+.035,lt,.005,false);}
  if(o.tank){add(new THREE.CylinderGeometry(.13,.13,.22,16),M('#6fa7d8',{roughness:.5}),x0+w*.3,B+h+.11,z0+d*.35);bx(x0+w*.55,x0+w*.85,B+h,B+h+.28,z0+d*.15,z0+d*.45,M('#e9e4da'),.02);}
  if(o.ac)for(let i=0;i<o.ac;i++)bx(x0+.15+i*.25,x0+.33+i*.25,B+h,B+h+.1,z1-.35,z1-.17,M('#d9dde3'),.02);
  if(o.pitch){const sp=new THREE.Shape();sp.moveTo(-d/2-.06,0);sp.lineTo(d/2+.06,0);sp.lineTo(0,.42);sp.lineTo(-d/2-.06,0);const g=new THREE.ExtrudeGeometry(sp,{depth:w+.08,bevelEnabled:true,bevelThickness:.02,bevelSize:.02,bevelSegments:2});g.translate(0,0,-(w+.08)/2);const e=add(g,M(o.pitch,{roughness:.5}),(x0+x1)/2,B+h,(z0+z1)/2);e.rotation.y=Math.PI/2;}
  if(o.stripe){const cv=document.createElement('canvas');cv.width=64;cv.height=8;const g2=cv.getContext('2d');for(let i=0;i<8;i++){g2.fillStyle=i%2?'#ffffff':o.stripe;g2.fillRect(i*8,0,8,8);}const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=THREE.RepeatWrapping;t.repeat.set(w*2,1);const am=new THREE.MeshStandardMaterial({map:t,roughness:.6});
   const aw=add(new THREE.BoxGeometry(w-.06,.03,.26),am,(x0+x1)/2,B+FH*.98,z1+.11);aw.rotation.x=.4;const t2=t.clone();t2.repeat.set(d*2,1);t2.needsUpdate=true;const aw2=add(new THREE.BoxGeometry(.26,.03,d-.06),new THREE.MeshStandardMaterial({map:t2,roughness:.6}),x1+.11,B+FH*.98,(z0+z1)/2);aw2.rotation.z=-.4;aw2.rotation.y=0;}
  if(o.awn){const aw=add(new THREE.BoxGeometry(w-.1,.03,.22),M(o.awn,{roughness:.5}),(x0+x1)/2,B+FH*.95,z1+.09);aw.rotation.x=.35;const aw2=add(new THREE.BoxGeometry(.22,.03,d-.1),M(o.awn,{roughness:.5}),x1+.09,B+FH*.95,(z0+z1)/2);aw2.rotation.z=-.35;}};
 const house=(x0,x1,z0,z1,roof)=>{const h=.5,w=x1-x0,d=z1-z0;add(new THREE.BoxGeometry(w,h,d),[M('#fbf7f0'),M('#fbf7f0'),M('#fbf7f0'),M('#fbf7f0'),M('#fbf7f0'),M('#fbf7f0')],(x0+x1)/2,B+h/2,(z0+z1)/2);
  for(const [px,pz,f] of [[x1+.005,(z0+z1)/2,'x'],[(x0+x1)/2,z1+.005,'z']]){const wn=add(new THREE.BoxGeometry(f==='x'?.01:.22,.2,f==='x'?.22:.01),M('#8fc3ee'),px,B+.27,pz,false);}
  const sp=new THREE.Shape();sp.moveTo(-w/2-.08,0);sp.lineTo(w/2+.08,0);sp.lineTo(0,.38);sp.lineTo(-w/2-.08,0);const g=new THREE.ExtrudeGeometry(sp,{depth:d+.1,bevelEnabled:true,bevelThickness:.02,bevelSize:.02,bevelSegments:2});g.translate(0,0,-(d+.1)/2);add(g,M(roof,{roughness:.55}),(x0+x1)/2,B+h,(z0+z1)/2);};
 const APT={wall:'#8a7562',hs:1,crown:1,roof:'#c9c6c0',ww:.3,pil:2},OFF={wall:'#e6e3de',gl:1,ww:.22,roof:'#c9c6c0',trim:1},
  SHOP={wall:'#f3efe8',frame:'#3e434c',shop:'#3e434c',signs:['#ff7a59','#3d9df5'],roof:'#cfcac2',trim:1},VIL={wall:'#ddd3c4',frame:'#3e434c',roof:'#c4bcb0',trim:1,ww:.42},CVS={wall:'#f6f4ef',shop:'#1fb5a5',awn:'#3e434c',trim:1,roof:'#dfe3ea',ac:2};
 const STONE={wall:'#d9cfbf',stone:1,ww:.3,roof:'#c9c2b6',trim:1},BAND={wall:'#f4f5f7',band:1,roof:'#d6d9de',trim:1,ac:3},
  BRICK={wall:'#b9694c',brick:1,piloti:1,balc:1,ww:.38,roof:'#c4bcb0',tank:1},GBRICK={wall:'#8f8c88',brick:1,balc:1,ww:.36,roof:'#bdb8b0'},
  WOOD={wall:'#f7f5f1',wood:1,roof:'#d9d6d0',trim:1},TOWN={wall:'#f5f2ec',frame:'#3e434c',ww:.36,pitch:'#5d6470'},
  NEIGH={wall:'#f1ece4',signs2:['#3d9df5','#ff7a59','#ffc23d','#1fb5a5','#8f7be0'],roof:'#d3cdc4',ac:2},
  BAKE={wall:'#f6efe4',frame:'#7a4b33',shop:'#7a4b33',stripe:'#d9534f',ww:.38,roof:'#d6cfc4'},
  PHAR={wall:'#f4f6f8',signs2:['#1fb5a5','#3d9df5','#ffffff'],cross:1,roof:'#d6d9de',trim:1};

 const wm=M('#ffffff',{roughness:.4}),dk=M('#3e434c',{roughness:.4}),glz=new THREE.MeshPhysicalMaterial({color:'#bfe2ff',roughness:.05,transparent:true,opacity:.35,envMapIntensity:1.2});
const B=.13;
const gas=(x,z)=>at(x,z,-4.55,3.3,()=>{/* gas station */{const x0=-4.55,x1=-3.3,z0=3.3,z1=4.55,yc=B+.62;ao(x0+.1,x1-.1,z0+.2,z1-.1,.142,.1);for(const [px,pz] of [[x0+.2,z0+.25],[x1-.25,z0+.25],[x0+.2,z1-.2],[x1-.25,z1-.2]])bx(px,px+.06,B,yc,pz,pz+.06,wm,.01);
  bx(x0,x1,yc,yc+.1,z0+.1,z1,wm,.03);bx(x0-.01,x1+.01,yc+.02,yc+.08,z1-.02,z1+.01,M('#1fb5a5'),.01,false);bx(x1-.02,x1+.01,yc+.02,yc+.08,z0+.1,z1+.01,M('#1fb5a5'),.01,false);
  for(const pz of [z0+.65,z0+1.0]){bx(x0+.55,x0+.75,B,B+.3,pz,pz+.14,wm,.02);bx(x0+.56,x0+.74,B+.18,B+.26,pz+.13,pz+.15,M('#1fb5a5'),.005,false);}
  bx(x0+.05,x0+.4,B,B+.42,z0+.3,z0+.95,M('#f4f1ec'),.02);bx(x0+.39,x0+.41,B+.06,B+.36,z0+.4,z0+.85,M('#8fc3ee'),.005,false);
  bx(x1-.15,x1-.08,B,B+.9,z1-.25,z1-.18,wm,.01);bx(x1-.2,x1-.03,B+.8,B+1.05,z1-.3,z1-.13,M('#1fb5a5'),.02);}
 });
const towerA=(x,z)=>at(x,z,-.15,-4.45,()=>{/* modern A: dark glass tower with dense white vertical fins */{const x0=-.15,x1=1.0,z0=-4.45,z1=-3.3,h=3.4,w=x1-x0,d=z1-z0;ao(x0,x1,z0,z1);const dg=new THREE.MeshPhysicalMaterial({color:'#6f8aa3',roughness:.06,metalness:.35,clearcoat:1,envMapIntensity:1.3}),fw=M('#f4f5f7',{roughness:.35,envMapIntensity:.5}),lob=new THREE.MeshPhysicalMaterial({color:'#a9cbe6',roughness:.05,metalness:.2,clearcoat:1,envMapIntensity:1.2});
  bx(x0-.06,x1+.06,B,B+.05,z0-.06,z1+.06,M('#e3ddd2',{roughness:.6}),.02);bx(x0+.08,x1-.08,B+.05,B+.62,z0+.08,z1-.08,lob,.02);bx(x0-.04,x1+.04,B+.62,B+.7,z0-.04,z1+.04,fw,.02);
  bx(x0,x1,B+.7,B+h,z0,z1,dg,.02);for(let t=x0+.1;t<x1-.02;t+=.19)bx(t-.012,t+.012,B+.7,B+h+.25,z1-.01,z1+.045,fw,.005);for(let t=z0+.1;t<z1-.02;t+=.19)bx(x1-.01,x1+.045,B+.7,B+h+.25,t-.012,t+.012,fw,.005);
  bx(x0+.15,x1-.15,B+h,B+h+.22,z0+.15,z1-.15,M('#d9dde3'),.02);bx(x0+.35,x1-.35,B+.05,B+.55,z1-.07,z1+.0,M('#e8eef5',{roughness:.2}),.01,false);bx(x0+.25,x1-.25,B+.62,B+.66,z1,z1+.25,fw,.015);}
 });
const roundB=(x,z)=>at(x,z,0,-2.6,()=>{/* modern B: rounded-corner mixed-use with wrapping balcony slabs */{const x0=.0,x1=1.0,z0=-2.6,z1=-1.45,R=.38,fl=8,FHb=.3;ao(x0,x1,z0,z1);
  const plan=(e)=>{const sp=new THREE.Shape();sp.moveTo(x0-e,z0-e);sp.lineTo(x1+e-R,z0-e);sp.lineTo(x1+e,z0-e);sp.lineTo(x1+e,z1+e-R);sp.absarc(x1+e-R,z1+e-R,R,0,Math.PI/2,false);sp.lineTo(x0-e,z1+e);sp.lineTo(x0-e,z0-e);return sp;};
  const ext=(e,y0,hh,m,sh=true)=>{const g=new THREE.ExtrudeGeometry(plan(e),{depth:hh,bevelEnabled:false,curveSegments:24});g.rotateX(Math.PI/2);g.translate(0,y0+hh,0);const mm=new THREE.Mesh(g,m);mm.castShadow=sh;mm.receiveShadow=true;sc.add(mm);return mm;};
  const gl=new THREE.MeshPhysicalMaterial({color:'#9fc6e2',roughness:.05,metalness:.25,clearcoat:1,envMapIntensity:1.3,side:THREE.DoubleSide}),wt=M('#f7f6f3',{roughness:.35,envMapIntensity:.5,side:THREE.DoubleSide});
  ext(.02,B,.5,M('#ddd3c4',{roughness:.5,side:THREE.DoubleSide}));ext(-.06,B+.5,fl*FHb,gl);for(let i=0;i<=fl;i++)ext(.07,B+.5+i*FHb-.035,.035,wt,false);
  for(let i=0;i<fl;i++)ext(.07-.005,B+.5+i*FHb+.12,.012,M('#ffffff',{roughness:.3,transparent:true,opacity:.6,side:THREE.DoubleSide}),false);
  ext(-.2,B+.5+fl*FHb,.2,wt);bx(x0+.15,x1-.3,B+.5+fl*FHb+.2,B+.5+fl*FHb+.24,z0+.15,z1-.3,M('#9fd27f',{roughness:.8}),.02,false);}
 });
const fountain=(cx_,cz_)=>at(cx_,cz_,-1.65,-2.15,()=>{/* landscaped fountain plaza */{const cx=-1.65,cz=-2.15,pav=M('#e9e3d8',{roughness:.8}),stone=M('#d9d3c8',{roughness:.6}),wat=new THREE.MeshPhysicalMaterial({color:'#4fb6f0',roughness:.05,clearcoat:1,envMapIntensity:1}),jet=new THREE.MeshStandardMaterial({color:'#e8f6ff',transparent:true,opacity:.7,roughness:.1});
  add(new THREE.CylinderGeometry(1.05,1.05,.03,48),pav,cx,B+.015,cz,false);
  add(new THREE.CylinderGeometry(.62,.64,.12,48),stone,cx,B+.06,cz);add(new THREE.CylinderGeometry(.55,.55,.1,48),wat,cx,B+.075,cz,false);
  add(new THREE.CylinderGeometry(.06,.08,.22,16),stone,cx,B+.2,cz);add(new THREE.CylinderGeometry(.24,.18,.05,32),stone,cx,B+.32,cz);add(new THREE.CylinderGeometry(.2,.2,.02,32),wat,cx,B+.345,cz,false);
  add(new THREE.CylinderGeometry(.04,.05,.14,12),stone,cx,B+.41,cz);add(new THREE.CylinderGeometry(.12,.09,.03,24),stone,cx,B+.49,cz);
  add(new THREE.CylinderGeometry(.012,.04,.32,12),jet,cx,B+.66,cz,false);add(new THREE.SphereGeometry(.05,12,8),jet,cx,B+.82,cz,false);
  for(let i=0;i<8;i++){const a=i/8*Math.PI*2;const e=add(new THREE.CylinderGeometry(.006,.02,.28,8),jet,cx+Math.cos(a)*.13,B+.42,cz+Math.sin(a)*.13,false);e.rotation.z=Math.cos(a)*.6;e.rotation.x=-Math.sin(a)*.6;}
  
  for(const a of [Math.PI*.25,Math.PI*1.25,Math.PI*.75]){const bxp=cx+Math.cos(a)*.85,bzp=cz+Math.sin(a)*.85;const e=add(new THREE.BoxGeometry(.32,.03,.1),M('#b9855a'),bxp,B+.08,bzp);e.rotation.y=-a+Math.PI/2;}}
 });
const roofCafe=(x,z)=>at(x,z,-1.35,-.15,()=>{/* rooftop-terrace cafe */{bld(-1.35,-.3,-.15,.8,2,{wall:'#f7f5f1',wood:1,roof:'#b98a5e'});const y=B+.64;for(const [a,b] of [[-1.0,.2],[-.6,.5]]){add(new THREE.CylinderGeometry(.012,.012,.32,6),wm,a,y+.16,b);add(new THREE.ConeGeometry(.2,.09,16),M('#2f8f6b'),a,y+.34,b);}
  bx(-1.35,-.3,y,y+.12,.77,.8,glz,.005,false);bx(-.33,-.3,y,y+.12,-.15,.8,glz,.005,false);}
 });
const shopHouse=(x,z)=>at(x,z,3.25,-2.4,()=>{/* shop-house (상가주택) */{bld(3.25,4.4,-2.4,-1.3,3,{wall:'#c98a6a',brick:1,balc:1,ww:.36,roof:'#cfc8bc'});bx(3.25,4.4,B,B+.3,-1.32,-1.26,M('#f3efe8'),.01);bx(3.3,4.35,B+.04,B+.26,-1.27,-1.25,M('#9fd0f5'),.005,false);
  const aw=add(new THREE.BoxGeometry(1.1,.03,.22),M('#ffc23d'),3.82,B+.33,-1.17);aw.rotation.x=.4;bx(3.4,4.2,B+.96,B+1.06,-2.25,-1.45,M('#6cc552',{roughness:.8}),.04);}
 });
const restaurant=(x,z)=>at(x,z,3.25,-.6,()=>{/* restaurant w/ rooftop billboard */{bld(3.25,4.45,-.6,.7,2,{wall:'#f6f2ea',frame:'#6b5a4c',shop:'#ff7a59',ww:.4,roof:'#d6cfc4',awn:'#ff7a59'});const y=B+.64;
  for(const pz of [-.35,.45])bx(3.8,3.85,y,y+.35,pz,pz+.05,dk,.005);const cv=document.createElement('canvas');cv.width=256;cv.height=64;const g=cv.getContext('2d');g.fillStyle='#ffc23d';g.fillRect(0,0,256,64);g.fillStyle='#ff7a59';g.fillRect(0,46,256,18);g.beginPath();g.arc(40,26,18,0,7);g.fill();g.fillStyle='#3e2a1e';g.fillRect(72,16,150,8);g.fillRect(72,30,110,8);
  const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;const sm=new THREE.MeshStandardMaterial({map:t,roughness:.5});add(new THREE.BoxGeometry(.06,.4,1.1),[sm,sm,dk,dk,dk,dk],3.84,y+.5,.08);}
 });
const greenhouse=(x,z)=>at(x,z,3.35,3.5,()=>{/* greenhouse cafe */{const x0=3.35,x1=4.25,z0=3.5,z1=4.4,h=.5;ao(x0,x1,z0,z1,.142,.12);bx(x0,x1,B,B+.04,z0,z1,M('#d8c3a8'),.02);add(new THREE.BoxGeometry(x1-x0,h,z1-z0),glz,(x0+x1)/2,B+.04+h/2,(z0+z1)/2,false);
  for(const [px,pz] of [[x0,z0],[x1,z0],[x0,z1],[x1,z1]])bx(px-.02,px+.02,B,B+h+.04,pz-.02,pz+.02,wm,.005);for(const pz of [z0,z1])bx(x0,x1,B+h+.02,B+h+.05,pz-.02,pz+.02,wm,.005);for(const px of [x0,x1])bx(px-.02,px+.02,B+h+.02,B+h+.05,z0,z1,wm,.005);
  const sp=new THREE.Shape();sp.moveTo(-(z1-z0)/2,0);sp.lineTo((z1-z0)/2,0);sp.lineTo(0,.3);sp.lineTo(-(z1-z0)/2,0);const rg=new THREE.ExtrudeGeometry(sp,{depth:x1-x0,bevelEnabled:false});rg.translate(0,0,-(x1-x0)/2);const r=add(rg,glz,(x0+x1)/2,B+h+.05,(z0+z1)/2,false);r.rotation.y=Math.PI/2;
  bx(x0+.02,x1-.02,B+h+.33,B+h+.36,(z0+z1)/2-.02,(z0+z1)/2+.02,wm,.005);for(const [a,b,rr] of [[x0+.2,z0+.2,.1],[x1-.2,z0+.25,.08],[x0+.25,z1-.2,.08],[x1-.25,z1-.25,.1]])add(new THREE.SphereGeometry(rr,20,14),M('#5fae4f',{roughness:.7}),a,B+rr,b,false);bx(x0+.35,x1-.35,B,B+.2,z0+.35,z1-.35,M('#ffffff'),.02);}});
return {bld,house,car,gas,towerA,roundB,fountain,roofCafe,shopHouse,restaurant,greenhouse,STY:{APT,OFF,SHOP,VIL,CVS,STONE,BAND,BRICK,GBRICK,WOOD,TOWN,NEIGH,BAKE,PHAR},crown,PAL,TRK,PIT,LEAF,FH};};
