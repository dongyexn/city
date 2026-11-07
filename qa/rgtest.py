import asyncio,sys,json
from playwright.async_api import async_playwright
JS=r"""
(()=>{const seen=new Set(),out=[];
function walk(x,path,d){if(!x||typeof x!=='object'||seen.has(x)||d>7)return;seen.add(x);
 if(x.rg&&x.c){out.push([x,path]);}
 if(Array.isArray(x)){x.forEach((y,i)=>walk(y,path+'['+i+']',d+1));return;}
 if(x instanceof HTMLCanvasElement||x instanceof CanvasRenderingContext2D)return;
 if(Object.getPrototypeOf(x)!==Object.prototype)return;
 for(const k in x){if(k==='rg'||k==='c'||k==='c2'||k==='lit'||k==='lit2'||k==='sn'||k==='sn2'||k==='shd')continue;walk(x[k],path+'.'+k,d+1);}}
for(let t=0;t<LMKT.length;t++)lmkGet(t,1);
walk(SP,'SP',0);
let bad=[],tot=0,tm=0,px=0;
for(const [o,p] of out){const c0=o.c;o.c=null;const t0=performance.now();regenC(o);tm+=performance.now()-t0;tot++;
 const a=c0.getContext('2d').getImageData(0,0,c0.width,c0.height).data,c1=o.c;
 if(c1.width!==c0.width||c1.height!==c0.height){bad.push(p+' size');continue;}
 const b=c1.getContext('2d').getImageData(0,0,c1.width,c1.height).data;let n=0;for(let i=0;i<a.length;i+=4){if(Math.abs(a[i]-b[i])>6||Math.abs(a[i+1]-b[i+1])>6||Math.abs(a[i+2]-b[i+2])>6||Math.abs(a[i+3]-b[i+3])>6)n++;}
 px+=a.length/4;if(n>a.length/4*0.002)bad.push(p+' '+n+'/'+(a.length/4));}
return {tot,ms:Math.round(tm),avg:+(tm/tot).toFixed(2),mpx:Math.round(px/1e6),nbad:bad.length,bad:bad.slice(0,60)};})()
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width':1200,'height':800});errs=[]
        await pg.add_init_script('window.__NODROP=1')
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.goto('file://'+__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))),'build','dbg.html'));await pg.wait_for_function("document.getElementById('loading').hidden", timeout=400000)
        r=await pg.evaluate('__pc.ev('+json.dumps(JS)+')')
        print(json.dumps(r,ensure_ascii=False,indent=0)[:6000]);print('errs',errs[:5]);await b.close()
asyncio.run(main())
