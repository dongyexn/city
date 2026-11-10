import asyncio,base64,os,mimetypes
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page();pg.on('pageerror',lambda e:print('ERR',str(e)[:400]))
        async def h(route):
            path=os.path.join(D,route.request.url.split('http://l/')[1].split('?')[0]);ct=mimetypes.guess_type(path)[0] or 'text/plain'
            if path.endswith('.js'):ct='application/javascript'
            await route.fulfill(path=path,content_type=ct)
        await pg.route('http://l/**',h);await pg.goto('http://l/catalog.html');await pg.wait_for_function('window.ready===1',timeout=120000)
        d=await pg.evaluate('render(2600,1600)');open(os.path.join(D,'catalog.png'),'wb').write(base64.b64decode(d.split(',')[1]));await b.close()
asyncio.run(main())
