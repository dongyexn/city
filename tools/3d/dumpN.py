import asyncio,json,sys,os
from playwright.async_api import async_playwright
SEEDS=[int(a) for a in sys.argv[1:]]
EXP=r"""(()=>{const b=a=>{let s='';const u=new Uint8Array(a.buffer,a.byteOffset,a.byteLength);for(let i=0;i<u.length;i+=8192)s+=String.fromCharCode.apply(null,u.subarray(i,i+8192));return btoa(s);};
return JSON.stringify({N,HN,TWA,K,H:b(H),terr:b(terr),kind:b(kind),lvl:b(lvl),vari:b(vari),deco:b(deco),lmkA:b(lmkA),fix:b(fix),H0:b(H0||H),LVL:b(LVL||new Uint8Array(NN)),ocean:b(OCEAN),wnear:b(wnear),hmin:Math.min(...H),hmax:Math.max(...H)});})()"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        pg=await b.new_page(viewport={'width':1200,'height':800});pg.on('pageerror',lambda e:print('ERR',str(e)[:200]))
        await pg.goto('file:///home/claude/city/build/dbg.html');await pg.wait_for_function("document.getElementById('loading').hidden",timeout=200000)
        for sd in SEEDS:
            await pg.evaluate('__pc.ev('+json.dumps("newCity(%d,'rand');1"%sd)+')');await pg.wait_for_timeout(300)
            d=await pg.evaluate('__pc.ev('+json.dumps(EXP)+')');open('maps/map_%d.json'%sd,'w').write(d);print(sd,flush=True)
        await b.close()
asyncio.run(main())
