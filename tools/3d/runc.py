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
        for c,t in []:
            d=await pg.evaluate('render(2600,1500,"%s","%s")'%(c,t));open(os.path.join(D,'catalog_%s.png'%c),'wb').write(base64.b64decode(d.split(',')[1]))
        d=await pg.evaluate('renderPeople(2600,1500)');open(os.path.join(D,'people.png'),'wb').write(base64.b64decode(d.split(',')[1]));d=await pg.evaluate('renderPeople(2600,1300,1.75,[0.25,.26,0.25])');open(os.path.join(D,'people_zoom.png'),'wb').write(base64.b64decode(d.split(',')[1]));await b.close();return
        d=await pg.evaluate('renderBig(2600,1700)');open(os.path.join(D,'catalog_big.png'),'wb').write(base64.b64decode(d.split(',')[1]))
        await b.close()
asyncio.run(main())
