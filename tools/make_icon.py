# -*- coding: utf-8 -*-
"""視聴リストのアプリアイコンを作る。

512x512 の座標で図形を定義し、同じ数値から
  - icon.svg（ファビコン・画面上部のロゴ用）
  - apple-touch-icon.png / icon-192.png / icon-512.png
  - icon-maskable-512.png（Android の丸型切り抜き用に内容を小さめに配置）
を書き出す。

    py -3 tools/make_icon.py
"""
import math
import os

from PIL import Image, ImageDraw

S = 512                      # 基準の座標系
SS = 4                       # 縁をなめらかにするための拡大率
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- 配色（アプリ本体の配色に合わせる） ----
G1 = (0x4b, 0x6f, 0xf0)      # 左上
G2 = (0x3b, 0x62, 0xd8)      # 中間
G3 = (0x6a, 0x45, 0xe0)      # 右下
SCREEN_TOP = (0xff, 0xff, 0xff)
SCREEN_BOT = (0xe8, 0xee, 0xfc)
STAR_TOP = (0xff, 0xd7, 0x6a)
STAR_BOT = (0xf5, 0xa6, 0x23)
PLAY = (0x3b, 0x62, 0xd8)

# ---- 図形の位置（512 基準） ----
TILE_R = 114                 # 角丸
SCREEN = (78, 86, 404, 296)   # 画面 x0,y0,x1,y1
SCREEN_R = 32
NECK = (222, 292, 262, 328)   # 支柱
NECK_R = 10
BASE = (176, 324, 308, 352)   # 台座
BASE_R = 14
PLAY_C = (241, 191)           # 再生マークの中心
PLAY_W, PLAY_H = 88, 96
PLAY_ROUND = 22               # 角の丸み（線幅で表現）
STAR_C = (392, 392)
STAR_R = 74
STAR_INNER = STAR_R * 0.395
STAR_GAP = 13                 # 星のまわりに空ける余白


def star_points(cx, cy, r_out, r_in, n=5, rot=-90.0):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * (360.0 / (n * 2)))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def play_points(cx, cy, w, h):
    """右向きの三角形（重心が中心に来るよう少し右に寄せる）"""
    return [(cx - w * 0.42, cy - h / 2.0),
            (cx + w * 0.58, cy),
            (cx - w * 0.42, cy + h / 2.0)]


def lin_gradient(size, c0, c1, diagonal=True):
    """左上→右下（または上→下）の線形グラデーション画像"""
    w = h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = ((x + y) / (w + h - 2.0)) if diagonal else (y / (h - 1.0))
            px[x, y] = (int(c0[0] + (c1[0] - c0[0]) * t),
                        int(c0[1] + (c1[1] - c0[1]) * t),
                        int(c0[2] + (c1[2] - c0[2]) * t))
    return img


def tile_gradient(size):
    """3色の対角グラデーション"""
    w = h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x + y) / (w + h - 2.0)
            if t < 0.55:
                u = t / 0.55
                a, b = G1, G2
            else:
                u = (t - 0.55) / 0.45
                a, b = G2, G3
            px[x, y] = (int(a[0] + (b[0] - a[0]) * u),
                        int(a[1] + (b[1] - a[1]) * u),
                        int(a[2] + (b[2] - a[2]) * u))
    return img


def sc(v, k):
    """512 基準の値を実際の描画サイズへ"""
    return v * k


def render(px_size, content_scale=1.0, rounded=True, parts=None):
    """アイコンを1枚描く。

    content_scale<1 で内容を小さくする（maskable 用）。
    parts に 'fg' を渡すと絵柄だけ（背景は透明）、'bg' を渡すと下地だけを返す。
    Android のアダプティブアイコン（前景と背景が別レイヤー）で使う。
    """
    n = px_size * SS
    k = n / float(S)

    base = tile_gradient(n).convert("RGBA")

    # 角丸マスク
    if rounded:
        mask = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, n - 1, n - 1],
                                               radius=sc(TILE_R, k), fill=255)
        tile = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        tile.paste(base, (0, 0), mask)
    else:
        tile = base

    layer = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cs = content_scale
    ctr = S / 2.0

    def T(x, y):
        """内容の拡大縮小（中心基準）と実サイズ変換"""
        return (sc(ctr + (x - ctr) * cs, k), sc(ctr + (y - ctr) * cs, k))

    def rect(box, radius, fill):
        p0 = T(box[0], box[1])
        p1 = T(box[2], box[3])
        d.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]],
                            radius=radius * cs * k, fill=fill)

    # テレビの支柱と台座
    rect(NECK, NECK_R, (255, 255, 255, 235))
    rect(BASE, BASE_R, (255, 255, 255, 235))

    # 画面（上下のグラデーション）
    scr = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    sm = Image.new("L", (n, n), 0)
    p0, p1 = T(SCREEN[0], SCREEN[1]), T(SCREEN[2], SCREEN[3])
    ImageDraw.Draw(sm).rounded_rectangle([p0[0], p0[1], p1[0], p1[1]],
                                         radius=SCREEN_R * cs * k, fill=255)
    scr.paste(lin_gradient(n, SCREEN_TOP, SCREEN_BOT, diagonal=False).convert("RGBA"),
              (0, 0), sm)
    layer = Image.alpha_composite(layer, scr)
    d = ImageDraw.Draw(layer)

    # 再生マーク（角を丸めるため、塗り＋太線＋頂点の円）
    tri = [T(x, y) for (x, y) in play_points(PLAY_C[0], PLAY_C[1], PLAY_W, PLAY_H)]
    lw = max(1, int(PLAY_ROUND * cs * k))
    d.polygon(tri, fill=PLAY + (255,))
    for i in range(3):
        d.line([tri[i], tri[(i + 1) % 3]], fill=PLAY + (255,), width=lw)
    for (x, y) in tri:
        r = lw / 2.0
        d.ellipse([x - r, y - r, x + r, y + r], fill=PLAY + (255,))

    # 星のまわりの余白（下地のグラデーションで抜く）
    gap = Image.new("L", (n, n), 0)
    gc = T(STAR_C[0], STAR_C[1])
    gr = (STAR_R + STAR_GAP) * cs * k
    ImageDraw.Draw(gap).ellipse([gc[0] - gr, gc[1] - gr, gc[0] + gr, gc[1] + gr], fill=255)
    layer.paste((0, 0, 0, 0), (0, 0), gap)

    # 星
    star = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    stm = Image.new("L", (n, n), 0)
    pts = [T(x, y) for (x, y) in
           star_points(STAR_C[0], STAR_C[1], STAR_R, STAR_INNER)]
    ImageDraw.Draw(stm).polygon(pts, fill=255)
    star.paste(lin_gradient(n, STAR_TOP, STAR_BOT, diagonal=False).convert("RGBA"),
               (0, 0), stm)
    layer = Image.alpha_composite(layer, star)

    if parts == "fg":
        img = layer                                   # 絵柄だけ（背景は透明）
    elif parts == "bg":
        img = tile                                    # 下地だけ
    else:
        img = Image.alpha_composite(tile, layer)
    return img.resize((px_size, px_size), Image.LANCZOS)


def fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def write_svg(path):
    star = " ".join("%s,%s" % (fmt(x), fmt(y))
                    for x, y in star_points(STAR_C[0], STAR_C[1], STAR_R, STAR_INNER))
    tri = play_points(PLAY_C[0], PLAY_C[1], PLAY_W, PLAY_H)
    tri_s = " ".join("%s,%s" % (fmt(x), fmt(y)) for x, y in tri)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="視聴リスト">
  <defs>
    <linearGradient id="tile" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="512" y2="512">
      <stop offset="0" stop-color="#4b6ff0"/>
      <stop offset=".55" stop-color="#3b62d8"/>
      <stop offset="1" stop-color="#6a45e0"/>
    </linearGradient>
    <linearGradient id="scr" gradientUnits="userSpaceOnUse" x1="0" y1="{SCREEN[1]}" x2="0" y2="{SCREEN[3]}">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#e8eefc"/>
    </linearGradient>
    <linearGradient id="star" gradientUnits="userSpaceOnUse" x1="0" y1="{fmt(STAR_C[1] - STAR_R)}" x2="0" y2="{fmt(STAR_C[1] + STAR_R)}">
      <stop offset="0" stop-color="#ffd76a"/>
      <stop offset="1" stop-color="#f5a623"/>
    </linearGradient>
    <clipPath id="tileClip"><rect width="512" height="512" rx="{TILE_R}"/></clipPath>
  </defs>
  <g clip-path="url(#tileClip)">
    <rect width="512" height="512" fill="url(#tile)"/>
    <rect x="{NECK[0]}" y="{NECK[1]}" width="{NECK[2]-NECK[0]}" height="{NECK[3]-NECK[1]}" rx="{NECK_R}" fill="#ffffff" opacity=".92"/>
    <rect x="{BASE[0]}" y="{BASE[1]}" width="{BASE[2]-BASE[0]}" height="{BASE[3]-BASE[1]}" rx="{BASE_R}" fill="#ffffff" opacity=".92"/>
    <rect x="{SCREEN[0]}" y="{SCREEN[1]}" width="{SCREEN[2]-SCREEN[0]}" height="{SCREEN[3]-SCREEN[1]}" rx="{SCREEN_R}" fill="url(#scr)"/>
    <polygon points="{tri_s}" fill="#3b62d8" stroke="#3b62d8" stroke-width="{PLAY_ROUND}" stroke-linejoin="round"/>
    <circle cx="{STAR_C[0]}" cy="{STAR_C[1]}" r="{fmt(STAR_R + STAR_GAP)}" fill="url(#tile)"/>
    <polygon points="{star}" fill="url(#star)"/>
  </g>
</svg>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    write_svg(os.path.join(OUT, "icon.svg"))
    jobs = [
        # 名前, ピクセル数, 内容の倍率, 角を丸めるか
        ("apple-touch-icon.png", 180, 1.0, True),
        ("icon-192.png", 192, 1.0, True),
        ("icon-512.png", 512, 1.0, True),
        # maskable は端末側が好きな形に切り抜くので、角は丸めず全面を塗る
        ("icon-maskable-512.png", 512, 0.72, False),
    ]
    for name, size, cs, rounded in jobs:
        img = render(size, content_scale=cs, rounded=rounded)
        p = os.path.join(OUT, name)
        img.save(p, optimize=True)
        print("OK", name, img.size)
    print("OK icon.svg")


if __name__ == "__main__":
    main()
