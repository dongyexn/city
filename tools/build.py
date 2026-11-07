# python3 tools/build.py  -> index.html (Pages) + build/pixel-city.html (artifact) + build/dbg.html (test hook)
import os,subprocess
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));S=lambda *p:os.path.join(R,*p)
subprocess.run(['node','--check',S('src','game.js')],check=True)
h=open(S('src','head.html')).read();s=open(S('src','game.js')).read();p=h+'<script>\n'+s+'\n</script>\n'
os.makedirs(S('build'),exist_ok=True);open(S('build','pixel-city.html'),'w').write(p)
d=open(S('tools','hook.js')).read().strip();i=p.rindex('})();\n');open(S('build','dbg.html'),'w').write(p[:i]+d+'\n'+p[i:])
pre='<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="theme-color" content="#7fb4e8">\n'
i=p.index('<script>');head,body=p[:i],p[i:];j=head.index('</style>')+len('</style>')
open(S('index.html'),'w').write(pre+head[:j]+'\n</head>\n<body>\n'+head[j:]+body+'</body>\n</html>\n');print('built')
