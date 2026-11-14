/* ---- island generator ----
   seed string 'g:<type>:<shape>:<n>'. type: city 도시 · metro 대도시 · ind 공업 · farm 농촌 · forest 숲속마을. shape: round long twin crescent archi.
   Builds the same fields the saved maps carry (kind, terr, LVL, ocean, deco, lmkA, lvl …) plus pv/sl/prop, so the renderer needs nothing new.
   Layout rules: blocks between roads keep a walkway every few frontage tiles and a paved path through the middle, terraces never step more
   than one level where people walk, and every terrace edge inside a town gets a slope or stairs now and then. */
const GTYPES=[['city','도시'],['metro','대도시'],['ind','공업'],['farm','농촌'],['forest','숲속마을']],GSHAPES=[['round','둥근'],['oval','타원'],['long','길쭉한'],['twin','쌍둥이'],['crescent','초승달'],['archi','군도'],['heart','하트'],['star','별'],['tri','삼각'],['square','네모'],['penta','오각'],['hexa','육각'],['rhombus','마름모'],['clover','세잎'],['quatre','네잎'],['flower','꽃'],['atoll','환초'],['peanut','땅콩'],['bean','강낭콩'],['drop','물방울'],['egg','달걀'],['lshape','ㄱ자'],['tshape','T자'],['cross','십자'],['horseshoe','말굽'],['bay','만'],['scurve','S자'],['boot','장화'],['fish','물고기'],['tadpole','올챙이'],['triple','세 섬'],['chain','줄섬'],['banana','바나나'],['butterfly','나비'],['lemon','레몬'],['gourd','호리병'],['mitten','벙어리장갑'],['comet','혜성']];
const MULTI=new Set(['archi','triple','chain','butterfly']);
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
 /* 모양 사전: 반지름 ~46칸 기준 좌표(U,V)에서 1보다 작으면 땅. 원·다각형·꽃잎·막대를 합(min)·차(max)로 엮는다 */
 const ci=(U,V,x,y,r)=>Math.hypot(U-x,V-y)/r,poly=(U,V,n,r,ph=0)=>{const a=Math.atan2(V,U)+ph,s=Math.PI/n,k=((a%(2*s))+2*s)%(2*s)-s;return Math.hypot(U,V)*Math.cos(k)/(r*Math.cos(s));},
  lobe=(U,V,n,r,a,p=1)=>{const t=Math.atan2(V,U);return Math.hypot(U,V)/(r*(1+a*(Math.pow(Math.abs(Math.cos(t*n/2)),p)*2-1)));},
  box=(U,V,x,y,w,h,p=5)=>Math.pow(Math.pow(Math.abs(U-x)/w,p)+Math.pow(Math.abs(V-y)/h,p),1/p),
  seg=(U,V,ax,ay,bx,by,r0,r1=r0)=>{const dx=bx-ax,dy=by-ay,t=Math.max(0,Math.min(1,((U-ax)*dx+(V-ay)*dy)/(dx*dx+dy*dy))),r=r0+(r1-r0)*t;return Math.hypot(U-ax-dx*t,V-ay-dy*t)/r;},
  arc=(U,V,R0,w,a0,a1)=>{let t=Math.atan2(V,U);const m=(a0+a1)/2,h=(a1-a0)/2;let d=t-m;d=Math.atan2(Math.sin(d),Math.cos(d));const tc=m+Math.max(-h,Math.min(h,d));return Math.hypot(U-R0*Math.cos(tc),V-R0*Math.sin(tc))/w;},
  mn=(...a)=>Math.min(...a),cut=(a,b)=>Math.max(a,2-b);
 const SH={round:(U,V)=>Math.hypot(U,V)/46,oval:(U,V)=>Math.hypot(U/54,V/36),
  heart:(U,V)=>mn(ci(U,V,-19,-14,25),ci(U,V,19,-14,25),seg(U,V,0,-6,0,44,34,3)),
  star:(U,V)=>lobe(U,V,5,40,.26,2.5),tri:(U,V)=>poly(U,V,3,54,Math.PI/6),square:(U,V)=>box(U,V,0,0,40,40,6),penta:(U,V)=>poly(U,V,5,48),hexa:(U,V)=>poly(U,V,6,47),
  rhombus:(U,V)=>Math.abs(U)/60+Math.abs(V)/36,clover:(U,V)=>mn(ci(U,V,0,-26,23),ci(U,V,-23,14,23),ci(U,V,23,14,23),ci(U,V,0,0,18)),quatre:(U,V)=>mn(ci(U,V,0,-26,21),ci(U,V,0,26,21),ci(U,V,-26,0,21),ci(U,V,26,0,21),ci(U,V,0,0,18)),flower:(U,V)=>lobe(U,V,6,40,.24,1.6),
  atoll:(U,V)=>Math.abs(Math.hypot(U,V)-36)/13,peanut:(U,V)=>mn(ci(U,V,-22,0,28),ci(U,V,22,0,28),seg(U,V,-22,0,22,0,20)),
  bean:(U,V)=>cut(Math.hypot(U/54,V/38),ci(U,V,0,38,22)),drop:(U,V)=>mn(ci(U,V,14,0,34),seg(U,V,14,0,-52,0,30,4)),egg:(U,V)=>Math.hypot(U/(U>0?50:38),V/40),
  lshape:(U,V)=>mn(box(U,V,-14,0,18,46),box(U,V,10,26,40,18)),tshape:(U,V)=>mn(box(U,V,0,-26,50,17),box(U,V,0,8,17,44)),cross:(U,V)=>mn(box(U,V,0,0,52,17),box(U,V,0,0,17,52)),
  horseshoe:(U,V)=>arc(U,V,32,15,-Math.PI*.15,Math.PI*1.15),bay:(U,V)=>cut(Math.hypot(U,V)/46,box(U,V,0,32,13,26)),
  scurve:(U,V)=>mn(arc(U+18,V,24,13,-Math.PI*.1,Math.PI*1.1),arc(U-18,V,24,13,Math.PI*.9,Math.PI*2.1)),
  boot:(U,V)=>mn(box(U,V,-8,-14,17,38),box(U,V,12,26,30,13)),fish:(U,V)=>mn(Math.hypot((U-10)/40,V/27),seg(U,V,-30,0,-52,-20,10),seg(U,V,-30,0,-52,20,10)),
  tadpole:(U,V)=>mn(ci(U,V,18,0,30),seg(U,V,10,0,-30,14,22,6),seg(U,V,-30,14,-50,4,6,3)),
  triple:(U,V)=>mn(ci(U,V,0,-28,22),ci(U,V,-26,18,20),ci(U,V,26,18,21)),chain:(U,V)=>mn(ci(U,V,-40,0,18),ci(U,V,0,0,21),ci(U,V,40,0,18)),
  banana:(U,V)=>arc(U,V+30,52,15,Math.PI*.2,Math.PI*.8),butterfly:(U,V)=>mn(ci(U,V,-22,-16,22),ci(U,V,22,-16,22),ci(U,V,-18,22,16),ci(U,V,18,22,16)),
  lemon:(U,V)=>Math.max(ci(U,V,0,-32,58),ci(U,V,0,32,58)),gourd:(U,V)=>mn(ci(U,V,-16,0,32),ci(U,V,28,0,20)),
  mitten:(U,V)=>mn(box(U,V,0,6,28,34,3),seg(U,V,-24,-6,-40,-30,11)),comet:(U,V)=>mn(ci(U,V,24,0,26),seg(U,V,24,0,-56,10,24,5))};
 const sh=(x,y)=>{const u=(x-cx)*ca+(y-cy)*sa,v=-(x-cx)*sa+(y-cy)*ca;
  if(shape==='long')return Math.hypot(u/56/Sc,v/27/Sc);
  if(shape==='crescent'){const d=Math.hypot(x-cx,y-cy)/48/Sc,d2=Math.hypot(x-(cx+ca*26*Sc),y-(cy+sa*26*Sc))/30/Sc;return Math.max(d,2-d2);}
  if(shape==='twin'){let m=9;for(const [bx,by,br] of blobs)m=Math.min(m,Math.hypot(x-bx,y-by)/br);const [a,b]=blobs,t=Math.max(0,Math.min(1,((x-a[0])*(b[0]-a[0])+(y-a[1])*(b[1]-a[1]))/((b[0]-a[0])**2+(b[1]-a[1])**2))),px=a[0]+(b[0]-a[0])*t,py=a[1]+(b[1]-a[1])*t;return Math.min(m,Math.hypot(x-px,y-py)/9/Sc);}
  if(SH[shape]){const U=u/Sc,V=v/Sc;return SH[shape](U,V);}
  let m=9;for(const [bx,by,br] of blobs)m=Math.min(m,Math.hypot(x-bx,y-by)/br);return m;};
 const ocean=new Uint8Array(NN).fill(1);

 for(let y=4;y<N-4;y++)for(let x=4;x<N-4;x++){const d=sh(x,y)+(fbm(x/18/Sc,y/18/Sc)-.5)*(SH[shape]&&shape!=='round'&&shape!=='oval'?.3:.55);if(d<1)ocean[id(x,y)]=0;}
 /* keep the big pieces only */
 {const lab=new Int32Array(NN).fill(-1),sz=[];for(let i=0;i<NN;i++){if(ocean[i]||lab[i]>=0)continue;const q=[i];lab[i]=sz.length;let n=0;while(q.length){const j=q.pop();n++;const x=j%N,y=(j/N)|0;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(!ocean[k]&&lab[k]<0){lab[k]=sz.length;q.push(k);}}}sz.push(n);}
  const mx=Math.max(...sz);for(let i=0;i<NN;i++)if(!ocean[i]&&sz[lab[i]]<(MULTI.has(shape)?40*Sc*Sc:mx*.25))ocean[i]=1;}
 /* distance to the coast */
 const cd=new Int16Array(NN).fill(999);{const q=[];for(let i=0;i<NN;i++)if(ocean[i]){cd[i]=0;q.push(i);}for(let h=0;h<q.length;h++){const i=q[h],x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(cd[k]>cd[i]+1){cd[k]=cd[i]+1;q.push(k);}}}}
 /* 2. terraces */
 const maxL={metro:3,city:4,ind:3,farm:5,forest:7}[type]||4,/* 산이 있는 섬(숲·농촌 산줄기)만 7단까지 */LVL=new Uint8Array(NN);
 for(let i=0;i<NN;i++){if(ocean[i])continue;const x=i%N,y=(i/N)|0,h=fbm(x/26+3,y/26+7)*1.25+Math.min(1,cd[i]/12)*.55-.55;LVL[i]=Math.max(1,Math.min(maxL,1+Math.floor(h*maxL*1.15)));}
 for(let p=0;p<2;p++){const L2=LVL.slice();for(let y=1;y<N-1;y++)for(let x=1;x<N-1;x++){const i=id(x,y);if(ocean[i])continue;const c={};for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const k=id(x+dx,y+dy);if(!ocean[k])c[LVL[k]]=(c[LVL[k]]||0)+1;}let b=LVL[i],bn=0;for(const l in c)if(c[l]>bn){bn=c[l];b=+l;}L2[i]=b;}LVL.set(L2);}
 const relax=()=>{let ch=true,g=0;while(ch&&g++<40){ch=false;for(let y=0;y<N;y++)for(let x=0;x<N;x++){const i=id(x,y);if(ocean[i])continue;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const k=id(xx,yy);if(!ocean[k]&&LVL[i]>LVL[k]+1){LVL[i]=LVL[k]+1;ch=true;}}}}};relax();
 /* 농촌: 말굽 모양 산줄기가 들을 감싸고, 한쪽(물 나가는 쪽)만 열린다. 들은 평평, 산자락은 완만 */
 const FV=type==='farm'&&!MULTI.has(shape),MT=new Float32Array(NN);let FTH=R()*Math.PI*2,FMC=1;
 if(FV){for(let i=0;i<NN;i++)if(!ocean[i]&&cd[i]<999&&cd[i]>FMC)FMC=cd[i];const ox=Math.cos(FTH),oy=Math.sin(FTH);
  for(let i=0;i<NN;i++){if(ocean[i])continue;const x=i%N,y=(i/N)|0,rr=1-cd[i]/FMC,an=Math.atan2(y-cy,x-cx),op=Math.max(0,Math.cos(an-FTH));
   const m=Math.max(0,Math.min(1,(rr+(fbm(x/10/Sc+5,y/10/Sc)-.5)*.55-.47)/.4))*(1-.95*Math.pow(op,1.2));MT[i]=m;
   LVL[i]=m>.12?Math.max(1,Math.min(7,1+Math.round(m*6.4+(fbm(x/4/Sc,y/4/Sc+9)-.5)*1.6))):(fbm(x/16/Sc+2,y/16/Sc)>.66?2:1);}
  relax();}
 for(let i=0;i<NN;i++)if(!ocean[i]&&cd[i]<=1)LVL[i]=Math.min(LVL[i],2);relax();
 /* 3. town centres: one per blob for twin/archi, otherwise the land centroid */
 const land=i=>!ocean[i];const centres=[];{for(const [bx,by] of blobs){let best=-1,bd=1e9;for(let i=0;i<NN;i++){if(!land(i)||cd[i]<5)continue;const d=Math.hypot(i%N-bx,((i/N)|0)-by);if(d<bd){bd=d;best=i;}}if(best>=0)centres.push([best%N,(best/N)|0]);}}
 if(!centres.length)centres.push([cx,cy]);
 const cdist=(x,y)=>{let m=1e9;for(const [a,b] of centres)m=Math.min(m,Math.hypot(x-a,y-b));return m;};
 const RAD={metro:60,city:34,ind:38,farm:44,forest:24}[type]*(shape==='archi'?.55:shape==='twin'?.8:1)*Sc;
 const dev=(x,y)=>{const i=id(x,y);if(!land(i)||cd[i]<2)return false;return cdist(x,y)/RAD+(fbm(x/14+40,y/14)-.5)*.6<1;};
 /* 4. river (not on the small archipelago pieces) */
 const terr=new Uint8Array(NN),kind=new Uint8Array(NN),lvl=new Uint8Array(NN),deco=new Uint8Array(NN),pv=new Uint8Array(NN),sl=new Uint8Array(NN),prop=new Uint8Array(NN),lmkA=new Int32Array(NN).fill(-1);
 /* 물: 호수(산속 분지) → 그 출구에서 시작해 바다로 굽이쳐 흐르는 강(하류로 갈수록 넓어짐) + 강으로 합류하는 실개천 + 작은 연못 */
 const carve=(i,L)=>{if(ocean[i])return;terr[i]=TWA;LVL[i]=Math.min(LVL[i],L);};
 const blob=(x0,y0,r,amp=.35,seed=0)=>{const T=[];let L=9;for(let y=Math.floor(y0-r-2);y<=y0+r+2;y++)for(let x=Math.floor(x0-r-2);x<=x0+r+2;x++){if(!In(x,y))continue;const i=id(x,y);if(ocean[i]||cd[i]<3)continue;const a=Math.atan2(y-y0,x-x0),rr=r*(1+amp*(fbm(Math.cos(a)*1.3+seed,Math.sin(a)*1.3+seed*.7,3)-.5)*2);if(Math.hypot(x-x0,y-y0)<rr){T.push(i);L=Math.min(L,LVL[i]);}}for(const i of T)carve(i,L);return T;};
 const downA=(x,y)=>{let best=0,bv=1e9;for(let k=0;k<16;k++){const a=k/16*Math.PI*2,xx=Math.round(x+Math.cos(a)*4),yy=Math.round(y+Math.sin(a)*4);if(!In(xx,yy))continue;const i=id(xx,yy),v=ocean[i]?-99:cd[i]+LVL[i]*2.5;if(v<bv){bv=v;best=a;}}return best;};
 /* 강: 목표 지점(반대편 바다)을 향하되 굽이치며 흐른다. 하류로 갈수록 넓어지고, 폭은 원형 단면으로 깎는다 */
 const flow=(sx,sy,tx,ty,w0,w1,join,steps=900)=>{let x=sx,y=sy,a=Math.atan2(ty-y,tx-x),L=LVL[id(Math.round(sx),Math.round(sy))]||1,n=0;const seed=R()*50;
  for(let st=0;st<steps;st++){const at=Math.atan2(ty-y,tx-x);let d=at-a;d=Math.atan2(Math.sin(d),Math.cos(d));a+=d*.06+(fbm(st*.022+seed,seed,2)-.5)*.34;x+=Math.cos(a)*.5;y+=Math.sin(a)*.5;const cxr=Math.round(x),cyr=Math.round(y);if(!In(cxr,cyr))break;const ci=id(cxr,cyr);if(ocean[ci])break;
   if(join&&st>8&&terr[ci]===TWA)break;L=Math.min(L,LVL[ci]);const w=(w0+(w1-w0)*Math.min(1,st/160))*(1+.22*(fbm(st*.04,seed+9,2)-.5))*Sc,r=w/2;
   for(let yy=Math.floor(y-r-1);yy<=y+r+1;yy++)for(let xx=Math.floor(x-r-1);xx<=x+r+1;xx++){if(!In(xx,yy))continue;if(Math.hypot(xx+.5-x,yy+.5-y)<=Math.max(.6,r))carve(id(xx,yy),L);}n++;}return [n,x,y];};
 const pickIn=(minCd,tries=500)=>{let s=-1,bs=-1;for(let k=0;k<tries;k++){const i=(R()*NN)|0;if(land(i)&&cd[i]>minCd&&LVL[i]>=bs){bs=LVL[i];s=i;}}return s;};
 if(!MULTI.has(shape)){
  let mcd=0;for(let i=0;i<NN;i++)if(cd[i]<999&&cd[i]>mcd)mcd=cd[i];
  /* 수원: 섬 안쪽(바다에서 먼 곳)의 한쪽, 하구: 그 반대편 바다 */
  const th=FV?FTH+Math.PI+(R()-.5)*.5:R()*Math.PI*2,ux=Math.cos(th),uy=Math.sin(th);let s0=-1;for(let f=.55;f>=0&&s0<0;f-=.1){const px=Math.round(cx+ux*mcd*f),py=Math.round(cy+uy*mcd*f);if(In(px,py)&&land(id(px,py))&&cd[id(px,py)]>4*Sc)s0=id(px,py);}
  const rv={forest:.85,farm:.95,city:.85,ind:.6,metro:.9}[type]||.8;
  if(s0>=0&&R()<rv){let sx=s0%N,sy=(s0/N)|0;const lk=FV?1:{forest:.8,farm:.65,city:.45,ind:.25,metro:.3}[type]||.4;
   if(R()<lk){const r=(5+R()*4)*Sc;blob(sx,sy,r,.38,R()*30);sx-=ux*r*.7;sy-=uy*r*.7;}
   const tx=cx-ux*N,ty=cy-uy*N,[n,ex,ey]=flow(sx,sy,tx,ty,2.2,type==="metro"?5.5:4.6,false);
   /* 지류: 옆 고지대에서 본류로 */const nt=type==='forest'||type==='farm'?2:R()<.6?1:0;
   for(let k=0;k<nt;k++){const t=.3+R()*.4,mx=sx+(ex-sx)*t,my=sy+(ey-sy)*t,sd=(k%2?1:-1),px=Math.round(mx-uy*sd*mcd*.6),py=Math.round(my+ux*sd*mcd*.6);if(In(px,py)&&land(id(px,py))&&terr[id(px,py)]!==TWA)flow(px,py,mx,my,1.3,1.8,true,400);}}
  /* 작은 연못·둠벙 */const np={forest:4,farm:FV?1:4,city:2,ind:1,metro:1}[type]||1;for(let k=0;k<np;k++){const s=pickIn(6*Sc,200);if(s>=0)blob(s%N,(s/N)|0,(2.6+R()*2.2)*Sc,.5,R()*30);}}
 /* river banks keep within one level of the water so they read as banks, not canyons */
 for(let i=0;i<NN;i++)if(terr[i]===TWA){const x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const k=id(x+dx,y+dy);if(land(k)&&terr[k]!==TWA&&LVL[k]>LVL[i]+1)LVL[k]=LVL[i]+1;}}relax();
 /* 5. roads */
 const isR=i=>kind[i]===K.ROAD,water=i=>terr[i]===TWA;
 /* 농촌 길: 비용 최소 경로(산·물·급경사는 비싸고, 꺾을 때마다 벌점) → 곧게 뻗다 가끔 굽는 지방도 */
 const VIL=[];
 const route=(src,isGoal,maxC=1e9)=>{const S=NN*4,dist=new Float64Array(S).fill(1e9),from=new Int32Array(S).fill(-1),H=[];const push=(d,s)=>{H.push([d,s]);let k=H.length-1;while(k){const p=(k-1)>>1;if(H[p][0]<=H[k][0])break;[H[p],H[k]]=[H[k],H[p]];k=p;}};
   const pop=()=>{const t=H[0],l=H.pop();if(H.length){H[0]=l;let k=0;for(;;){const a=2*k+1,b=a+1;let m=k;if(a<H.length&&H[a][0]<H[m][0])m=a;if(b<H.length&&H[b][0]<H[m][0])m=b;if(m===k)break;[H[m],H[k]]=[H[k],H[m]];k=m;}}return t;};
   for(let d=0;d<4;d++){dist[src*4+d]=0;push(0,src*4+d);}
   while(H.length){const [dd,st]=pop();if(dd>dist[st])continue;const i=st>>2,dr=st&3;if(dd>maxC)break;if(i!==src&&isGoal(i)){const P=[];let c=st;while(c>=0){P.push(c>>2);c=from[c];}return P;}
    const x=i%N,y=(i/N)|0;for(let d=0;d<4;d++){const [dx,dy]=D4[d],xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const j=id(xx,yy);if(ocean[j]||cd[j]<2||Math.abs(LVL[j]-LVL[i])>1)continue;
     const c=1+MT[j]*26+(terr[j]===TWA?(terr[i]===TWA?3:9):0)+(LVL[j]!==LVL[i]?2:0)+fbm(xx/6,yy/6+3,2)*1.2+(d!==dr&&i!==src?6:0)+(kind[j]===K.ROAD?-.6:0),nd=dd+c,ns=j*4+d;if(nd<dist[ns]){dist[ns]=nd;from[ns]=st;push(nd,ns);}}}return null;};
 const FROADS=()=>{const ox=Math.cos(FTH),oy=Math.sin(FTH);
  /* 마을 자리: 산자락(산 기운 .08~.32), 들보다 한두 단 높지 않은 곳, 서로 멀리 */
  const nv=Sc>1.2?4:3;for(let k=0;k<nv;k++){let best=-1,bs=-1e9;for(let t=0;t<900;t++){const i=(R()*NN)|0;if(ocean[i]||terr[i]===TWA||cd[i]<5||MT[i]<.06||MT[i]>.3||LVL[i]>3)continue;const x=i%N,y=(i/N)|0;let dm=99;for(const [a,b] of VIL)dm=Math.min(dm,Math.hypot(a-x,b-y));if(VIL.length&&dm<24*Sc)continue;const mN=MT[id(x,Math.max(0,y-6))]||0,mS=MT[id(x,Math.min(N-1,y+6))]||0,sc=dm+R()*6+(mN-mS)*40;/* 배산임수: 뒤(북)는 산, 앞(남)은 들 */if(sc>bs){bs=sc;best=i;}}if(best>=0)VIL.push([best%N,(best/N)|0]);}
  /* 지방도: 열린 쪽 바닷가에서 가장 안쪽 마을까지 */
  let m0=-1,md=1e9;for(let i=0;i<NN;i++){if(ocean[i]||cd[i]!==2||terr[i]===TWA)continue;const x=i%N,y=(i/N)|0,d=Math.hypot(x-(cx+ox*FMC*1.6),y-(cy+oy*FMC*1.6));if(d<md){md=d;m0=i;}}
  if(m0>=0&&VIL.length){VIL.sort((a,b)=>Math.hypot(b[0]-m0%N,b[1]-((m0/N)|0))-Math.hypot(a[0]-m0%N,a[1]-((m0/N)|0)));const far=VIL[0],g=id(far[0],far[1]),P=route(m0,i=>i===g);if(P)for(const j of P)kind[j]=K.ROAD;}
  /* 나머지 마을 → 가까운 길로 이어 붙인다 */
  for(const [vx,vy] of VIL.slice(1)){const P=route(id(vx,vy),i=>kind[i]===K.ROAD);if(P)for(const j of P)kind[j]=K.ROAD;}
  /* 마을 안길: 중심에서 두세 갈래, 짧게 */
  for(const [vx,vy] of VIL){const nl=2+((R()*2)|0);for(let k=0;k<nl;k++){let x=vx,y=vy,d=(R()*4)|0;const L=5+((R()*5)|0);for(let st=0;st<L;st++){if(st===((L/2)|0)&&R()<.6)d=(d+(R()<.5?1:3))%4;const xx=x+D4[d][0],yy=y+D4[d][1];if(!In(xx,yy))break;const j=id(xx,yy);if(ocean[j]||cd[j]<2||terr[j]===TWA||MT[j]>.42||Math.abs(LVL[j]-LVL[id(x,y)])>1)break;kind[j]=K.ROAD;x=xx;y=yy;}}}};
 if(type==='forest'){/* winding lanes between the villages, plus a loop near each */
  const lane=(a,b)=>{let x=a[0],y=a[1],g=0;while((x!==b[0]||y!==b[1])&&g++<400){const i=id(x,y);if(land(i))kind[i]=K.ROAD;const dx=Math.sign(b[0]-x),dy=Math.sign(b[1]-y);if(dx&&(!dy||R()<.5))x+=dx;else y+=dy;}};
  const vils=[...centres];for(let k=0;k<3;k++){for(let t=0;t<200;t++){const i=(R()*NN)|0;if(land(i)&&cd[i]>6&&!water(i)){vils.push([i%N,(i/N)|0]);break;}}}
  for(let k=1;k<vils.length;k++)lane(vils[k-1],vils[k]);for(const [a,b] of vils){lane([a-4,b-3],[a+4,b-3]);lane([a+4,b-3],[a+4,b+3]);lane([a+4,b+3],[a-4,b+3]);lane([a-4,b+3],[a-4,b-3]);}
 }else if(FV){FROADS();}else{const S={metro:7,city:8,ind:9,farm:11}[type],ox=(R()*S)|0,oy=(R()*S)|0;
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
 const pEnc=(n,r)=>(n&15)|((1+((r*4)|0))<<4)|((n>>4)<<7),hayP=r=>pEnc(28,r),hutP=r=>pEnc(30,r),stopP=r=>pEnc(31,r);
 /* 큰 건물: 블록 앞줄에 규모대로(2×2 타워, 3×2 마트 …) 길을 바라보게 놓고 둘레 한 칸은 비워 보행로로 남긴다 */
 const GB={res:'terraceApt 2 2|mixedTower 2 2|hanok 1 1|peanut 1 1|cornerShop 1 1|container 1 1|country 1 1|cityHome 1 1|penthouse 1 1',
  mres:'terraceApt 2 2|mixedTower 2 2|cityHome 1 1|penthouse 1 1|cornerShop 1 1',
  com:'pocha 2 1|hypermarket 3 2|dept 3 3|cafe 1 1|ramen 1 1|icecream 1 1|stationery 1 1|optician 1 1|petshop 1 1|karaoke 1 1',
  off:'twinTower 2 2|roundTower 2 2|lab 2 2|convention 3 2|datacenter 2 1|hotel 2 1|bankHQ 2 1|setback 1 1|broadcast 1 1|cowork 1 1',
  ind:'coldStore 2 1|brewery 2 1|recycle 2 1|sawmill 2 1|truckDepot 2 1|dairy 2 1|bakery 2 1|foundry 2 1|paperMill 2 2|chemTanks 2 2|solarFarm 2 2|containerYard 2 2|oilTanks 2 2|cementPlant 2 2|carPlant 3 2|fab 3 2|kiln 1 1|waterTower 1 1|pylon 1 1|printShop 1 1|silo 2 2|wind 2 2',
  pub:'church 1 1|chapel 1 1|kinder 1 1|policeBox 1 1|fireStation 1 1|observatory 1 1|lectureHall 2 1|natatorium 2 1|temple 2 2',
  fac:'tennis 2 1|basketball 2 1|miniGolf 2 2|festival 2 2|iceRink 2 2|nightMarket 2 2|bigWheel 2 2|viewTower 2 2|lakePark 3 3|botanic 3 2|market 3 2|zoo 3 3|aquarium 3 3|arena 3 3|waterpark 3 3|driveIn 3 3|golfRange 3 2',
  tow:'tw2 2 2|tw3 2 2|tw5 2 2|tw8 2 2|tw17 2 2|twinTower 2 2|roundTower 2 2|mixedTower 2 2',
  farm:'barn 2 1|farmhouse 2 2|riceMill 1 1|flourMill 1 1|greenhouseFarm 4 3|silo 2 2|wind 2 2|dairy 2 1|equestrian 4 3|waterTower 1 1',vil:'hanok 1 1|cabin 1 1|country 1 1|peanut 1 1|farmhouse 2 2',wild:'campsite 3 2|observatory 1 1|lighthouse 1 1'};
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
 /* 농촌 채우기: 산자락 마을(집은 안길을 보고 띄엄띄엄) → 길가 농가 시설·비닐하우스 단지 → 들의 경지(정리된 논 + 농로, 굽은 경계의 밭) → 산은 숲 */
 const FFILL=()=>{const ox=Math.cos(FTH),oy=Math.sin(FTH),alongX=Math.abs(ox)>=Math.abs(oy),vd=(x,y)=>{let m=1e9;for(const [a,b] of VIL)m=Math.min(m,Math.hypot(a-x,b-y));return m;},VR=8*Sc;
  const front=[];for(let i=0;i<NN;i++)if(land(i)&&!water(i)&&!isR(i)&&blk[i]>=0&&nearR(i))front.push(i);
  const pb=(cands,pool)=>{if(!cands.length)return false;const i=cands[(R()*cands.length)|0],b=blk[i],c=cands.filter(j=>blk[j]===b);const sv=GB.farm;GB.farm=pool;const ok=placeBig(c,'farm',b);GB.farm=sv;return ok;};
  const nearV=front.filter(i=>vd(i%N,(i/N)|0)<VR),midV=front.filter(i=>{const d=vd(i%N,(i/N)|0);return d>=VR*.7&&d<VR*1.8;}),plain=front.filter(i=>MT[i]<.05&&vd(i%N,(i/N)|0)>VR*1.4);
  /* 버스터미널: 첫(가장 큰) 마을 */{const t=nearV.filter(i=>Math.hypot(i%N-VIL[VIL.length-1][0],((i/N)|0)-VIL[VIL.length-1][1])<VR*1.4);pb(t.length?t:nearV,'busTerminal 2 1');}
  /* 큰 마을: 마을회관·경로당, 마을마트·농약사, 교회 / 마을마다 어귀(들 쪽)에 정자목 */{const V0=VIL[VIL.length-1],t=nearV.filter(i=>Math.hypot(i%N-V0[0],((i/N)|0)-V0[1])<VR*1.4);pb(t.length?t:nearV,'villageHall 2 1');pb(t.length?t:nearV,'villageMart 2 1');pb(nearV,'farmSupply 1 1');pb(nearV,'chapel 1 1');}
  for(const [vx,vy] of VIL){const e=front.filter(i=>{const d=Math.hypot(i%N-vx,((i/N)|0)-vy);return d>VR*.55&&d<VR*1.3&&MT[i]<.12;});if(e.length)pb(e,'villageTree 2 2');}
  /* 집이 2×2로 커져 자리 찾기가 어려우니 더 여러 번 시도 */for(let k=0;k<VIL.length*36;k++)pb(nearV,'slateHouse 2 2|yangok 2 2|yangokBlue 2 2|farmhouse 2 2|slateHouse 2 2|hanok 1 1|yangok 2 2');
  /* 들 가운데엔 들에 어울리는 시설(창고 컨테이너·하우스·양수장)만 — 축사·정미소·헛간·사일로는 마을 언저리 */const edgeV=front.filter(i=>{const d=vd(i%N,(i/N)|0);return d>=VR*.5&&d<VR*1.05;});for(let k=0;k<VIL.length*2;k++)pb(edgeV,'cowshed 3 2|riceMill 1 1|barn 2 1|silo 2 2');for(let k=0;k<VIL.length;k++)pb(midV,'containerStore 1 1');
  /* 물가 양수장 */for(let k=0;k<2;k++)pb(front.filter(i=>WD[i]<=3*Sc),'pumpHouse 1 1');
  for(let k=0;k<3+((R()*3)|0);k++)pb(plain,'greenhouseFarm 4 3');
  if(R()<.6)pb(edgeV,'equestrian 4 3');/* 풍력발전기는 바람 센 바닷가나 산자락에 */if(R()<.75){const wc=front.filter(i=>cd[i]>0&&cd[i]<=4*Sc||MT[i]>=.12);pb(wc.length?wc:plain,'wind 2 2');}
  /* 경지: 논은 물(강·저수지) 가까운 낮은 들에 8×3칸 직사각 필지, 9칸마다 가로 농로, 두 필지마다 세로 농로 */
  const ao=(R()*9)|0,bo=(R()*7)|0,h2=(a,b)=>((Math.imul(a,73856093)^Math.imul(b,19349663))>>>0);
  for(let i=0;i<NN;i++){if(!land(i)||water(i)||isR(i)||bigm[i]||kind[i]||prop[i])continue;const x=i%N,y=(i/N)|0,a=alongX?x:y,b=alongX?y:x,v=vd(x,y),m=MT[i];
   if(v<VR){/* 마을 안: 텃밭·마당 나무 */const q=R();if(q<.22){terr[i]=10;lvl[i]=1+(h2(x>>1,y>>1)%250);}else if(q<.42)tree(i);continue;}
   if(m>=.3||LVL[i]>=4){/* 산: 빽빽한 숲, 꼭대기엔 바위 */if(LVL[i]>=5&&fbm(x/5,y/5+7)>.62)terr[i]=9;else if(R()<.86){tree(i);if(R()<.75)deco[i]=21;/* 산은 소나무가 주인, 활엽수는 사이사이(가을 단풍) */}continue;}
   if(m>=.1){/* 산자락: 물 가까운 골짜기엔 다랑논(단마다 따로 필지) · 과수원 줄나무 · 비탈밭 · 풀밭 */const z=fbm(x/9+11,y/9);if(WD[i]<=12*Sc&&fbm(x/12+60,y/12)>.48){terr[i]=12;lvl[i]=1+(h2(LVL[i]*97+Math.floor(a/4),Math.floor(b/3)+300)%250);continue;}if(z<.42){if((a%2===0)&&(b%2===0))tree(i);}else if(z<.62){terr[i]=10;lvl[i]=1+(h2(Math.floor((a+fbm(x/5,y/5)*3)/5),Math.floor(b/3)+77)%250);}else if(R()<.25)tree(i);else if(R()<.04)prop[i]=hayP(R());continue;}
   const pa=a-ao,pB=b-bo,ra=((pa%9)+9)%9,rb=((pB%7)+7)%7;
   if(WD[i]<=(7+fbm(x/14+40,y/14)*9)*Sc&&LVL[i]<=2){if(ra===8||rb===6){terr[i]=0;if(rb===6&&ra!==8&&(((Math.floor(pB/7)%2)+2)%2===0))pv[i]=6;continue;}terr[i]=12;lvl[i]=1+(h2(Math.floor(pa/9),Math.floor(pB/7)*2+(rb>=3?1:0))%250);continue;}
   /* 밭: 경계가 조금씩 굽은 필지. 열에 하나는 풀밭(짚뭉치) */const ka=Math.floor((a+fbm(x/7+3,y/7)*4)/6),kb=Math.floor((b+fbm(x/7,y/7+3)*4)/4),hh=h2(ka,kb+500);
   if(hh%10===0){if(R()<.08)prop[i]=hayP(R());continue;}if(ra===8&&hh%3===0){terr[i]=0;continue;}terr[i]=10;lvl[i]=1+(hh%250);}
  /* 들에 어울리지 않는 건물은 둘레 한 칸을 논밭 대신 풀 마당으로 */{const FIT=new Set(['greenhouseFarm','pumpHouse','containerStore','villageTree','wind','grave']);for(const [f,x0,y0,W,Dd] of BIGS){if(FIT.has(f))continue;for(let yy=y0-1;yy<=y0+Dd;yy++)for(let xx=x0-1;xx<=x0+W;xx++){if(!In(xx,yy))continue;const j=id(xx,yy);if(terr[j]===10||terr[j]===12){terr[j]=0;lvl[j]=0;}}}}
  /* 둑길: 들판을 지나는 강 양옆 한 칸은 농로(자전거·경운기 길) */for(let i=0;i<NN;i++){if(!land(i)||water(i)||isR(i)||bigm[i]||kind[i]||LVL[i]>2||MT[i]>.1)continue;const x=i%N,y=(i/N)|0;if(!D4.some(([dx,dy])=>In(x+dx,y+dy)&&terr[id(x+dx,y+dy)]===TWA&&!ocean[id(x+dx,y+dy)]))continue;if(terr[i]!==0&&terr[i]!==10&&terr[i]!==12)continue;terr[i]=0;lvl[i]=0;pv[i]=6;prop[i]=0;deco[i]=0;}
  /* 산소: 산 중턱 양지에 몇 기 */{let n=0;for(let t=0;t<4000&&n<4+((R()*3)|0);t++){const i=(R()*NN)|0;if(!land(i)||water(i)||isR(i)||bigm[i]||kind[i]||MT[i]<.3||MT[i]>.6||LVL[i]<3||terr[i]===9)continue;const x=i%N,y=(i/N)|0;if(!D4.every(([dx,dy])=>In(x+dx,y+dy)&&LVL[id(x+dx,y+dy)]===LVL[i]&&!bigm[id(x+dx,y+dy)]))continue;bigm[i]=1;deco[i]=0;prop[i]=0;terr[i]=0;BIGS.push(['grave',x,y,1,1,'z+']);n++;}}
  /* 길가 밭 한쪽에 원두막 */for(let k=0;k<4;k++){const c=front.filter(i=>terr[i]===10&&!prop[i]&&!bigm[i]&&vd(i%N,(i/N)|0)>VR);if(!c.length)break;const i=c[(R()*c.length)|0];terr[i]=0;lvl[i]=0;prop[i]=hutP(R());}};
 /* 농로 잇기: 차도에 닿지 않은 농로 묶음은 풀밭(필요하면 논밭 가장자리)을 지나 가장 가까운 같은 높이 차도까지 길을 내고, 끝내 못 닿으면 풀밭으로 되돌린다 */
 const FLINK=()=>{const seen=new Uint8Array(NN),isRd=i=>kind[i]===K.ROAD;
  for(let s0=0;s0<NN;s0++){if(pv[s0]!==6||seen[s0])continue;const comp=[s0];seen[s0]=1;for(let h=0;h<comp.length;h++){const i=comp[h],x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const j=id(xx,yy);if(pv[j]===6&&!seen[j]){seen[j]=1;comp.push(j);}}}
   const touch=comp.some(i=>{const x=i%N,y=(i/N)|0;return D4.some(([dx,dy])=>{const xx=x+dx,yy=y+dy;if(!In(xx,yy))return false;const j=id(xx,yy);return isRd(j)&&LVL[j]===LVL[i];});});if(touch)continue;
   const dist=new Map(),from=new Map(),H=[];for(const i of comp){dist.set(i,0);H.push([0,i]);}let goal=-1;
   const hp=e=>{H.push(e);let k=H.length-1;while(k){const q=(k-1)>>1;if(H[q][0]<=H[k][0])break;[H[q],H[k]]=[H[k],H[q]];k=q;}},hpop=()=>{const t=H[0],l=H.pop();if(H.length){H[0]=l;let k=0;for(;;){const a2=2*k+1,b2=a2+1;let m=k;if(a2<H.length&&H[a2][0]<H[m][0])m=a2;if(b2<H.length&&H[b2][0]<H[m][0])m=b2;if(m===k)break;[H[m],H[k]]=[H[k],H[m]];k=m;}}return t;};
   while(H.length&&goal<0){const [d,i]=hpop();if(d>dist.get(i)||d>40)continue;const x=i%N,y=(i/N)|0;
    for(const [dx,dy] of D4){const xx=x+dx,yy=y+dy;if(!In(xx,yy))continue;const j=id(xx,yy);if(LVL[j]!==LVL[i])continue;if(isRd(j)){goal=i;break;}
     if(ocean[j]||terr[j]===TWA||kind[j]||bigm[j]||pv[j]===6)continue;const c=(terr[j]===0?1:terr[j]===10||terr[j]===12?3:6)+(prop[j]?4:0)+(deco[j]?1:0),nd=d+c;if(!dist.has(j)||nd<dist.get(j)){dist.set(j,nd);from.set(j,i);hp([nd,j]);}}}
   if(goal>=0){let j=goal;while(j!==undefined&&pv[j]!==6){pv[j]=6;terr[j]=0;prop[j]=0;deco[j]=0;lvl[j]=0;j=from.get(j);}}else for(const i of comp)pv[i]=0;}};
 if(FV){FFILL();FLINK();}else for(const c of BL){if(c.length>220)continue;let x0=1e9,x1=-1,y0=1e9,y1=-1,mx=0,my=0;for(const i of c){const x=i%N,y=(i/N)|0;x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);mx+=x;my+=y;}mx/=c.length;my/=c.length;
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
   if(wmin>9&&c.length>=20&&R()<.7){for(let t=0;t<40;t++){const i=c[(R()*c.length)|0],x=i%N,y=(i/N)|0,r=1.3+R()*1.1,q=[];let ok=true;for(let yy=Math.floor(y-r-1);yy<=y+r+1&&ok;yy++)for(let xx=Math.floor(x-r-1);xx<=x+r+1;xx++){const a=Math.atan2(yy-y,xx-x),rr=r*(1+.35*(fbm(Math.cos(a)+i,Math.sin(a),2)-.5)*2);if(Math.hypot(xx-x,yy-y)>=rr)continue;const j=id(xx,yy);if(!In(xx,yy)||blk[j]!==blk[i]||bigm[j]||nearR(j)||LVL[j]!==LVL[i]){ok=false;break;}q.push(j);}if(!ok||q.length<3)continue;for(const j of q){terr[j]=TWA;}wDist();wmin=0;break;}}
   const q0=R(),kindF=wmin<=10&&q0<.36?'paddy':q0<.74?'field':q0<.9?'pasture':'orchard';
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
 /* 농촌: 마을 중심 가까이 버스터미널 1곳, 길가 곳곳에 버스정류장 */
 if(type==='farm'){const cs=[];if(!FV)for(const [bi,b] of BL.entries()){if(!b.length)continue;let mx=0,my=0;for(const i of b){mx+=i%N;my+=(i/N)|0;}mx/=b.length;my/=b.length;cs.push([cdist(mx,my),b,bi]);}cs.sort((a,b)=>a[0]-b[0]);
  const sv=GB.farm;GB.farm='busTerminal 2 1';for(const [,b,bi] of cs.slice(0,8))if(placeBig(b,'farm',bi))break;GB.farm=sv;
  let last=[];for(let i=0;i<NN;i++){if(!land(i)||water(i)||kind[i]||bigm[i]||prop[i]||terr[i]===10||terr[i]===12||!nearR(i))continue;const x=i%N,y=(i/N)|0;if(last.some(([a,b])=>Math.abs(a-x)+Math.abs(b-y)<26))continue;if(R()<.6)continue;let dr=0;D4.forEach(([dx,dy],k)=>{const j=id(x+dx,y+dy);if(isR(j))dr=k;});prop[i]=stopP([.75,.25,0,.5][dr]);last.push([x,y]);}}
 /* 7. terrace edges in town: a ramp (lawn) or stairs (paved) here and there so people can climb */
 const walk=i=>land(i)&&!water(i)&&!isR(i)&&(kind[i]===0||kind[i]===K.PARK)&&lmkA[i]<0&&!bigm[i];
 for(let y=2;y<N-2;y++)for(let x=2;x<N-2;x++){const b=id(x,y);if(!walk(b)||sl[b]||deco[b]||prop[b]||cdist(x,y)>RAD*1.2)continue;D4.forEach(([dx,dy],di)=>{if(sl[b])return;const a=id(x-dx,y-dy),c2=id(x+dx,y+dy);if(!walk(a)||!walk(c2))return;if(LVL[a]===LVL[b]-1&&LVL[c2]===LVL[b]){let near=false;for(let r=-3;r<=3&&!near;r++)for(let s=-3;s<=3;s++){const k=id(x+r,y+s);if(In(x+r,y+s)&&sl[k]){near=true;break;}}if(near||R()>.5)return;const dir=dx===1?2:dx===-1?4:dy===1?1:3;sl[b]=dir+(pv[b]?4:0);}});}
 /* 8. nature: forests, beaches, rocky tops */
 const fth={forest:.42,farm:.56,ind:.56,city:.52,metro:.6}[type];
 if(!FV)for(let i=0;i<NN;i++){if(!land(i)||water(i)||kind[i]||pv[i]||deco[i]||prop[i]||terr[i]===10||terr[i]===12||bigm[i])continue;const x=i%N,y=(i/N)|0;const f=fbm(x/11+90,y/11);if(blk[i]<0||!dev(x,y)){if(f>fth)tree(i);else if(cd[i]===1&&fbm(x/9,y/9+50)>.55)terr[i]=6;else if(LVL[i]>=4&&fbm(x/7+20,y/7)>.7)terr[i]=9;else if(f<.3&&R()<.05)terr[i]=11;}}
 /* 9. 고립 건물 없애기: 길에서 걸어서(같은 높이, 또는 경사로 한 단) 못 닿는 건물 칸은 이웃 길·마당 높이로 땅을 맞추고, 그래도 안 되면 비워 풀밭으로 */
 {const bld=i=>(kind[i]>=K.RES&&kind[i]!==K.WATER&&kind[i]!==K.PARK)||bigm[i];
  for(let pass=0;pass<3;pass++){const seen=new Uint8Array(NN),q=[];for(let i=0;i<NN;i++)if(isR(i)){seen[i]=1;q.push(i);}
   for(let h=0;h<q.length;h++){const i=q[h],x=i%N,y=(i/N)|0;for(const [dx,dy] of D4){if(!In(x+dx,y+dy))continue;const j=id(x+dx,y+dy);if(seen[j]||ocean[j]||water(j))continue;if(!(LVL[j]===LVL[i]||((sl[i]||sl[j])&&Math.abs(LVL[j]-LVL[i])<=1)))continue;if(bld(j)){seen[j]=2;continue;}seen[j]=1;q.push(j);}}
   const G=new Map();for(let i=0;i<NN;i++){if(!bld(i))continue;let g=lmkA[i]>=0?'l'+lmkA[i]:'t'+i;if(bigm[i]){const b=BIGS.find(([,x0,y0,w,d])=>i%N>=x0&&i%N<x0+w&&((i/N)|0)>=y0&&((i/N)|0)<y0+d);g=b?'b'+BIGS.indexOf(b):g;}if(!G.has(g))G.set(g,[]);G.get(g).push(i);}
   let fixed=0;for(const [g,cells] of G){if(cells.some(i=>seen[i]===2))continue;if(g[0]==='b'&&BIGS[+g.slice(1)]&&BIGS[+g.slice(1)][0]==='grave')continue;/* 산소는 산길로 오르니 길 연결 없이 둔다 */
    if(cells.length===1&&!bigm[cells[0]]){const i=cells[0],x=i%N,y=(i/N)|0;let lv=-1;for(const [dx,dy] of D4){if(!In(x+dx,y+dy))continue;const j=id(x+dx,y+dy);if(seen[j]===1&&!sl[j]&&Math.abs(LVL[j]-LVL[i])===1){const ok=D4.every(([ex,ey])=>{if(!In(x+ex,y+ey))return true;const k=id(x+ex,y+ey);return ocean[k]||(Math.abs(LVL[k]-LVL[j])<=1&&!sl[k]);});if(ok){lv=LVL[j];break;}}}
     if(lv>0){LVL[i]=lv;fixed++;continue;}}
    if(pass<2)continue;/* 마지막: 비운다 */for(const i of cells){kind[i]=0;lmkA[i]=-1;bigm[i]=0;lvl[i]=0;pv[i]=0;}const bi=g[0]==='b'?+g.slice(1):-1;if(bi>=0)BIGS[bi]=null;fixed++;}
   if(!fixed&&pass<2)continue;}
  for(let k=BIGS.length-1;k>=0;k--)if(!BIGS[k])BIGS.splice(k,1);}
 const H=new Uint8Array(HN*HN);for(let y=0;y<HN;y++)for(let x=0;x<HN;x++)H[y*HN+x]=Math.max(0,(LVL[id(Math.min(x,N-1),Math.min(y,N-1))]||1)-1);
 /* 논 사이엔 경사가 없다 — 논 칸의 경사는 없애 계단식 단으로(밭 경사는 밭흙 경사로 남긴다). 섬 가장자리 절벽에 바로 붙은 논은 풀 둔치로 */for(let i=0;i<NN;i++){if(sl[i]&&terr[i]===12&&!isR(i)&&pv[i]!==6)sl[i]=0;}
 for(let i=0;i<NN;i++){if(terr[i]!==12)continue;const x=i%N,y=(i/N)|0;let e=false;for(let a=-1;a<=1&&!e;a++)for(let b=-1;b<=1;b++){if(!In(x+b,y+a)||!land(id(x+b,y+a))){e=true;break;}}if(e){terr[i]=0;lvl[i]=0;}}
 return {N,HN,K,TWA,H:b64e(H),terr:b64e(terr),kind:b64e(kind),lvl:b64e(lvl),deco:b64e(deco),ocean:b64e(ocean),LVL:b64e(LVL),lmkA:b64e(new Uint8Array(lmkA.buffer)),pv:b64e(pv),sl:b64e(sl),prop:b64e(prop),big:BIGS,auto:type!=='farm'&&type!=='forest',hmin:0,hmax:FV?7:maxL};};
