# python3 tools/3d/pages.py  -> index.html (GitHub Pages: 3D 섬 도시). mkplay.py 결과(play.html)를 문서 머리말·매니페스트·서비스워커와 함께 감싼다.
import os,subprocess,sys
D=os.path.dirname(os.path.abspath(__file__));R=os.path.dirname(os.path.dirname(D))
subprocess.run([sys.executable,os.path.join(D,'mkplay.py'),'11'],check=True,stdout=subprocess.DEVNULL)
body=open(os.path.join(D,'play.html')).read()
t=body.index('</style>')+len('</style>')
head='<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n<meta name="theme-color" content="#3fa2f5">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icons/icon-192.png">\n<link rel="apple-touch-icon" href="icons/icon-192.png">\n'
out=head+body[:t]+'\n</head>\n<body>\n'+body[t:]+"<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));</script>\n</body>\n</html>\n"
open(os.path.join(R,'index.html'),'w').write(out);os.remove(os.path.join(D,'play.html'));print('index.html',len(out))
