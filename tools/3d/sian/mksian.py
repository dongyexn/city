import os,sys,base64,asyncio,json
D=os.path.dirname(os.path.abspath(__file__))
html='''<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0">
<script type="importmap">{"imports":{"three":"http://l/node_modules/three/build/three.module.js","three/addons/":"http://l/node_modules/three/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
'''+open(os.path.join(D,'sian_obj.js')).read()+'''
const R=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=1.05;R.outputColorSpace=THREE.SRGBColorSpace;R.shadowMap.enabled=true;R.shadowMap.type=THREE.PCFSoftShadowMap;R.setPixelRatio(1);
const ENV=new THREE.PMREMGenerator(R).fromScene(new RoomEnvironment(),.04).texture;
const gtx=(()=>{const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');g.fillStyle='#7ccc4c';g.fillRect(0,0,128,128);let s=3;const r=()=>{s=(s*16807)%2147483647;return s/2147483647;};for(let k=0;k<60;k++){g.fillStyle=`rgba(${r()<.5?'60,140,40':'170,230,110'},.22)`;g.beginPath();g.ellipse(r()*128,r()*128,6+r()*10,4+r()*6,0,0,7);g.fill();}const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;return t;})();
const cell=(fn,foot,S)=>{const sc=new THREE.Scene();sc.environment=ENV;sc.add(new THREE.HemisphereLight('#ffffff','#b8c4d0',1.15));const L=new THREE.DirectionalLight('#fff6e8',2.6);L.position.set(-3,9,6);L.castShadow=true;L.shadow.mapSize.set(2048,2048);L.shadow.bias=-.0004;L.shadow.normalBias=.02;const sh=L.shadow.camera;sh.left=sh.bottom=-foot*1.6;sh.right=sh.top=foot*1.6;sh.near=.1;sh.far=40;sc.add(L);sc.add(L.target);
 const root=new THREE.Group();sc.add(root);const t=gtx.clone();t.repeat.set(foot,foot);t.needsUpdate=true;const bh=foot<1?.07:.3;const base=new THREE.Mesh(new RoundedBoxGeometry(foot,bh,foot,2,Math.min(.04,bh/2-.005)),[new THREE.MeshStandardMaterial({color:'#b07f58',roughness:.9}),new THREE.MeshStandardMaterial({color:'#b07f58',roughness:.9}),new THREE.MeshStandardMaterial({map:t,roughness:.8}),new THREE.MeshStandardMaterial({color:'#b07f58'}),new THREE.MeshStandardMaterial({color:'#b07f58',roughness:.9}),new THREE.MeshStandardMaterial({color:'#b07f58',roughness:.9})]);base.position.y=.13-bh/2;base.receiveShadow=true;root.add(base);
 const S2=SIAN(THREE,RoundedBoxGeometry,mergeGeometries,root);const lib=Object.assign({},S2.B1,S2.B2,S2.P);lib[fn]();
 const bb=new THREE.Box3().setFromObject(root),ce=bb.getCenter(new THREE.Vector3());const cam=new THREE.OrthographicCamera(-1,1,1,-1,.1,100);const dir=new THREE.Vector3(1,.737,1).normalize();cam.position.copy(ce).addScaledVector(dir,30);cam.lookAt(ce);cam.updateMatrixWorld();
 let mx=0,my=0;const v=new THREE.Vector3();for(const x of [bb.min.x,bb.max.x])for(const y of [bb.min.y,bb.max.y])for(const z of [bb.min.z,bb.max.z]){v.set(x,y,z).applyMatrix4(cam.matrixWorldInverse);mx=Math.max(mx,Math.abs(v.x));my=Math.max(my,Math.abs(v.y));}const hh=Math.max(mx,my)*1.06;cam.left=-hh;cam.right=hh;cam.top=hh;cam.bottom=-hh;cam.updateProjectionMatrix();
 R.setSize(S,S);R.setClearColor(0,0);R.render(sc,cam);const c=document.createElement('canvas');c.width=S;c.height=S;c.getContext('2d').drawImage(R.domElement,0,0);return c;};
window.sheet=(items,cols,S,title)=>{const rows=Math.ceil(items.length/cols),LH=44,TH=70,W=cols*S,H=TH+rows*(S+LH);const o=document.createElement('canvas');o.width=W;o.height=H;const g=o.getContext('2d');const q=g.createLinearGradient(0,0,0,H);q.addColorStop(0,'#cfe9fb');q.addColorStop(1,'#eaf5fd');g.fillStyle=q;g.fillRect(0,0,W,H);
 g.fillStyle='#1f2a36';g.font='bold 34px sans-serif';g.fillText(title,24,48);
 items.forEach(([fn,foot,lab,sub],i)=>{const x=(i%cols)*S,y=TH+((i/cols)|0)*(S+LH);try{g.drawImage(cell(fn,foot,S),x,y);}catch(e){g.fillStyle='#c00';g.font='16px sans-serif';g.fillText(String(e).slice(0,60),x+10,y+40);console.error(fn,e.stack);}g.fillStyle='#1f2a36';g.font='bold 22px sans-serif';g.textAlign='center';g.fillText(lab,x+S/2,y+S+18);g.fillStyle='#5a6b7c';g.font='16px sans-serif';g.fillText(sub,x+S/2,y+S+38);g.textAlign='left';});
 return o.toDataURL('image/png');};
window.ready=1;
</script></body></html>'''
open(os.path.join(D,'sian.html'),'w').write(html)
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page();pg.on('pageerror',lambda e:print('ERR',str(e)[:400]));pg.on('console',lambda m:print('C',m.text[:400]) if m.type=='error' else None)
        async def h(route):
            path=os.path.join(D,route.request.url.split('http://l/')[1].split('?')[0])
            await route.fulfill(path=path,content_type='application/javascript' if path.endswith('.js') else 'text/html')
        await pg.route('http://l/**',h);await pg.goto('http://l/sian.html');await pg.wait_for_function('window.ready===1',timeout=120000)
        for name,items,cols,S,title in json.loads(open(os.path.join(D,'sian_items.json')).read()):
            if len(sys.argv)>1 and name not in sys.argv[1:]:continue
            d=await pg.evaluate('sheet(%s,%d,%d,%s)'%(json.dumps(items),cols,S,json.dumps(title)))
            open(os.path.join(D,name+'.png'),'wb').write(base64.b64decode(d.split(',')[1]));print('ok',name)
        await b.close()
asyncio.run(main())
