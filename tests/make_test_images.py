"""読み取りテスト用の合成スキャン画像を作る（Pillowが必要: pip install pillow）
使い方: python tests/make_test_images.py
tests/out/ に画像(.raw)と正解(expected.json)を出力する。
※ レイアウトの数値は marksheet-saiten.html の LAYOUT と合わせること。
"""
from PIL import Image, ImageDraw
import json, os
S = 8; W, H = 210*S, 297*S
OUT = os.path.join(os.path.dirname(__file__), 'out'); os.makedirs(OUT, exist_ok=True)
ID_ROWS = [46, 52, 58]; Y0, DY, DX = 100, 7.0, 7; COLS = [(30, 37), (115, 122)]

def make(name, n_written, w_size, rot, flip):
    per_col = 25 - n_written * w_size
    nq = per_col * 2
    im = Image.new('L', (W, H), 255); d = ImageDraw.Draw(im)
    for cx, cy in [(13.5,13.5),(196.5,13.5),(13.5,283.5),(196.5,283.5)]:
        d.rectangle([(cx-3.5)*S,(cy-3.5)*S,(cx+3.5)*S,(cy+3.5)*S], fill=0)
    d.rectangle([22.5*S, 11.5*S, 26.5*S, 15.5*S], fill=0)            # 上下判定マーク
    ell = lambda x, y, f: d.ellipse([(x-2.5)*S,(y-1.7)*S,(x+2.5)*S,(y+1.7)*S], outline=100, width=2, fill=f)
    bp = lambda q, c: (COLS[q//per_col][1] + c*DX, Y0 + (q % per_col)*DY)
    answers = []
    for q in range(nq):
        a = q % 10 if q % 7 != 6 else -1                              # 7問ごとに無回答
        if q == 5: a = -2                                              # 複数マーク
        answers.append(a)
        for c in range(10):
            x, y = bp(q, c)
            fill = 90 if (a == c or (a == -2 and c in (1, 9))) else None
            ell(x, y, fill)
    ident = [3, 2, 7]
    for r, y in enumerate(ID_ROWS):
        for dg in range(10): ell(72 + dg*10, y, 90 if ident[r] == dg else None)
    for ex in [62, 121, 148]:                                          # 塗りつぶし例（読まない）
        d.ellipse([(ex-3.5)*S,(68-2.5)*S,(ex+3.5)*S,(68+2.5)*S], fill=40)
    for j in range(n_written):                                         # 記述欄と手書き風の線
        top = Y0 - DY/2 + (per_col + j*w_size)*DY + 0.8
        d.rectangle([20*S, top*S, 190*S, (top + w_size*DY - 1.6)*S], outline=136, width=2)
        for k in range(12): d.line([(30+k*10)*S,(top+5)*S,(36+k*10)*S,(top+9)*S], fill=30, width=5)
    im = im.rotate(rot, fillcolor=250, resample=Image.BILINEAR)
    if flip: im = im.rotate(180)
    im = im.resize((1400, int(1400*H/W)))
    with open(os.path.join(OUT, name + '.raw'), 'wb') as f:
        f.write(bytes([im.width//256, im.width%256, im.height//256, im.height%256]) + im.tobytes())
    return {'written': n_written, 'size': w_size, 'id': ident, 'answers': answers, 'rotated': flip}

cases = {
    'plain_tilt':       make('plain_tilt', 0, 3, 1.5, False),
    'plain_upsidedown': make('plain_upsidedown', 0, 3, -1.0, True),
    'written3':         make('written3', 3, 3, 1.0, False),
    'written2_tall':    make('written2_tall', 2, 5, -1.2, True),
}
json.dump(cases, open(os.path.join(OUT, 'expected.json'), 'w'), ensure_ascii=False, indent=1)
print('作成しました:', ', '.join(cases))
