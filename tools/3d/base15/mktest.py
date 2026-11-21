# python3 tools/3d/base15/mktest.py -> build/float-resident-test.html
# 새 주민 시험판: 게임 빌드에 새 베이스 모델을 싣고(B15=1) 기존 주민과 바꿔 보는 단추·수치 표시(hud.js)를 얹는다. 아티팩트로 게시해 기기에서 확인한다.
import os,subprocess,sys
D=os.path.dirname(os.path.abspath(__file__));T=os.path.dirname(D);R=os.path.dirname(os.path.dirname(T))
subprocess.run([sys.executable,os.path.join(T,'mkplay.py'),'11'],check=True,stdout=subprocess.DEVNULL,env=dict(os.environ,B15='1'))
h=open(os.path.join(T,'play.html'),encoding='utf-8').read();tag='<script type="importmap">'
assert h.count('<title>FLOAT</title>')==1 and h.count(tag)==1 and '<script type="application/json" id="b15">' in h
h=h.replace('<title>FLOAT</title>','<title>FLOAT 주민 시험</title>').replace(tag,'<script>window.__B15DEF="b";</script>\n'+tag)+'<script>'+open(os.path.join(D,'hud.js'),encoding='utf-8').read()+'</script>\n'
os.makedirs(os.path.join(R,'build'),exist_ok=True);out=os.path.join(R,'build','float-resident-test.html')
open(out,'w',encoding='utf-8').write(h);os.remove(os.path.join(T,'play.html'));print(out,len(h))
