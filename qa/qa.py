# QA harness: python3 qa.py [seeds...]  -> qa_report.json + qa_<seed>.png contact sheets
import asyncio,sys,json,os
from playwright.async_api import async_playwright
from PIL import Image,ImageDraw,ImageFont
D=os.path.dirname(os.path.abspath(__file__));os.makedirs(os.path.join(D,'out'),exist_ok=True);O=os.path.join(D,'out')
CHECK=r"""
(()=>{const R={};const DIR=[[1,0],[-1,0],[0,1],[0,-1]],rd=(x,y)=>x>=0&&y>=0&&x<N&&y<N&&kind[idx(x,y)]===K.ROAD;
 /* 1. rail: pillars/decks off the median, rail tiles off road */
 let offMed=0,offRoad=0;for(let i=0;i<NN;i++){if(!RL[i])continue;if(kind[i]!==K.ROAD){offRoad++;continue;}if(isWide(i)){const W=RC[lvl[i]].W,w=wInfo(i);const L=RLINES.find(q=>(RL[i]>>q.line)&1);if(L&&w.ax===L.ax&&(!(W&1)||w.p!==(W>>1)))offMed++;}}R.railOffMedian=offMed;R.railOffRoad=offRoad;
 /* 2. road network: components and stubs */
 const lab=new Int32Array(NN).fill(-1),sz=[];for(let s0=0;s0<NN;s0++){if(kind[s0]!==K.ROAD||lab[s0]>=0)continue;const q=[s0];lab[s0]=sz.length;for(let h=0;h<q.length;h++){const i=q[h],x=i&NM,y=i>>NS;for(const [dx,dy] of DIR){if(!rd(x+dx,y+dy))continue;const j=idx(x+dx,y+dy);if(lab[j]<0){lab[j]=sz.length;q.push(j);}}}sz.push(q.length);}
 const main=sz.indexOf(Math.max(...sz));R.roadComponents=sz.length;R.orphanRoadTiles=sz.reduce((a,v,k)=>k===main?a:a+v,0);
 let stub=0;for(let i=0;i<NN;i++){if(kind[i]!==K.ROAD||isWide(i))continue;const x=i&NM,y=i>>NS;let n=0;for(const [dx,dy] of DIR)if(rd(x+dx,y+dy))n++;if(n<=1)stub++;}R.deadEnds=stub;
 /* 3. lots without street access (BFS distance from road > 4) */
 const dist=new Uint8Array(NN).fill(99),q=[];for(let i=0;i<NN;i++)if(kind[i]===K.ROAD){dist[i]=0;q.push(i);}for(let h=0;h<q.length;h++){const i=q[h];if(dist[i]>=8)continue;const x=i&NM,y=i>>NS;for(const [dx,dy] of DIR){const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=N||yy>=N)continue;const j=idx(xx,yy);if(dist[j]>dist[i]+1){dist[j]=dist[i]+1;q.push(j);}}}
 let noAcc=0,blt=0,noSpr=0,slope=0;for(let i=0;i<NN;i++){const k=kind[i];if(!((k===K.RES||k===K.COM||k===K.IND)&&lvl[i]))continue;blt++;if(dist[i]>4&&fix[i]!==2&&!isFoot(i))noAcc++;if(lmkA[i]<0&&!objOf(i))noSpr++;const x=i&NM,y=i>>NS;if(!isFlat(x,y))slope++;}
 R.builtTiles=blt;R.lotsNoAccess=noAcc;R.builtNoSprite=noSpr;R.builtOnSlope=slope;
 /* 4. stations with a station building nearby */
 let st=0,stB=0;for(const L of RLINES)for(const k of L.sts){st++;const [x0,y0]=L.path[k];let ok=false;for(let dy=-9;dy<=9&&!ok;dy++)for(let dx=-9;dx<=9;dx++){const x=x0+dx,y=y0+dy;if(x<0||y<0||x>=N||y>=N)continue;const i=idx(x,y);if(kind[i]===K.LMK&&lmkA[i]>=0&&(LMKT[vari[lmkA[i]]]?.id||'').startsWith('rstn')){ok=true;break;}}if(ok)stB++;}R.stations=st;R.stationsWithBuilding=stB;
 /* 5. district fill */
 let lowCells=0;for(const c of GCELLS){let n=0,b=0;for(let y=c.y0;y<=c.y1;y++)for(let x=c.x0;x<=c.x1;x++){const i=idx(x,y);if(terr[i]===TWA)continue;n++;if(kind[i]!==K.EMPTY)b++;}if(n>40&&b/n<.35)lowCells++;}R.cells=GCELLS.length;R.lowFillCells=lowCells;
 /* 6. water roads that are not bridges over straight runs (corners on water) */
 let wCorner=0;for(let i=0;i<NN;i++){if(terr[i]!==TWA||kind[i]!==K.ROAD||isWide(i))continue;const m=roadMask(i&NM,i>>NS);if(m!==5&&m!==10)wCorner++;}R.waterRoadCorners=wCorner;
 /* 7. trains: count and on-path */
 R.trains=TRAINS.length;R.lines=RLINES.length;
 /* 8. landmarks partially on water/road */
 let lmBad=0;for(let i=0;i<NN;i++)if(kind[i]===K.LMK&&terr[i]===TWA)lmBad++;R.lmkOnWater=lmBad;
 R.pop=sim.pop;return JSON.stringify(R);})()
"""
PERF=r"""new Promise(res=>{let n=0,t0=performance.now(),mx=0,last=t0;function f(t){const d=t-last;last=t;if(n>2)mx=Math.max(mx,d);n++;if(t-t0<4000)requestAnimationFrame(f);else res(JSON.stringify({fps:+(n/((t-t0)/1000)).toFixed(1),worst:Math.round(mx)}));}requestAnimationFrame(f);})"""
SCN=[('overview','zoom=1;const c=GCELLS[0];centerOn(Math.round(c.mx),Math.round(c.my));'),
 ('downtown','const c=GCELLS.filter(c=>c.t==="cbd")[0]||GCELLS[0];centerOn(Math.round(c.mx),Math.round(c.my));zoom=3;'),
 ('oldtown','const c=GCELLS.filter(c=>c.t==="old")[0]||GCELLS[0];centerOn(Math.round(c.mx),Math.round(c.my));zoom=8;'),
 ('apartments','const c=GCELLS.filter(c=>c.t==="new")[0]||GCELLS[0];centerOn(Math.round(c.mx),Math.round(c.my));zoom=4;'),
 ('station','const L=RLINES[0];if(L){const q=L.path[L.sts[Math.min(2,L.sts.length-1)]];centerOn(q[0],q[1]);}zoom=5;'),
 ('bridge','let b=-1;for(let i=0;i<NN;i++)if(terr[i]===TWA&&kind[i]===K.ROAD&&isWide(i)){b=i;break;}if(b>=0)centerOn(b&NM,b>>NS);zoom=4;'),
 ('outskirts','const c=GCELLS.filter(c=>c.t==="vil")[0]||GCELLS[GCELLS.length-1];centerOn(Math.round(c.mx),Math.round(c.my));zoom=4;'),
 ('night','const c=GCELLS.filter(c=>c.t==="cbd")[0]||GCELLS[0];centerOn(Math.round(c.mx),Math.round(c.my));zoom=2.5;todMode="night";tod=.95;')]
async def main():
    seeds=[int(a) for a in sys.argv[1:]] or [22,5]
    rep={}
    fp=[f for f in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-DemiLight.ttc'] if os.path.exists(f)]
    font=ImageFont.truetype(fp[0],26) if fp else ImageFont.load_default()
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        pg=await b.new_page(viewport={'width':1200,'height':800});errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)[:300]));pg.on('console',lambda m:errs.append(m.text[:200]) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
        await pg.goto('file://'+os.path.join(os.path.dirname(D),'build','dbg.html'));await pg.wait_for_function("document.getElementById('loading').hidden",timeout=400000)
        for sd in seeds:
            await pg.evaluate('__pc.ev('+json.dumps("newCity(%d,'rand');todMode='auto';1"%sd)+')');await pg.wait_for_timeout(1500)
            r=json.loads(await pg.evaluate('__pc.ev('+json.dumps(CHECK)+')'))
            shots=[];perf={}
            for name,js in SCN:
                await pg.evaluate('__pc.ev('+json.dumps("todMode='auto';tod=.42;"+js+"1")+')');await pg.wait_for_timeout(3500)
                f=f'{O}/qa_{sd}_{name}.png';await pg.screenshot(path=f);shots.append((name,f))
                if name in ('overview','downtown','oldtown'):perf[name]=json.loads(await pg.evaluate(PERF))
            r['perf']=perf;rep[sd]=r
            ims=[];W,H=600,400
            for name,f in shots:
                im=Image.open(f).resize((W,H));d=ImageDraw.Draw(im);d.rectangle((0,0,len(name)*15+24,36),fill=(15,16,20));d.text((10,2),name,font=font,fill=(255,255,255));ims.append(im)
            sheet=Image.new('RGB',(W*2,H*4),(10,10,12))
            for k,im in enumerate(ims):sheet.paste(im,((k%2)*W,(k//2)*H))
            sheet.save(f'{O}/qa_{sd}.png')
        rep['errors']=errs[:10]
        await b.close()
    json.dump(rep,open(f'{O}/qa_report.json','w'),ensure_ascii=False,indent=1);print(json.dumps(rep,ensure_ascii=False))
asyncio.run(main())
