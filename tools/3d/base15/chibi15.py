# 1.5등신 클레이 베이스 (머리 높이 = 1.0, 전체 약 1.53)
# 방식: 부위별 거리장(SDF)을 부드럽게 합쳐 한 덩어리 표면을 뽑는다 → 관절 이음새가 형태로 드러나지 않음
# 좌표: x 좌우, -y 정면, z 위. 바닥 z=0
import os, sys, math, numpy as np
from skimage import measure

D0 = os.path.dirname(os.path.abspath(__file__))
STEP = float(os.environ.get('STEP', 0.006))

# ------------------------------------------------------------------ 치수(전부 여기서 조정). 조정 도구(웹)가 내보낸 JSON을 PARAMS=파일 로 주면 그 값으로 덮어쓴다
import json
Q = dict(headW=0.465, headTop=1.465, headD=0.478, chinFwd=0.286, chinW=0.272, chinZ=0.686,
         eyeX=0.195, eyeZ=0.840, sockD=0.030, noseZ=0.735, noseH=0.021, mouthZ=0.657, muzzH=0.021, lipD=0.009, cheekH=0.012,
         eyeW=0.049, eyeH=0.070, browDZ=0.104, browLen=0.053, browTilt=0.0, blushDX=0.085, blushDZ=-0.073, blushW=0.070, mouthW=0.054, mouthCurve=0.034,
         earX=0.488, earY=-0.068, earZ=0.785, earS=1.0, earYaw=50.0, earTilt=0.10,
         shX=0.138, shZ=0.456, armAng=42.0, armLen=1.0, armR=0.050, handR=0.058,
         torsoW=0.170, hipZ=0.238, legX=0.094, legR=0.076, footL=0.122, footH=0.048, bodyY=0.0, faceD=0.478,
         hlFront=1.085, hlCorner=1.03, hlTemple=0.93, hlSide=0.86, hlSideAz=66.0, hlEar=0.915, hlNape=0.67, hairT=0.030, hlBack=0.8025, hlBackAz=96.0)
if os.environ.get('PARAMS'):
    _q = json.load(open(os.environ['PARAMS'], encoding='utf-8'))
    for _k, _v in _q.items():
        if _k in Q: Q[_k] = float(_v)
if os.environ.get('ARMS'): Q['armLen'] = float(os.environ['ARMS'])
if os.environ.get('EARYAW'): Q['earYaw'] = float(os.environ['EARYAW'])
HEAD_BOT = 0.535
EYE_Z, EYE_X = Q['eyeZ'], Q['eyeX']
NOSE_Z, MOUTH_Z = Q['noseZ'], Q['mouthZ']
EAR = (Q['earX'], Q['earY'], Q['earZ']); EAR_S = Q['earS']
EAR_YAW = math.radians(Q['earYaw'])   # 귀를 세로축으로 돌린 각(0 = 머리 옆면과 나란히, 클수록 귀 면이 정면을 봄)
SH = np.array([Q['shX'], 0.010, Q['shZ']])  # 어깨
ADIR = np.array([math.cos(math.radians(Q['armAng'])), 0.0, -math.sin(math.radians(Q['armAng']))])   # 팔 방향(수평에서 armAng° 아래)
ARMS = Q['armLen']
EL, WR, HN = 0.075 * ARMS, 0.150 * ARMS, 0.150 * ARMS + 0.046      # 어깨에서 팔꿈치·손목·손 중심까지 거리
HIP = np.array([Q['legX'], 0.005, Q['hipZ']]); ANK = np.array([Q['legX'] + 0.002, 0.008, 0.058]); KNEE = (HIP + ANK) / 2
TOE = np.array([Q['legX'] + 0.004, -(Q['footL'] + 0.008), Q['footH'] / 2])
BY = np.array([0.0, Q['bodyY'], 0.0])

def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)
def smax(a, b, k): return -smin(-a, -b, k)
def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def ell(X, Y, Z, c, r):
    qx, qy, qz = X - c[0], Y - c[1], Z - c[2]
    k0 = np.sqrt((qx / r[0]) ** 2 + (qy / r[1]) ** 2 + (qz / r[2]) ** 2)
    k1 = np.sqrt((qx / r[0] ** 2) ** 2 + (qy / r[1] ** 2) ** 2 + (qz / r[2] ** 2) ** 2)
    return np.where(k1 > 1e-9, k0 * (k0 - 1) / np.maximum(k1, 1e-9), -float(np.min([np.min(x) for x in r])))

def sell(X, Y, Z, c, r, p):
    """위에서 본 단면이 둥근 사각에 가까운 타원체(얼굴 정면을 평평하게)"""
    qx, qy, qz = np.abs(X - c[0]) / r[0], np.abs(Y - c[1]) / r[1], (Z - c[2]) / r[2]
    k0 = (qx ** p + qy ** p) ** (1.0 / p)
    return (np.sqrt(k0 * k0 + qz * qz) - 1) * (r[0] + r[1] + r[2]) / 3

def sph(X, Y, Z, c, r): return np.sqrt((X - c[0]) ** 2 + (Y - c[1]) ** 2 + (Z - c[2]) ** 2) - r

def rcone(X, Y, Z, a, b, r1, r2):
    """양 끝 반지름이 다른 둥근 원뿔대(팔·다리)"""
    ba = b - a; l2 = float(ba @ ba); rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
    px, py, pz = X - a[0], Y - a[1], Z - a[2]
    y = px * ba[0] + py * ba[1] + pz * ba[2]; z = y - l2
    cx, cy, cz = px * l2 - ba[0] * y, py * l2 - ba[1] * y, pz * l2 - ba[2] * y
    x2 = cx * cx + cy * cy + cz * cz; y2 = y * y * l2; z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    d3 = (np.sqrt(x2 * a2 * il2) + y * rr) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))

def gauss(X, Z, cx, cz, sx, sz): return np.exp(-(((X - cx) / sx) ** 2 + ((Z - cz) / sz) ** 2))

def core_sdf(X, Y, Z):
    """귀를 뺀 머리(두상 + 얼굴 굴곡)"""
    A = np.abs(X)
    # ---- 머리: 넓고 낮은 볼 + 둥근 두개 + 앞아래 턱 볼륨
    cran = ell(X, Y, Z, (0, 0.022, 1.060), (Q['headW'] + 0.005, Q['faceD'] + (Q['headD'] - Q['faceD']) * sstep(-0.06, 0.06, Y - 0.022), Q['headTop'] - 1.060))   # 앞(이마)과 뒤(뒤통수) 깊이를 따로
    jaw = sell(X, Y, Z, (0, 0.000, 0.900), (Q['headW'], 0.465 + (Q['headD'] - 0.013 - 0.465) * sstep(-0.06, 0.06, Y), 0.365), 2.5)
    chin = ell(X, Y, Z, (0, -Q['chinFwd'], Q['chinZ']), (Q['chinW'], 0.190, 0.155))
    head = smin(smin(cran, jaw, 0.12), chin, 0.12)
    # 얼굴 굴곡(정면에만): 눈자리는 살짝 오목, 볼·입 주변·코는 볼록 → 옆에서 보면 이마-눈-코-입이 완만한 S선
    fw = sstep(0.02, -0.22, Y)
    sock = gauss(A, Z, EYE_X, EYE_Z, 0.120, 0.125)
    lip = gauss(X, Z, 0.0, MOUTH_Z, 0.050, 0.020)
    cheek = gauss(A, Z, 0.270, 0.715, 0.110, 0.095)
    muzz = gauss(X, Z, 0.0, MOUTH_Z + 0.015, 0.140, 0.080)
    nose = gauss(X, Z, 0.0, NOSE_Z, 0.032, 0.030)
    head = head + fw * (Q['sockD'] * sock - Q['cheekH'] * cheek - Q['muzzH'] * muzz - Q['noseH'] * nose + Q['lipD'] * lip)
    return head

def parts(X, Y, Z):
    """부위별 거리장. 좌우 대칭(|x|)"""
    A = np.abs(X); P = {'_z': Z}; Yb = Y - Q['bodyY']                              # 몸은 머리 밑에서 앞뒤로 옮길 수 있음(bodyY)
    head = core_sdf(X, Y, Z)
    # 귀: 납작한 타원 + 안쪽 오목
    zl = Z - EAR[2]; es = EAR_S * (1 + 0.12 * np.clip(zl / (0.078 * EAR_S), -1, 1))                    # 위가 조금 넓고 아래는 턱선으로 흘러듦
    dx = A - EAR[0] - Q['earTilt'] * zl; dy = Y - EAR[1]; ce, se = math.cos(EAR_YAW), math.sin(EAR_YAW)
    xl = (dx * ce - dy * se) / es                                                    # 귀 면의 법선 방향(앞·바깥)
    yl = (dx * se + dy * ce) / es                                                    # 귀가 뻗는 방향(바깥·뒤): 뿌리는 머리에, 끝은 바깥으로
    ear = ell(xl, yl, zl / EAR_S, (0, 0, 0), (0.030, 0.050, 0.078)) * EAR_S                             # 두툼한 반달 덩어리
    ear = smax(ear, -ell(xl, yl, zl / EAR_S, (0.034, 0.006, 0.000), (0.022, 0.030, 0.050)) * EAR_S, 0.012)   # 정면을 보는 면의 얕은 홈
    P['_core'] = head
    P['head'] = smin(head, ear, 0.020)
    # ---- 목(머리 밑에 거의 숨음), 몸통(가슴 + 조금 더 넓은 배)
    P['neck'] = rcone(X, Yb, Z, np.array([0, 0.018, 0.455]), np.array([0, 0.018, 0.580]), 0.074, 0.068)
    chest = ell(X, Yb, Z, (0, 0.012, 0.415), (Q['torsoW'] - 0.020, 0.120, 0.090))
    _b0 = Q['hipZ'] - 0.044; belly = ell(X, Yb, Z, (0, 0.000, (_b0 + 0.442) / 2), (Q['torsoW'], 0.142, (0.442 - _b0) / 2))
    yoke = rcone(A, Yb, Z, np.array([0.030, 0.014, 0.468]), np.array([SH[0] - 0.030, SH[1], SH[2] - 0.010]), 0.045, 0.036)             # 목에서 어깨로 내려가는 완만한 경사(승모)
    P['torso'] = smin(smin(chest, belly, 0.06), yoke, 0.035)
    # ---- 팔: 어깨→손목 원뿔대, 손은 구 + 앞쪽으로 살짝 나온 엄지
    wr = SH + ADIR * WR; hc = SH + ADIR * HN
    arm = rcone(A, Yb, Z, SH, wr, Q['armR'], Q['armR'] - 0.005)                           # 어깨 끝은 팔과 같은 굵기의 둥근 끝(따로 볼록한 구 없음)
    dsh = np.sqrt((A - SH[0]) ** 2 + (Yb - SH[1]) ** 2 + (Z - SH[2]) ** 2)
    P['_ka'] = 0.022 * (1 - sstep(Q['armR'] + 0.012, Q['armR'] + 0.055, dsh)) + 1e-4       # 팔은 어깨 뿌리에서만 몸통과 녹아 붙고, 그 밖에서 겹치면 붙지 않음
    hk = Q['handR'] / 0.058; hand = sph(A, Yb, Z, hc, Q['handR'])
    th_c = hc + np.array([-0.012, -0.050, 0.014]) * hk
    hand = smin(hand, sph(A, Yb, Z, th_c, 0.023 * hk), 0.022)
    P['arm'] = smin(arm, hand, 0.03)
    # ---- 다리: 허벅지→발목 원뿔대, 발은 신발 꼴(뭉툭한 발끝, 평평한 바닥)
    P['leg'] = rcone(A, Yb, Z, HIP, ANK, Q['legR'], Q['legR'] - 0.005)                                 # 몸통 옆선에서 발까지 일자
    fx = Q['legX'] + 0.004; foot = ell(A, Yb, Z, (fx, -0.040, Q['footH'] - 0.014), (0.074, Q['footL'], Q['footH']))
    foot = smin(foot, sph(A, Yb, Z, (fx, -(Q['footL'] - 0.022), Q['footH'] - 0.010), Q['footH'] + 0.004), 0.03)
    P['foot'] = smax(foot, -(Z - 0.0), 0.014)
    return P

def Z_GROUND(P): return P['_z']

def total(P):
    low = smin(P['leg'], P['foot'], 0.02)
    body = smin(P['torso'], low, 0.045)
    body = smin(body, P['arm'], P['_ka'])
    body = smin(body, P['neck'], 0.07)
    return smax(smin(body, P['head'], 0.022), -Z_GROUND(P), 0.008)

def sdf(X, Y, Z): return total(parts(X, Y, Z))

# ------------------------------------------------------------------ 임시 헤어(뒤통수 크기 판단용 짧은 머리): 두피를 따라 덮는 껍질, 헤어라인 위쪽만
def hl_keys():
    """헤어라인: 정면에서 잰 방위각(°)마다의 높이. 이마 가운데 → 이마 모서리 → 관자 → 구레나룻 → 귀 위 → 귀 뒤 → 목덜미"""
    f, c, t, sd, e, n, sa, hb, ba = Q['hlFront'], Q['hlCorner'], Q['hlTemple'], Q['hlSide'], Q['hlEar'], Q['hlNape'], Q['hlSideAz'], Q['hlBack'], Q['hlBackAz']
    return (np.array([0, 28, 46, 58, sa, sa + 9, ba, ba + 14, ba + 32, 180.0]),
            np.array([f, f - 0.004, c, t, sd, e, e, hb, n + 0.02, n]))
def hairline_z(az):
    """점들을 지나는 매끈한 곡선(계단 없이)"""
    A, Zk = hl_keys(); m = np.zeros(10); m[1:9] = (Zk[2:] - Zk[:-2]) / (A[2:] - A[:-2])
    i = np.clip(np.searchsorted(A, az, side='right') - 1, 0, 8)
    da = A[i + 1] - A[i]; t = np.clip((az - A[i]) / da, 0, 1); t2 = t * t; t3 = t2 * t
    return (2 * t3 - 3 * t2 + 1) * Zk[i] + (t3 - 2 * t2 + t) * da * m[i] + (-2 * t3 + 3 * t2) * Zk[i + 1] + (t3 - t2) * da * m[i + 1]
def hair_sdf(X, Y, Z):
    core = parts(X, Y, Z)['_core']
    az = np.degrees(np.arctan2(np.abs(X), -Y))
    T = Q['hairT'] * (1 + 0.73 * sstep(0.95, 1.30, Z))                    # 정수리 쪽이 조금 더 두껍게
    return smax(core - T, hairline_z(az) - Z, float(np.clip(Q['hairT'] * 0.8, 0.003, 0.022)))

def build_mesh(fn=None):
    fn = fn or sdf
    xs = np.arange(-0.69, 0.69 + 1e-9, STEP); xs = xs - (xs[0] + xs[-1]) / 2       # x=0 대칭
    ys = np.arange(-0.60, 0.60 + 1e-9, STEP); zs = np.arange(-0.03, 1.59, STEP)
    vol = np.empty((len(xs), len(ys), len(zs)), np.float32)
    Xg, Yg = np.meshgrid(xs, ys, indexing='ij')
    for k0 in range(0, len(zs), 24):
        zz = zs[k0:k0 + 24]
        X = np.repeat(Xg[:, :, None], len(zz), 2); Y = np.repeat(Yg[:, :, None], len(zz), 2); Z = np.broadcast_to(zz, X.shape)
        vol[:, :, k0:k0 + 24] = fn(X, Y, Z)
    v, f, n, _ = measure.marching_cubes(vol, 0.0, spacing=(STEP, STEP, STEP))
    v += np.array([xs[0], ys[0], zs[0]])
    return v.astype(np.float64), f.copy()          # 면이 바깥을 보는 순서(뒤집으면 게임에서 안쪽 면이 보임)

def surf_y(x, z, y0=-0.7, y1=0.0):
    """정면에서 (x, z)로 쏜 선이 표면과 만나는 y"""
    ys = np.linspace(y0, y1, 1400); d = sdf(np.full_like(ys, x), ys, np.full_like(ys, z))
    i = int(np.argmax(d < 0)); return float(ys[i])

if __name__ == '__main__':
    v, f = build_mesh(); print('MESH', len(v), len(f), v.min(0), v.max(0))
    np.savez(os.path.join(D0, os.environ.get('MESH', 'mesh.npz')), v=v, f=f)
    if os.environ.get('HAIR'):
        hv, hf = build_mesh(hair_sdf); np.savez(os.path.join(D0, os.environ['HAIR']), v=hv, f=hf); print('HAIR', len(hv))
    # 옆모습 실루엣 수치(이마-눈-코-입-턱의 앞뒤 굴곡)
    for z in (1.2, 1.0, 0.92, EYE_Z, 0.78, NOSE_Z, MOUTH_Z, 0.62, 0.57):
        print('PROFILE z=%.3f  center y=%.4f  eye-x y=%.4f' % (z, surf_y(0, z), surf_y(EYE_X, z)))
