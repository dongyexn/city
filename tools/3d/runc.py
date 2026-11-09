import asyncio,base64,os,mimetypes,json,sys
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
async def main():
    sd=int(sys.argv[1]) if len(sys.argv)>1 else 22
    views=json.loads(sys.argv[2]) if len(sys.argv)>2 else {"all":{"k":150},"zoom":{"k":42}}
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page();pg.on('pageerror',lambda e:print('ERR',str(e)[:300]));pg.on('console',lambda m:print('C',m.text[:200]) if m.type=='error' else None)
        async def h(route):
            path=os.path.join(D,route.request.url.split('http://l/')[1].split('?')[0]);ct=mimetypes.guess_type(path)[0] or 'text/plain'
            if path.endswith('.js'):ct='application/javascript'
            await route.fulfill(path=path,content_type=ct)
        await pg.route('http://l/**',h);await pg.add_init_script('window.NOCURB=%d'%int(os.environ.get('NOCURB','0')));await pg.goto('http://l/city3d.html');await pg.wait_for_function('window.ready===1',timeout=300000)
        for n,v in views.items():
            d=await pg.evaluate('render(%d,1600,1000,%s)'%(sd,json.dumps(v)));print(n,await pg.evaluate('JSON.stringify(window.STAT)'));open(os.path.join(D,'c_%d_%s.png'%(sd,n)),'wb').write(base64.b64decode(d.split(',')[1]))
        await b.close()
asyncio.run(main())
