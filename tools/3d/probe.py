import asyncio,json,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        pg=await b.new_page(viewport={'width':1200,'height':800});pg.on('pageerror',lambda e:print('ERR',str(e)[:200]))
        await pg.goto('file:///home/claude/city/build/dbg.html');await pg.wait_for_function("document.getElementById('loading').hidden",timeout=200000)
        for sd in sys.argv[1:]:
            await pg.evaluate('__pc.ev('+json.dumps("newCity(%s,'rand');1"%sd)+')');await pg.wait_for_timeout(800)
            print(sd,await pg.evaluate('__pc.ev('+json.dumps("JSON.stringify({cells:GCELLS.length,pop:sim.pop,g:window.__g})")+')'))
        await b.close()
asyncio.run(main())
