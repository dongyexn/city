# 새 주민 베이스 (1.5등신 클레이)

머리가 키의 2/3인 1.5등신 캐릭터. 부위별 거리장(SDF)을 부드럽게 합쳐 한 덩어리 표면을 뽑으므로 관절 이음새가 형태로 드러나지 않는다.
치수는 `params.json`(조정 도구에서 확정한 값)에 있고, `chibi15.py`의 `Q` 기본값을 덮어쓴다.

| 파일 | 내용 |
|---|---|
| `chibi15.py` | 형태 생성(거리장 → 메시). `PARAMS=params.json MESH=mesh.npz python3 chibi15.py` |
| `render15.py` | 블렌더(bpy): 클레이 재질·뼈대(19개)·가중치·얼굴 파츠, 점검 렌더, GLB 내보내기 |
| `params.json` | 확정 치수 |
| `base15.glb` | 게임용 모델: 스킨 메시 1개(약 2,700 삼각형), 얼굴은 꼭짓점 색으로 구움 |
| `mktest.py`, `hud.js` | 시험판 빌드(기존 주민과 바꿔 보는 단추, 그리기 수치 표시) |

게임용 모델 다시 만들기(bpy, scikit-image 필요):

```
cd tools/3d/base15
PARAMS=params.json MESH=mesh.npz python3 chibi15.py
PARAMS=params.json MESH=mesh.npz JOBS=gglb GNAME=base15 GTRI=2000 GFACE=0.3 OUTD=. python3 render15.py
```

게임 쪽(`play_game.js`의 "새 주민" 구역): 모델 자료를 실은 빌드(`B15=1 python3 tools/3d/mkplay.py`)에서만 켜지고, 기본 빌드(`pages.py`)는 기존 주민 그대로다.
헤어·옷이 준비될 때까지 기본 화면에는 넣지 않는다. 시험판: `python3 tools/3d/base15/mktest.py` → `build/float-resident-test.html`.

좌표: x 좌우, -y 정면, z 위, 바닥 z=0, 머리 높이 ≈ 1. 게임에서는 배율 .33(기존 주민과 같은 키).
