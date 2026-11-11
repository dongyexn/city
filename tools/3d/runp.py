import asyncio,os,mimetypes,sys,json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page(viewport={'width':1280,'height':800});pg.on('pageerror',lambda e:print('ERR',str(e.stack)[:900]));pg.on('console',lambda m:print('C',m.text[:300]) if m.type=='error' else None)
        async def h(route):
            u=route.request.url
            if 'cdn.jsdelivr.net/npm/three@0.160.0/' in u:path=os.path.join(D,'node_modules/three',u.split('three@0.160.0/')[1])
            else:path=os.path.join(D,u.split('http://l/')[1].split('?')[0])
            ct='application/javascript' if path.endswith('.js') else 'text/html'
            body=open(path,'rb').read()
            if path.endswith('play.html'):body=b'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+body+b'</body></html>'
            await route.fulfill(body=body,content_type=ct)
        await pg.route('**/*',h);await pg.goto('http://l/play.html#still');await pg.wait_for_function('window.__ready===1',timeout=150000);await pg.wait_for_timeout(8000)
        await pg.screenshot(path=os.path.join(D,'p0.png'))
        for step in json.loads(sys.argv[1]) if len(sys.argv)>1 else []:
            if step[0]=='click':await pg.get_by_role('button',name=step[1],exact=True).click(timeout=240000)
            elif step[0]=='drag':
                await pg.mouse.move(step[1],step[2]);await pg.mouse.down()
                for k in range(1,9):await pg.mouse.move(step[1]+(step[3]-step[1])*k/8,step[2]+(step[4]-step[2])*k/8)
                await pg.mouse.up()
            elif step[0]=='wheel':await pg.mouse.move(640,400);await pg.mouse.wheel(0,step[1])
            elif step[0]=='shot':await pg.wait_for_timeout(step[2] if len(step)>2 else 9000);await pg.screenshot(path=os.path.join(D,step[1]),timeout=180000)
            elif step[0]=='eval':print(await pg.evaluate(step[1]))
            elif step[0]=='move':await pg.mouse.move(step[1],step[2],steps=4)
            elif step[0]=='key':await pg.keyboard.press(step[1])
            elif step[0]=='down':await pg.mouse.move(step[1],step[2]);await pg.mouse.down();await pg.mouse.up()
        await b.close()
asyncio.run(main())
