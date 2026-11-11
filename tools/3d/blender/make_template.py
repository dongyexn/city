# 주민 템플릿 합치기: ppl.py TEMPLATE=… 로 만든 주민별 .blend 를 한 파일(people_template.blend)에 모은다.
# 사용: bpy가 설치된 파이썬으로  python make_template.py <주민별 blend 폴더> <출력.blend>
import bpy,sys,os,glob
src,out=sys.argv[-2],sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
fs=sorted(glob.glob(os.path.join(src,'v*.blend')),key=lambda p:int(os.path.basename(p)[1:-6]))
for k,f in enumerate(fs):
    with bpy.data.libraries.load(f,link=False) as (a,b):b.collections=[c for c in a.collections]
    for c in b.collections:
        sc.collection.children.link(c)
        for o in c.objects:
            if o.parent is None:o.location.x+=k*1.0
for m in bpy.data.materials:
    if '.' in m.name and m.name.rsplit('.',1)[1].isdigit():pass
# 바닥 안내판(변환할 때 무시됨)
me=bpy.data.meshes.new('GUIDE_FLOOR');me.from_pydata([(-.6,-.6,0),(len(fs)-.4,-.6,0),(len(fs)-.4,.6,0),(-.6,.6,0)],[],[(0,1,2,3)])
g=bpy.data.objects.new('GUIDE_FLOOR',me);sc.collection.objects.link(g);g.display_type='WIRE';g.hide_select=True;g.hide_render=True
t=bpy.data.texts.new('README')
t.write("""ISLE 주민 템플릿
- 컬렉션 하나 = 주민 한 명. 새 주민은 컬렉션을 통째로 복제(Shift+D 아님, 아웃라이너에서 Duplicate Collection)해서 고친다.
- 앞쪽 = -Y(정면 뷰 숫자패드 1), 위 = +Z, 바닥 = Z 0. 키는 지금 크기(약 1)를 유지.
- 이름 규칙: ARM_L, ARM_R, LEG_L, LEG_R 로 시작하는 오브젝트는 걸을 때 흔들린다. 나머지(HEAD, HAIR, BODY, SHIRT…)는 몸통에 고정.
  L = 캐릭터 기준 왼쪽 = +X 쪽.
- 관절 위치 = ARM_L / ARM_R / LEG_L / LEG_R 오브젝트의 원점(주황 점). 팔 회전은 이 점을 중심으로.
  소매·손·신발은 이 오브젝트의 자식이라 같이 움직인다. 팔을 벌린 자세를 원하면 ARM_L 을 회전시켜 두면 그 자세가 기본 자세가 된다.
- 색은 머티리얼의 Base Color 한 가지만 쓴다(텍스처는 무시). 한 오브젝트에 머티리얼 여러 개 가능.
- 폴리곤 수는 신경 쓰지 않아도 된다. 변환할 때 주민 한 명당 약 3,000 삼각형으로 자동으로 줄인다.
  너무 잘게 깎은 디테일은 줄이면서 사라질 수 있다.
- GUIDE 로 시작하는 오브젝트, 렌더에서 숨긴 오브젝트는 무시된다.
- 다 되면 이 .blend 파일을 그대로 보내면 된다.
""")
bpy.ops.wm.save_as_mainfile(filepath=out,compress=True);print('saved',out,len(fs))
