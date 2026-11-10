import asyncio,os,json,collections
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page(viewport={'width':1280,'height':800});pg.on('pageerror',lambda e:print('ERR',str(e)[:400]))
        async def h(route):
            u=route.request.url
            path=os.path.join(D,'node_modules/three',u.split('three@0.160.0/')[1]) if 'three@0.160.0/' in u else os.path.join(D,u.split('http://l/')[1].split('?')[0])
            body=open(path,'rb').read()
            if path.endswith('play.html'):body=b'<!doctype html><html><head><meta charset="utf-8"></head><body>'+body+b'</body></html>'
            await route.fulfill(body=body,content_type='application/javascript' if path.endswith('.js') else 'text/html')
        await pg.route('**/*',h);await pg.goto('http://l/play.html');await pg.wait_for_function('window.__ready===1',timeout=300000)
        c=await pg.context.new_cdp_session(pg);await c.send('Profiler.enable');await c.send('Profiler.setSamplingInterval',{'interval':500});await c.send('Profiler.start')
        ms=await pg.evaluate("(()=>{const t=performance.now();window.__dbg.rebuild();return Math.round(performance.now()-t)})()")
        pr=(await c.send('Profiler.stop'))['profile'];print('rebuild ms',ms)
        src=open(os.path.join(D,'play.html')).read().split('\n')
        nodes={n['id']:n for n in pr['nodes']};dt=pr['timeDeltas'];self_=collections.Counter()
        for s,d in zip(pr['samples'],dt):
            f=nodes[s]['callFrame'];self_[(f['functionName'] or '?',f['url'].split('/')[-1][:18],f['lineNumber'])]+=d
        tot=sum(self_.values())
        for (fn,u,ln),v in self_.most_common(28):
            ctx=src[ln-0][:70] if u.startswith('play') and ln<len(src) else ''
            print('%5.0fms %-22s %-14s L%d %s'%(v/1000,fn[:22],u,ln,ctx))
        await b.close()
asyncio.run(main())
