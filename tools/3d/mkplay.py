import re,sys,os
D=os.path.dirname(os.path.abspath(__file__));s=open(D+'/block3d.html').read()
def R(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:70]);s=s.replace(a,b)
i=s.index('<script type="module">');j=s.index('</script></body></html>');js=s[i+len('<script type="module">'):j];s=js
R("window.render=async(seed,VW,VH,view)=>{\nconst D=await (await fetch('http://l/map_'+seed+'.json')).json();const u8=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));","window.__TEX=[];const TX=(...a)=>{const t=new THREE.CanvasTexture(...a);if(!window.__KEEPTX)window.__TEX.push(t);return t;};window.OBC={stage:new THREE.Group(),recs:[],map:new Map(),chunks:new Map()};\nwindow.buildCity=(D,r)=>{const u8=a=>a;window.STAT={};")
R("const lmkA=new Int32Array(u8(D.lmkA).buffer),","const lmkA=D.lmkA,")
a=s.index("const r=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});");b=s.index("\n",a);s=s[:a]+s[b+1:]
R("sc.environment=new THREE.PMREMGenerator(r).fromScene(new RoomEnvironment(),.04).texture;","sc.environment=window.__ENV||(window.__ENV=new THREE.PMREMGenerator(r).fromScene(new RoomEnvironment(),.04).texture);")
a=s.index("const asp=VW/VH,k=view.k;");b=s.index("window.ready=1;");s=s[:a]+"return {sc,hT,LH,land,riv,BIGP,PLACED:window.PLACED,bounds:[bx0,bx1,bz0,bz1],water,fw:window.__FW,FL:window.__FL||[],FNT:window.__FNT||[],DET:window.__DET||[],RD:window.__RD,DYN:window.OBC.dyn||[],FLIP,RT};};\n"+s[b+len("window.ready=1;"):]
s=s.replace("new THREE.CanvasTexture(...a)","new __CT(...a)").replace("new THREE.CanvasTexture(","TX(").replace("new __CT(...a)","new THREE.CanvasTexture(...a)")
s=s.replace("L.shadow.mapSize.set(4096,4096)","L.shadow.mapSize.set(SHM,SHM)")
s="const SHM=(navigator.maxTouchPoints>1&&Math.min(screen.width,screen.height)<900)?2048:4096;window.MS2=1;window.NOCURB=1;\n"+s
cdn='https://cdn.jsdelivr.net/npm/three@0.160.0/'
out=open(D+'/play_ui.html').read()+'<script type="application/json" id="map">'+open(D+'/map_%s.json'%(sys.argv[1] if len(sys.argv)>1 else '11')).read()+'</script>\n<script type="importmap">{"imports":{"three":"'+cdn+'build/three.module.js","three/addons/":"'+cdn+'examples/jsm/"}}</script>\n<script type="module">'+s+open(D+'/play_game.js').read()+'</script>\n'
open(D+'/play.html','w').write(out);print(len(out))
