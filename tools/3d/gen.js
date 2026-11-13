/* ---- island generator ----
   seed string 'g:<type>:<shape>:<n>'. type: city 도시 · metro 대도시 · ind 공업 · farm 농촌 · forest 숲속마을. shape: round long twin crescent archi.
   Builds the same fields the saved maps carry (kind, terr, LVL, ocean, deco, lmkA, lvl …) plus pv/sl/prop, so the renderer needs nothing new.
   Layout rules: blocks between roads keep a walkway every few frontage tiles and a paved path through the middle, terraces never step more
   than one level where people walk, and every terrace edge inside a town gets a slope or stairs now and then. */
const GTYPES=[['city','도시'],['metro','대도시'],['ind','공업'],['farm','농촌'],['forest','숲속마을']],GSHAPES=[['round','둥근'],['long','길쭉한'],['twin','쌍둥이'],['crescent','초승달'],['archi','군도']];
const genIsland=(type,shape,num,NS=128)=>{
 const N=NS,HN=NS+1,Sc=NS/128,K={EMPTY:0,ROAD:1,RES:2,COM:3,IND:4,POWER:5,WATER:6,POLICE:7,FIRE:8,PARK:9,LMK:10},TWA=1,NN=N*N;
 let sd=((num*2654435761)^0x9e3779b9)>>>0||7;const R=()=>{sd^=sd<<13;sd>>>=0;sd^=sd>>>17;sd^=sd<<5;sd>>>=0;return sd/4294967296;};
 const PT=new Float32Array(65536);for(let i=0;i<65536;i++)PT[i]=R();
 const vn=(x,y)=>{const X=Math.floor(x),Y=Math.floor(y),fx=x-X,fy=y-Y,ux=fx*fx*(3-2*fx),uy=fy*fy*(3-2*fy),g=(a,b)=>PT[((b&255)<<8)|(a&255)];return (g(X,Y)*(1-ux)+g(X+1,Y)*ux)*(1-uy)+(g(X,Y+1)*(1-ux)+g(X+1,Y+1)*ux)*uy;};
 const fbm=(x,y,o=4)=>{let s=0,a=.5,f=1,t=0;for(let k=0;k<o;k++){s+=a*vn(x*f+k*31.7,y*f+k*17.3);t+=a;a*=.5;f*=2;}return s/t;};
 const id=(x,y)=>y*N+x,In=(x,y)=>x>=0&&y>=0&&x<N&&y<N,D4=[[1,0],[-1,0],[0,1],[0,-1]];
 /* 1. shape */
 const cx=N/2,cy=N/2,an=R()*Math.PI,ca=Math.cos(an),sa=Math.sin(an),blobs=[];
 if(shape==='twin'){const o=(20+R()*6)*Sc;blobs.push([cx-ca*o,cy-sa*o,(26+R()*5)*Sc],[cx+ca*o,cy+sa*o,(24+R()*6)*Sc]);}
 else if(shape==='archi'){const n=4+((R()*3)|0);for(let k=0;k<n;k++){const a=k/n*6.283+R()*.6,r=k===0?0:(22+R()*16)*Sc;blobs.push([cx+Math.cos(a)*r,cy+Math.sin(a)*r,(k===0?20+R()*4:10+R()*7)*Sc]);}}
 else blobs.push([cx,cy,46*Sc]);
 const sh=(x,y)=>{const u=(x-cx)*ca+(y-cy)*sa,v=-(x-cx)*sa+(y-cy)*ca;
  if(shape==='long')return Math.hypot(u/56/Sc,v/27/Sc);
  if(shape==='crescent'){const d=Math.hypot(x-cx,y-cy)/48/Sc,d2=Math.hypot(x-(cx+ca*26*Sc),y-(cy+sa*26*Sc))/30/Sc;return Math.max(d,2-d2);}
  if(shape==='twin'){let m=9;for(const [bx,by,br] of blobs)m=Math.min(m,Math.hypot(x-bx,y-by)/br);const [a,b]=blobs,t=Math.max(0,Math.min(1,((x-a[0])*(b[0]-a[0])+(y-a[1])*(b[1]-a[1]))/((b[0]-a[0])**2+(b[1]-a[1])**2))),px=a[0]+(b[0]-a[0])*t,py=a[1]+(b[1]-a[1])*t;return Math.min(m,Math.hypot(x-px,y-py)/9/Sc);}
  let m=9;for(const [bx,by,br] of blobs)m=Math.min(m,Math.hypot(x-bx,y-by)/br);return m;};
 const ocean=new Uint8Array(NN).fill(1);
 for(let y=4;y<N-4;y++)for(let x=4;x<N-4;x++){const d=sh(x,y)+(fbm(x/18/Sc,y/18/Sc)-.5)*.55;if(d<1)ocean[id(x,y)]=0;}
 /* keep the big pieces only */
 {const lab=new Int32Array(NN).fill(-1),sz=[];for(let i=0;i<NN;i++){if(ocean[i]||lab[i]>=0)continue;const q=[i];lab[i]=sz.length;let n=0;while(q.length){const j=q.pop();n++;const x=j%N,y=(j/N)|0;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(!ocean[k]&&lab[k]<0){lab[k]=sz.length;q.push(k);}}}sz.push(n);}
  const mx=Math.max(...sz);for(let i=0;i<NN;i++)if(!ocean[i]&&sz[lab[i]]<(shape==='archi'?40*Sc*Sc:mx*.25))ocean[i]=1;}
 /* distance to the coast */
 const cd=new Int16Array(NN).fill(999);{const q=[];for(let i=0;i<NN;i++)if(ocean[i]){cd[i]=0;q.push(i);}for(let h=0;h<q.length;h++){const i=q[h],x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(cd[k]>cd[i]+1){cd[k]=cd[i]+1;q.push(k);}}}}
 /* 2. terraces */
 const maxL={metro:3,city:4,ind:3,farm:3,forest:5}[type]||4,LVL=new Uint8Array(NN);
 for(let i=0;i<NN;i++){if(ocean[i])continue;const x=i%N,y=(i/N)|0,h=fbm(x/26+3,y/26+7)*1.25+Math.min(1,cd[i]/12)*.55-.55;LVL[i]=Math.max(1,Math.min(maxL,1+Math.floor(h*maxL*1.15)));}
 for(let p=0;p<2;p++){const L2=LVL.slice();for(let y=1;y<N-1;y++)for(let x=1;x<N-1;x++){const i=id(x,y);if(ocean[i])continue;const c={};for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const k=id(x+dx,y+dy);if(!ocean[k])c[LVL[k]]=(c[LVL[k]]||0)+1;}let b=LVL[i],bn=0;for(const l in c)if(c[l]>bn){bn=c[l];b=+l;}L2[i]=b;}LVL.set(L2);}
 const relax=()=>{let ch=true,g=0;while(ch&&g++<40){ch=false;for(let y=0;y<N;y++)for(let x=0;x<N;x++){const i=id(x,y);if(ocean[i])continue;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(!ocean[k]&&LVL[i]>LVL[k]+1){LVL[i]=LVL[k]+1;ch=true;}}}}};relax();
 for(let i=0;i<NN;i++)if(!ocean[i]&&cd[i]<=1)LVL[i]=Math.min(LVL[i],2);relax();
 /* 3. town centres: one per blob for twin/archi, otherwise the land centroid */
 const land=i=>!ocean[i];const centres=[];{for(const [bx,by] of blobs){let best=-1,bd=1e9;for(let i=0;i<NN;i++){if(!land(i)||cd[i]<5)continue;const d=Math.hypot(i%N-bx,((i/N)|0)-by);if(d<bd){bd=d;best=i;}}if(best>=0)centres.push([best%N,(best/N)|0]);}}
 if(!centres.length)centres.push([cx,cy]);
 const cdist=(x,y)=>{let m=1e9;for(const [a,b] of centres)m=Math.min(m,Math.hypot(x-a,y-b));return m;};
 const RAD={metro:60,city:34,ind:38,farm:44,forest:24}[type]*(shape==='archi'?.55:shape==='twin'?.8:1)*Sc;
 const dev=(x,y)=>{const i=id(x,y);if(!land(i)||cd[i]<2)return false;return cdist(x,y)/RAD+(fbm(x/14+40,y/14)-.5)*.6<1;};
 /* 4. river (not on the small archipelago pieces) */
 const terr=new Uint8Array(NN),kind=new Uint8Array(NN),lvl=new Uint8Array(NN),deco=new Uint8Array(NN),pv=new Uint8Array(NN),sl=new Uint8Array(NN),prop=new Uint8Array(NN),lmkA=new Int32Array(NN).fill(-1);
 if(shape!=='archi'&&R()<(type==='metro'?.9:.75)){let s=-1,bs=-1;for(let k=0;k<400;k++){const i=(R()*NN)|0;if(land(i)&&cd[i]>bs&&cd[i]>8){bs=cd[i];s=i;}}
  if(s>=0){const seen=new Uint8Array(NN);let i=s,L=LVL[s],steps=0,dir=D4[(R()*4)|0];while(i>=0&&steps++<300){terr[i]=TWA;seen[i]=1;LVL[i]=L=Math.min(L,LVL[i]);const x=i%N,y=(i/N)|0;let nx=-1,best=1e9;for(const d of D4){const xx=x+d[0],yy=y+d[1];if(!In(xx,yy))continue;const k=id(xx,yy);if(seen[k])continue;if(ocean[k]){nx=-2;break;}const sc=LVL[k]*3+cd[k]*.25+(d===dir?-1.2:0)+R()*1.4;if(sc<best){best=sc;nx=k;dir=d;}}if(nx===-2||nx<0)break;i=nx;}}}
 /* river banks keep within one level of the water so they read as banks, not canyons */
 for(let i=0;i<NN;i++)if(terr[i]===TWA){const x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const k=id(x+dx,y+dy);if(land(k)&&terr[k]!==TWA&&LVL[k]>LVL[i]+1)LVL[k]=LVL[i]+1;}}relax();
 /* 5. roads */
 const isR=i=>kind[i]===K.ROAD,water=i=>terr[i]===TWA;
 if(type==='forest'){/* winding lanes between the villages, plus a loop near each */
  const lane=(a,b)=>{let x=a[0],y=a[1],g=0;while((x!==b[0]||y!==b[1])&&g++<400){const i=id(x,y);if(land(i))kind[i]=K.ROAD;const dx=Math.sign(b[0]-x),dy=Math.sign(b[1]-y);if(dx&&(!dy||R()<.5))x+=dx;else y+=dy;}};
  const vils=[...centres];for(let k=0;k<3;k++){for(let t=0;t<200;t++){const i=(R()*NN)|0;if(land(i)&&cd[i]>6&&!water(i)){vils.push([i%N,(i/N)|0]);break;}}}
  for(let k=1;k<vils.length;k++)lane(vils[k-1],vils[k]);for(const [a,b] of vils){lane([a-4,b-3],[a+4,b-3]);lane([a+4,b-3],[a+4,b+3]);lane([a+4,b+3],[a-4,b+3]);lane([a-4,b+3],[a-4,b-3]);}
 }else{const S={metro:7,city:8,ind:9,farm:11}[type],ox=(R()*S)|0,oy=(R()*S)|0;
  for(let y=2;y<N-2;y++)for(let x=2;x<N-2;x++){const i=id(x,y);if(!land(i))continue;if(((x-ox)%S===0||(y-oy)%S===0)&&dev(x,y))kind[i]=K.ROAD;}
  /* trunk roads from each centre to the others */for(let k=1;k<centres.length;k++){let [x,y]=centres[k-1];const [tx,ty]=centres[k];let g=0;while((x!==tx||y!==ty)&&g++<400){const i=id(x,y);if(land(i))kind[i]=K.ROAD;if(x!==tx)x+=Math.sign(tx-x);else y+=Math.sign(ty-y);}}}
 /* roads never climb more than one level between neighbours: flatten along them */
 for(let p=0;p<3;p++)for(let i=0;i<NN;i++)if(isR(i)){const x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const k=id(x+dx,y+dy);if(isR(k)&&LVL[k]>LVL[i]+1)LVL[k]=LVL[i]+1;}}
 /* drop tiny road crumbs */
 {const lab=new Int32Array(NN).fill(-1);for(let i=0;i<NN;i++){if(!isR(i)||lab[i]>=0)continue;const q=[i],c=[i];lab[i]=i;while(q.length){const j=q.pop(),x=j%N,y=(j/N)|0;for(const [dx,dy] of D4){const k=id(x+dx,y+dy);if(In(x+dx,y+dy)&&isR(k)&&lab[k]<0){lab[k]=i;q.push(k);c.push(k);}}}if(c.length<8)for(const j of c)kind[j]=0;}}
 const nearR=i=>{const x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const k=id(x+dx,y+dy);if(In(x+dx,y+dy)&&isR(k)&&LVL[k]===LVL[i])return true;}return false;};
 /* 6. blocks: flood the tiles between roads */
 const blk=new Int32Array(NN).fill(-1),BL=[];for(let i=0;i<NN;i++){if(!land(i)||isR(i)||water(i)||blk[i]>=0)continue;const q=[i],c=[];blk[i]=BL.length;while(q.length){const j=q.pop();c.push(j);const x=j%N,y=(j/N)|0;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(land(k)&&!isR(k)&&!water(k)&&blk[k]<0){blk[k]=BL.length;q.push(k);}}}BL.push(c);}
 const pave=i=>{pv[i]=1+((fbm((i%N)/5,((i/N)|0)/5)*3)|0)%3;};
 const tree=i=>{deco[i]=1+((R()*20)|0);};
 let nPlaza=0;
 /* 물(강·둠벙)까지 거리 */
 const WD=new Int16Array(NN),wDist=()=>{WD.fill(999);const q=[];for(let i=0;i<NN;i++)if(water(i)){WD[i]=0;q.push(i);}for(let h=0;h<q.length;h++){const i=q[h],x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){if(!In(x+dx,y+dy))continue;const k=id(x+dx,y+dy);if(WD[k]>WD[i]+1){WD[k]=WD[i]+1;q.push(k);}}}};wDist();
 /* 소품 번호(PN 순서): 짚뭉치 28, 경운기 29, 원두막 30 — 하위 4비트 + 방향 + 5번째 비트 */
 const pEnc=(n,r)=>(n&15)|((1+((r*4)|0))<<4)|((n>>4)<<7),hayP=r=>pEnc(28,r),hutP=r=>pEnc(30,r);
 /* 큰 건물: 블록 앞줄에 규모대로(2×2 타워, 3×2 마트 …) 길을 바라보게 놓고 둘레 한 칸은 비워 보행로로 남긴다 */
 const GB={res:'terraceApt 2 2|mixedTower 2 2|hanok 1 1|peanut 1 1|cornerShop 1 1|container 1 1|country 1 1|cityHome 1 1|penthouse 1 1',
  mres:'terraceApt 2 2|mixedTower 2 2|cityHome 1 1|penthouse 1 1|cornerShop 1 1',
  com:'pocha 2 1|hypermarket 3 2|dept 3 3|cafe 1 1|ramen 1 1|icecream 1 1|stationery 1 1|optician 1 1|petshop 1 1|karaoke 1 1',
  off:'twinTower 2 2|roundTower 2 2|lab 2 2|convention 3 2|datacenter 2 1|hotel 2 1|bankHQ 2 1|setback 1 1|broadcast 1 1|cowork 1 1',
  ind:'coldStore 2 1|brewery 2 1|recycle 2 1|sawmill 2 1|truckDepot 2 1|dairy 2 1|bakery 2 1|foundry 2 1|paperMill 2 2|chemTanks 2 2|solarFarm 2 2|containerYard 2 2|oilTanks 2 2|cementPlant 2 2|carPlant 3 2|fab 3 2|kiln 1 1|waterTower 1 1|pylon 1 1|printShop 1 1|silo 1 1|wind 1 1',
  pub:'church 1 1|chapel 1 1|kinder 1 1|policeBox 1 1|fireStation 1 1|observatory 1 1|lectureHall 2 1|natatorium 2 1|temple 2 2',
  fac:'tennis 2 1|basketball 2 1|miniGolf 2 2|festival 2 2|iceRink 2 2|nightMarket 2 2|bigWheel 2 2|viewTower 2 2|lakePark 3 3|botanic 3 2|market 3 2|zoo 3 3|aquarium 3 3|arena 3 3|waterpark 3 3|driveIn 3 3|golfRange 3 2',
  tow:'tw2 2 2|tw3 2 2|tw5 2 2|tw8 2 2|tw17 2 2|twinTower 2 2|roundTower 2 2|mixedTower 2 2',
  farm:'barn 2 1|farmhouse 1 1|riceMill 1 1|flourMill 1 1|greenhouseFarm 2 2|silo 1 1|wind 1 1|dairy 2 1|equestrian 3 2|waterTower 1 1',vil:'hanok 1 1|cabin 1 1|country 1 1|peanut 1 1',wild:'campsite 3 2|observatory 1 1|lighthouse 1 1'};
 const BIGS=[],bigm=new Uint8Array(NN),used={};
 const poolOf=(z,L)=>{const t=type,q=R();if(t==='metro')return z==='com'?(L>=4?'tow':q<.65?'off':'com'):z==='res'?'mres':z==='park'?'fac':null;if(t==='city')return z==='com'?(q<.3?'off':'com'):z==='res'?'res':z==='pub'?'pub':z==='park'?'fac':null;
  if(t==='ind')return z==='ind'?'ind':z==='com'?'com':z==='res'?'res':null;if(t==='farm')return z==='field'?'farm':z==='res'?(R()<.5?'farm':'vil'):z==='com'?'vil':null;return z==='res'?'vil':z==='wild'?'wild':null;};
 const placeBig=(c,pk,b)=>{const L=GB[pk].split('|').map(e=>e.split(' ')).sort((a,b2)=>(used[a[0]]||0)-(used[b2[0]]||0)+(R()-.5)*1.5);
  for(const [f,ws,ds] of L.slice(0,4)){const w=+ws,d=+ds;for(let t=0;t<30;t++){const i=c[(R()*c.length)|0],x=i%N,y=(i/N)|0,Lv=LVL[i];
   for(const [dx,dy,dir] of [[0,1,'z+'],[0,-1,'z-'],[1,0,'x+'],[-1,0,'x-']]){const k=id(x+dx,y+dy);if(!In(x+dx,y+dy)||!isR(k)||LVL[k]!==Lv)continue;const W=dx?d:w,Dd=dx?w:d;
    const x0=dx>0?x-W+1:dx<0?x:x-((R()*W)|0),y0=dy>0?y-Dd+1:dy<0?y:y-((R()*Dd)|0);let ok=true;
    for(let yy=y0-1;yy<=y0+Dd&&ok;yy++)for(let xx=x0-1;xx<=x0+W;xx++){if(!In(xx,yy)){ok=false;break;}const j=id(xx,yy),inn=xx>=x0&&xx<x0+W&&yy>=y0&&yy<y0+Dd;if(bigm[j]){ok=false;break;}if(!inn)continue;if(blk[j]!==b||kind[j]||lmkA[j]>=0||LVL[j]!==Lv||water(j)){ok=false;break;}}
    if(ok)for(let e=0;e<(dx?Dd:W)&&ok;e++){const fx=dx>0?x0+W:dx<0?x0-1:x0+e,fy=dy>0?y0+Dd:dy<0?y0-1:y0+e,j=id(fx,fy);if(!In(fx,fy)||!isR(j)||LVL[j]!==Lv)ok=false;}
    if(!ok)continue;for(let yy=y0;yy<y0+Dd;yy++)for(let xx=x0;xx<x0+W;xx++){const j=id(xx,yy);bigm[j]=1;pv[j]=0;deco[j]=0;prop[j]=0;}used[f]=(used[f]||0)+1;BIGS.push([f,x0,y0,W,Dd,dir]);return true;}}}return false;};
 for(const c of BL){if(c.length>220)continue;let x0=1e9,x1=-1,y0=1e9,y1=-1,mx=0,my=0;for(const i of c){const x=i%N,y=(i/N)|0;x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);mx+=x;my+=y;}mx/=c.length;my/=c.length;
  const d=cdist(mx,my)/RAD,front=c.filter(nearR),devd=dev(Math.round(mx),Math.round(my));if(!front.length||!devd)continue;
  /* zone for the block */
  const r=R();let z='res',L=1;
  if(type==='metro'){if(d<.35){z=r<.08?'park':'com';L=r<.5?4:3;}else if(d<.7){z=r<.1?'park':r<.5?'com':'res';L=z==='com'?2+((R()*2)|0):2;}else{z=r<.28?'park':'res';L=2;}}
  else if(type==='city'){if(d<.3){z=r<.1?'park':'com';L=r<.4?3:2;}else if(d<.65){z=r<.18?'park':r<.28?'pub':r<.45?'com':'res';L=z==='com'?(R()<.5?1:2):(R()<.6?2:1);}else{z=r<.24?'park':'res';L=1;}}
  else if(type==='ind'){const side=(mx-cx)*ca+(my-cy)*sa;if(side>0&&d>.15){z='ind';}else if(d<.3){z='com';L=r<.5?2:1;}else{z=r<.1?'park':'res';L=r<.5?2:1;}}
  else if(type==='farm'){if(d<.22){z=r<.3?'com':'res';L=1;}else if(r<.12){z='res';L=1;}else{z='field';}}
  else{z=d<.55?'res':'wild';L=1;}
  /* plazas: a square block big enough for a fountain */
  const w=x1-x0+1,h=y1-y0+1;
  if((type==='city'||type==='metro')&&w>=5&&h>=5&&c.length>=w*h-2&&R()<(nPlaza<3?.22:.06)){nPlaza++;const s=w>=7&&h>=7?6:4,ax=x0+((w-s)>>1),ay=y0+((h-s)>>1),a=id(ax,ay),L0=LVL[a];
   for(const i of c){pave(i);}for(let yy=ay;yy<ay+s;yy++)for(let xx=ax;xx<ax+s;xx++){const i=id(xx,yy);kind[i]=K.LMK;lmkA[i]=a;LVL[i]=L0;pv[i]=0;}continue;}
  {const b=blk[c[0]],pk=poolOf(z,L);if(pk){const n=z==='ind'?(R()<.6?2:1):pk==='fac'?(R()<.55?1:0):pk==='farm'?(R()<.75?1:0)+(c.length>36&&R()<.4?1:0):pk==='wild'?(R()<.35?1:0):pk==='vil'?(R()<.3?1:0):pk==='tow'?2+(c.length>30?1:0):type==='metro'?(R()<.5?1:0)+(c.length>40&&R()<.25?1:0):(R()<.45?1:0);for(let k=0;k<n;k++)placeBig(c,pk,b);}}
  if(z==='park'){for(const i of c){if(bigm[i]){pave(i);continue;}kind[i]=K.PARK;if(R()<.3)tree(i);}const m=c[(c.length/2)|0];if(!bigm[m])prop[m]=1;continue;}
  if(z==='field'){
   /* 농경지: 물에서 가까우면 논, 멀면 밭·풀밭(짚뭉치)·과수. 물이 멀고 블록이 크면 둠벙(작은 저수지)을 판다 */
   let wmin=1e9;for(const i of c)wmin=Math.min(wmin,WD[i]);
   if(wmin>9&&c.length>=20&&R()<.7){for(let t=0;t<40;t++){const i=c[(R()*c.length)|0],x=i%N,y=(i/N)|0,s=R()<.5?2:3,q=[];let ok=true;for(let yy=y;yy<y+s&&ok;yy++)for(let xx=x;xx<x+s;xx++){const j=id(xx,yy);if(!In(xx,yy)||blk[j]!==blk[i]||bigm[j]||nearR(j)||LVL[j]!==LVL[i]){ok=false;break;}q.push(j);}if(!ok)continue;for(const j of q){terr[j]=TWA;}wDist();wmin=0;break;}}
   const q0=R(),kindF=wmin<=10&&q0<.55?'paddy':q0<.78?'field':q0<.92?'pasture':'orchard';
   for(const i of c){if(bigm[i]||water(i))continue;if(nearR(i)&&R()<.06){kind[i]=K.RES;lvl[i]=1;continue;}
    const k=kindF==='paddy'&&WD[i]>12?'field':kindF;
    if(k==='paddy')terr[i]=12;else if(k==='field')terr[i]=10;else if(k==='pasture'){if(R()<.07)prop[i]=hayP(R());else if(R()<.04)tree(i);}else{if((i%N+((i/N)|0))%2===0)tree(i);}}
   {const ed=c.filter(i=>!bigm[i]&&!water(i)&&!kind[i]&&nearR(i)&&!prop[i]);if(ed.length&&R()<.5){const i=ed[(R()*ed.length)|0];terr[i]=0;prop[i]=hutP(R());}}
   continue;}
  if(z==='wild'){for(const i of c)if(!bigm[i]&&R()<.55)tree(i);continue;}
  /* frontage: a building on most road-facing tiles, every few a walkway through to the middle */
  const kd=z==='com'?K.COM:z==='ind'?K.IND:z==='pub'?[K.POLICE,K.FIRE,K.POWER][(R()*3)|0]:K.RES;
  let fi=0;for(const i of c){if(!nearR(i)||bigm[i])continue;const x=i%N,y=(i/N)|0;const gap=type==='forest'?R()<.45:((x+y*3)%(z==='res'&&L===1?3:4)===0);if(gap){pave(i);continue;}
   /* 빈 필지: 앞줄을 다 채우지 않는다 — 바깥으로 갈수록 잔디·나무·쉼터가 늘어난다 */
   {const pE=({metro:z==='com'?.14:.26,city:z==='com'?.16:.3,ind:.16}[type]||0)*(1+Math.max(0,d-.4)*1.5);if(R()<pE){const q=R();if(q<.2)pave(i);else if(q<.82)tree(i);else prop[i]=[1,2,3][(R()*3)|0];continue;}}
   kind[i]=z==='pub'&&fi>0?K.RES:kd;lvl[i]=z==='pub'&&fi>0?2:L;fi++;}
  /* metro: apartment complexes as 2×2 groups inside large residential blocks */
  if(type==='metro'&&z!=='com'){for(const i of c){const x=i%N,y=(i/N)|0;if(nearR(i)||kind[i]||bigm[i])continue;const q=[i,i+1,i+N,i+N+1];if(q.every(k=>blk[k]===blk[i]&&!nearR(k)&&!kind[k]&&!bigm[k]&&LVL[k]===LVL[i])&&R()<.35){for(const k of q){kind[k]=K.COM;lmkA[k]=i;lvl[k]=2;}}}}
  /* the middle: paved path ring + lawn with a tree or a bench */
  for(const i of c){if(kind[i]||pv[i]||bigm[i])continue;const x=i%N,y=(i/N)|0;let nb=0;for(const [dx,dy] of D4){const k=id(x+dx,y+dy);if(kind[k]&&kind[k]!==K.ROAD)nb++;}if(type==='forest'){if(R()<.35)tree(i);continue;}if((nb&&R()<.55)||z==='ind'||(z==='com'&&R()<.6))pave(i);else if(R()<.4)tree(i);else if(R()<.12)prop[i]=[1,2,3][(R()*3)|0];}}
 /* 7. terrace edges in town: a ramp (lawn) or stairs (paved) here and there so people can climb */
 const walk=i=>land(i)&&!water(i)&&!isR(i)&&(kind[i]===0||kind[i]===K.PARK)&&lmkA[i]<0&&!bigm[i];
 for(let y=2;y<N-2;y++)for(let x=2;x<N-2;x++){const b=id(x,y);if(!walk(b)||sl[b]||deco[b]||prop[b]||cdist(x,y)>RAD*1.2)continue;D4.forEach(([dx,dy],di)=>{if(sl[b])return;const a=id(x-dx,y-dy),c2=id(x+dx,y+dy);if(!walk(a)||!walk(c2))return;if(LVL[a]===LVL[b]-1&&LVL[c2]===LVL[b]){let near=false;for(let r=-3;r<=3&&!near;r++)for(let s=-3;s<=3;s++){const k=id(x+r,y+s);if(In(x+r,y+s)&&sl[k]){near=true;break;}}if(near||R()>.5)return;const dir=dx===1?2:dx===-1?4:dy===1?1:3;sl[b]=dir+(pv[b]?4:0);}});}
 /* 8. nature: forests, beaches, rocky tops */
 const fth={forest:.42,farm:.56,ind:.56,city:.52,metro:.6}[type];
 for(let i=0;i<NN;i++){if(!land(i)||water(i)||kind[i]||pv[i]||deco[i]||prop[i]||terr[i]===10||terr[i]===12||bigm[i])continue;const x=i%N,y=(i/N)|0;const f=fbm(x/11+90,y/11);if(blk[i]<0||!dev(x,y)){if(f>fth)tree(i);else if(cd[i]===1&&fbm(x/9,y/9+50)>.55)terr[i]=6;else if(LVL[i]>=4&&fbm(x/7+20,y/7)>.7)terr[i]=9;else if(f<.3&&R()<.05)terr[i]=11;}}
 const H=new Uint8Array(HN*HN);for(let y=0;y<HN;y++)for(let x=0;x<HN;x++)H[y*HN+x]=Math.max(0,(LVL[id(Math.min(x,N-1),Math.min(y,N-1))]||1)-1);
 return {N,HN,K,TWA,H:b64e(H),terr:b64e(terr),kind:b64e(kind),lvl:b64e(lvl),deco:b64e(deco),ocean:b64e(ocean),LVL:b64e(LVL),lmkA:b64e(new Uint8Array(lmkA.buffer)),pv:b64e(pv),sl:b64e(sl),prop:b64e(prop),big:BIGS,auto:type!=='farm'&&type!=='forest',hmin:0,hmax:maxL};};
