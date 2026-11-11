# 주민 모델링 (Blender)

1. `people_template.blend`를 Blender 4.x 이상에서 연다. 컬렉션 하나가 주민 한 명이다.
2. 고치거나 새로 만든다. 규칙은 파일 안 Text Editor의 `README`에도 있다.
   - 정면 = -Y, 위 = +Z, 바닥 = Z 0, 키는 지금 크기 유지.
   - `ARM_L` `ARM_R` `LEG_L` `LEG_R`로 시작하는 오브젝트만 걸을 때 흔들린다. 나머지는 몸통에 고정.
   - 관절 = 위 네 오브젝트의 원점. 회전해 둔 자세가 기본 자세가 된다.
   - 색은 머티리얼 Base Color만 쓴다. `GUIDE`로 시작하거나 렌더에서 숨긴 오브젝트는 무시.
   - 폴리곤 수는 자유. 변환 시 주민당 약 3,600 삼각형으로 줄인다.
3. 저장한 `.blend`를 보내면 변환해서 게임에 넣는다.

변환: `python import_people.py 입력.blend 출력.json` (bpy 필요) → `tools/3d/ppl.json` 교체 → `python3 tools/3d/pages.py`.
템플릿 재생성: `people.py`를 `VAR=n TEMPLATE=…/vn.blend`로 실행 → `make_template.py 폴더 출력.blend`.

# 곰 모델 각색
`adapt_bear.py`: CGTrader 무료 모델 Sunny Lazy Bear(.blend)를 사람 주민 8명 템플릿으로 각색. 원본 모델과 각색 .blend는 재배포 금지라 저장소에 넣지 않는다(게임에는 변환된 메시만 포함).
사용: `FACE=dot|happy|bean|sleepy python adapt_bear.py 원본.blend 출력.blend`
