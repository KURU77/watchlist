# -*- coding: utf-8 -*-
"""視聴リスト 使い方ガイド（実利用者向け PDF）

章ごとに「これ以上は分割しない」かたまりを作り、ページの切れ目が
かならず章の切れ目に来るようにしている。
そのうえで、下の DENSITY の数値で行間や余白を詰めて、
各ページの下に残る空白を小さくしている。

    py -3 tools/make_manual.py            通常どおり PDF を作る
    py -3 tools/make_manual.py --measure  章ごとの高さとページの空きを表示する
"""
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

FONTS = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("JP",  os.path.join(FONTS, "meiryo.ttc"),  subfontIndex=0))
pdfmetrics.registerFont(TTFont("JPB", os.path.join(FONTS, "meiryob.ttc"), subfontIndex=0))
pdfmetrics.registerFontFamily("JP", normal="JP", bold="JPB", italic="JP", boldItalic="JPB")

# ---------- 詰め具合の調整箇所 ----------
BODY_SIZE, BODY_LEAD = 8.7, 13.3
CELL_SIZE, CELL_LEAD = 8.3, 12.7
H2_SIZE = 10.6
H2_BEFORE, H2_AFTER = 2.5, 1.5        # 見出しの前後の余白(mm)
PARA_AFTER = 1.25                     # 段落のあとの余白(mm)
TBL_PAD_V = 1.0                       # 表のセルの上下余白(mm)
TBL_AFTER = 1.7                       # 表のあとの余白(mm)
BOX_PAD_V = 0.9
BOX_AFTER = 1.6
MARGIN = 12.5 * mm
TOP_MARGIN, BOT_MARGIN = 11 * mm, 13 * mm

INK    = colors.HexColor("#1c2230")
MUTED  = colors.HexColor("#5f6880")
ACC    = colors.HexColor("#2f52c0")
ACCBG  = colors.HexColor("#eef2fd")
LINE   = colors.HexColor("#dde3f0")
HEADBG = colors.HexColor("#f3f6fc")
KEYBG  = colors.HexColor("#fafbff")
WARNBG = colors.HexColor("#fdf4ef")
WARNLN = colors.HexColor("#d4551f")
TIPBG  = colors.HexColor("#f1faf6")
TIPLN  = colors.HexColor("#0f9b68")
NOTEBG = colors.HexColor("#f7f9fc")
NOTELN = colors.HexColor("#7c8bb5")

PW, PH = A4
CW = PW - MARGIN * 2
FRAME_H = PH - TOP_MARGIN - BOT_MARGIN

body = ParagraphStyle("body", fontName="JP", fontSize=BODY_SIZE, leading=BODY_LEAD,
                      textColor=INK, spaceAfter=PARA_AFTER * mm)
lead = ParagraphStyle("lead", parent=body, fontSize=8.9, leading=14.2, textColor=MUTED)
h1 = ParagraphStyle("h1", fontName="JPB", fontSize=18, leading=23, textColor=INK)
h2t = ParagraphStyle("h2t", fontName="JPB", fontSize=H2_SIZE, leading=H2_SIZE * 1.45, textColor=ACC)
h3 = ParagraphStyle("h3", fontName="JPB", fontSize=9.6, leading=14.4,
                    textColor=colors.HexColor("#26305c"),
                    spaceBefore=2.6 * mm, spaceAfter=1.0 * mm)
cell = ParagraphStyle("cell", fontName="JP", fontSize=CELL_SIZE, leading=CELL_LEAD, textColor=INK)
cellk = ParagraphStyle("cellk", parent=cell, fontName="JPB",
                       textColor=colors.HexColor("#26305c"))
boxs = ParagraphStyle("boxs", fontName="JP", fontSize=CELL_SIZE, leading=CELL_LEAD + 0.3,
                      textColor=INK)
boxt = ParagraphStyle("boxt", parent=boxs, fontName="JPB")
urls = ParagraphStyle("urls", fontName="JPB", fontSize=10.2, leading=15, textColor=ACC)

# 章を組み立てるための入れ物
sections = []          # [(見出し, [flowable, ...]), ...]
_cur = None


def new_section(name):
    global _cur
    _cur = []
    sections.append((name, _cur))


def add(f):
    _cur.append(f)


def P(t, st=body):
    return Paragraph(t, st)


def H2(text):
    t = Table([[P(text, h2t)]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCBG),
        ("LINEBEFORE", (0, 0), (0, -1), 1.6, ACC),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
    ]))
    add(t)
    add(Spacer(1, H2_AFTER * mm))


def TBL(rows, header=None, key_w=34 * mm):
    data = []
    if header:
        data.append([P(header[0], cellk), P(header[1], cellk)])
    for k, v in rows:
        data.append([P(k, cellk), P(v, cell)])
    t = Table(data, colWidths=[key_w, CW - key_w])
    st = [
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), KEYBG),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), TBL_PAD_V * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), TBL_PAD_V * mm),
    ]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HEADBG))
    t.setStyle(TableStyle(st))
    add(t)
    add(Spacer(1, TBL_AFTER * mm))


def BOX(title, text, kind="note"):
    bg, ln = {"note": (NOTEBG, NOTELN), "warn": (WARNBG, WARNLN), "tip": (TIPBG, TIPLN)}[kind]
    inner = []
    if title:
        inner.append([P(title, boxt)])
    inner.append([P(text, boxs)])
    t = Table(inner, colWidths=[CW - 6 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 1.4, ln),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), BOX_PAD_V * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), BOX_PAD_V * mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    add(Spacer(1, 0.8 * mm))
    add(t)
    add(Spacer(1, BOX_AFTER * mm))


def STEPS(items):
    data = []
    for i, s in enumerate(items, 1):
        num = Table([[P(str(i), ParagraphStyle("n", fontName="JPB", fontSize=8.4,
                                               leading=10.6, textColor=colors.white,
                                               alignment=1))]],
                    colWidths=[5.2 * mm], rowHeights=[5.2 * mm])
        num.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), ACC),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ROUNDEDCORNERS", [2.6 * mm] * 4),
        ]))
        data.append([num, P(s, cell)])
    t = Table(data, colWidths=[7.4 * mm, CW - 7.4 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0.7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.7 * mm),
    ]))
    add(t)
    add(Spacer(1, 2.2 * mm))


def BULLETS(items):
    data = [[P("・", cell), P(s, cell)] for s in items]
    t = Table(data, colWidths=[4.2 * mm, CW - 4.2 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0.4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.4 * mm),
    ]))
    add(t)
    add(Spacer(1, 2.2 * mm))


# ==================== 表紙 ====================
new_section("表紙")
cover = Table([
    [P("視聴リスト　使い方ガイド", h1)],
    [P("見たいアニメ・映画・地上波の番組を、忘れないように書きとめておくためのアプリです。<br/>"
       "「もう見た」「放送日が決まっている」「いつか見たい」を分けて置いておけます。", lead)],
    [P("https://kuru77.github.io/watchlist/", urls)],
    [P("インストールは不要です。スマホ・パソコンどちらのブラウザでも、上の住所を開けばすぐ使えます。",
       ParagraphStyle("cn", parent=lead, fontSize=8.3, leading=12.6))],
], colWidths=[CW])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafbff")),
    ("BOX", (0, 0), (-1, -1), 0.6, LINE),
    ("LINEABOVE", (0, 0), (-1, 0), 2.6, ACC),
    ("LEFTPADDING", (0, 0), (-1, -1), 5.4 * mm),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5.4 * mm),
    ("TOPPADDING", (0, 0), (0, 0), 4.2 * mm),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3 * mm),
    ("TOPPADDING", (0, 1), (-1, -1), 1.0 * mm),
    ("BOTTOMPADDING", (0, -1), (-1, -1), 4.2 * mm),
]))
add(cover)
add(Spacer(1, H2_BEFORE * mm))

# ==================== 1 ====================
new_section("1 画面の見かた")
H2("1.　画面の見かた")
add(P("画面はうえから「配信サービスの設定」「データの取り込み」「入力フォーム」"
      "「タブ」「作品の一覧」の順に並んでいます。作品はつぎの5つのタブに分かれて表示されます。"))
TBL([
    ("★ お気に入り", "★をつけた作品。<b>見た作品でもお気に入りに入れられます</b>"
                  "（下の3つとは別のしくみで、重ねて使えます）。"),
    ("放送予定", "放送日・公開日が決まっている作品。日付が近い順に並び、"
              "「今日！」「明日」「あと5日」が自動で出ます。"),
    ("いつか見たい", "日付は未定だけれど、いつか見たい作品。"),
    ("見た", "見終わった作品。見た日と5段階の評価をつけられます。"),
    ("すべて", "ぜんぶまとめて表示します。"),
], header=("タブ", "入っているもの"), key_w=29 * mm)
BOX("ひとつの作品が入るのは「放送予定・いつか見たい・見た」のどれか1つだけです",
    "お気に入りの★はそれとは別あつかいなので、「見た」に入れたまま★をつけておけます。", "tip")

# ==================== 2 ====================
new_section("2 作品を追加する")
H2("2.　作品を追加する")
add(P("<b>方法A　タイトルを検索して取り込む（おすすめ）</b>", h3))
STEPS([
    "いちばん上の「データを取り込む」に作品名を入れて、［取り込む］を押します。",
    "候補が出てくるので、目的の作品をおします。",
    "下のフォームに、放送日や話数、公式サイトなどが自動で入ります。",
    "中身をたしかめて、必要なら直してから［追加する］を押します。",
])
add(P("検索先は「両方から検索」のままで大丈夫です。うまく出ないときだけ"
      "「アニメ」「映画・番組」に切り替えてみてください。"))
add(P("<b>方法B　URL を貼り付けて取り込む</b>", h3))
add(P("作品ページの住所をコピーして同じ欄に貼ると、検索せずに直接読み込めます。"))
TBL([
    ("AniList", "https://anilist.co/anime/154587"),
    ("MyAnimeList", "https://myanimelist.net/anime/52991"),
    ("Wikipedia（日本語版）", "https://ja.wikipedia.org/wiki/君の名は。"),
    ("Wikidata", "https://www.wikidata.org/wiki/Q21697406"),
], header=("貼れるもの", "例"), key_w=38 * mm)
BOX("これ以外の URL は貼っても読み込めません",
    "Filmarks や Amazon、YouTube、作品の公式サイトなどの住所には対応していません。"
    "その場合はふつうに作品名で検索してください。", "warn")
add(P("<b>方法C　自分で入力する</b>", h3))
add(P("取り込みを使わず、フォームに直接タイトルを書いて［追加する］を押すだけでも登録できます。"
      "思いついたものをとりあえず入れておきたいときは、これがいちばん早いです。"))

# ==================== 3 ====================
new_section("3 種類ごとに記録できること")
H2("3.　種類ごとに記録できること")
add(P("「種類」を選ぶと、その種類に合った入力欄に切り替わります。"))
TBL([
    ("映画", "<b>公開日</b>を記録できます。取り込むと日本での公開日が入ります。"
           "上映時間や監督はメモ欄に自動で入ります。"),
    ("アニメ", "<b>全何期あって、何期まで見たか</b>を記録できます。話数も入れられます。"
            "カードには進みぐあいのバーが出て、全部見終わると「制覇」の表示に変わります。"),
    ("地上波", "放送日・放送開始時刻・放送局を記録できます。"),
], header=("種類", "記録できること"), key_w=24 * mm)
add(P("<b>アニメの「期」の使いかた</b>", h3))
add(P("取り込むと「全何期」は自動で入りますが、<b>何期まで見たかはご自身で入れてください</b>。"
      "あとから1期ずつ進めるときは、作品カードの［+1期］を押すだけです。"))
BOX("全何期の数がずれることがあります",
    "分割クール（1期が前半・後半に分かれている作品など）は、多めに数えられることがあります。"
    "実際とちがっていたら［編集］から「全何期」を書き直してください。", "note")

# ==================== 4 ====================
new_section("4 リストのあいだで動かす")
H2("4.　リストのあいだで動かす")
add(P("作品カードの右がわにあるボタンで、あとから自由に動かせます。"))
TBL([
    ("見た", "「見た」に移します。その日の日付が見た日として自動で入ります。"),
    ("また見たい", "「見た」の作品を「いつか見たい」に戻します。"),
    ("放送予定へ", "「いつか見たい」の作品を「放送予定」に移します。日付は［編集］から入れてください。"),
    ("★ / ☆", "カード左はしの星。押すたびにお気に入りの入り切りが変わります。"),
    ("編集", "その作品の内容をフォームに呼び出して直します。"),
    ("削除", "作品を消します（確認が出ます）。"),
], header=("ボタン", "はたらき"), key_w=29 * mm)
BOX("放送日が過ぎた作品は自動でまとめられます",
    "「放送予定」タブの下のほうに「公開・放送済み」としてまとまります。"
    "見終わったものから［見た］を押して片づけていくと、きれいに保てます。", "tip")

# ==================== 5 ====================
new_section("5 配信サービスのボタン")
H2("5.　配信サービスのボタン")
add(P("作品カードから、その作品を配信しているサービスへ直接とべます。"
      "画面のいちばん上にある「使っている配信サービスを選ぶ」をひらいて、"
      "<b>契約しているサービスだけを選んでおいてください</b>。"
      "対応しているのは　Prime Video ／ Netflix ／ Hulu ／ Disney+ ／ U-NEXT ／ TVer ／ NHK+　の7つです。"))
TBL([
    ("▶ が付いた<br/>サービス名",
     "その作品の視聴ページが分かっています。押すとその作品のページが直接ひらきます。"),
    ("虫めがねが付いた<br/>サービス名",
     "視聴ページまでは分からなかったので、押すとそのサービスの中で作品名を検索します。"),
], header=("ボタン", "意味"), key_w=34 * mm)
add(P("ひとつも選ばなかったときは、取り込みで分かった配信先だけが最大3件だけ表示されます。"))
BOX("配信されているかどうかまでは分かりません",
    "ボタンはあくまで「そのサービスで探しに行く」ためのものです。実際に配信中かどうかは、"
    "ひらいた先でおたしかめください。なお Hulu はつねに検索になります。", "note")

# ==================== 6 ====================
new_section("6 さがす・しぼりこむ")
H2("6.　さがす・しぼりこむ")
BULLETS([
    "タブの下の検索欄に文字を入れると、<b>タイトル・放送局・メモ</b>から探せます。",
    "となりの「すべての種類」を切り替えると、アニメだけ・映画だけを表示できます。",
    "どちらも今ひらいているタブの中だけではたらきます。全部から探したいときは「すべて」タブでどうぞ。",
])

# ==================== 7 ====================
new_section("7 データの保存とバックアップ")
H2("7.　データの保存とバックアップ")
add(P("登録した内容は、<b>お使いのブラウザの中だけに保存されます</b>。"
      "どこかのサーバーに送られることはないので、ほかの人に見られる心配はありません。"
      "そのかわり、つぎの点にご注意ください。"))
TBL([
    ("端末ごとに別", "スマホで入れた作品はパソコンには出てきません。逆も同じです。"),
    ("ブラウザごとに別", "Chrome で入れた作品は Safari には出てきません。いつも同じブラウザをお使いください。"),
    ("消えることがある", "ブラウザの閲覧データ（キャッシュや Cookie）を消すと、いっしょに消えることがあります。"),
], key_w=32 * mm)
BOX("ときどきバックアップをとってください",
    "画面右上の［書き出し］を押すとファイルが1つ保存されます。これがバックアップです。"
    "戻すときや、べつの端末に移すときは、その端末で［読み込み］を押して、"
    "保存しておいたファイルをえらんでください（今あるリストに<b>追加</b>されます）。", "warn")

# ==================== 8 ====================
new_section("8 困ったときは")
H2("8.　困ったときは")
TBL([
    ("検索しても<br/>出てこない",
     "正式なタイトルで試してください（「劇場版」「第2期」などをふくめた形）。"
     "英語の題名や、ひらがな・カタカナを変えると見つかることもあります。"
     "どうしても出てこないときは、方法Cの手入力でも困りません。"),
    ("取り込みに<br/>失敗する",
     "インターネットにつながっているかおたしかめください。取り込みは外部のデータを読みに行くため、"
     "通信できないと使えません（それ以外の機能はふつうに使えます）。"),
    ("画面が<br/>新しくならない",
     "ブラウザが古い画面をおぼえていることがあります。パソコンなら <b>Ctrl</b> と <b>F5</b> を同時に押し、"
     "スマホなら画面を下に引っぱって更新してください。"),
    ("日付や期の数が<br/>まちがっている",
     "取り込んだ内容はあくまで下書きです。［編集］からご自身で直してください。"),
    ("作品が全部<br/>消えてしまった",
     "ブラウザの閲覧データを消したか、べつの端末・べつのブラウザでひらいている可能性があります。"
     "バックアップのファイルがあれば［読み込み］から戻せます。"),
], header=("こまりごと", "対処"), key_w=30 * mm)
BOX("ホーム画面に置いておくと便利です",
    "スマホのブラウザのメニューから「ホーム画面に追加」をえらんでおくと、"
    "ふつうのアプリと同じように1タップでひらけるようになります。"
    "アドレスバーのない、ふつうのアプリのような画面で使えます。", "tip")


# ==================== 組み立て ====================
def section_height(flowables):
    """段落スタイルの前後の空き（spaceBefore / spaceAfter）も数える。
    連続する空きは大きいほうだけが効くので、reportlab と同じ数え方にする。"""
    h = 0.0
    prev_after = 0.0
    for f in flowables:
        try:
            before = f.getSpaceBefore()
        except Exception:
            before = 0.0
        h += max(prev_after, before)
        try:
            h += f.wrap(CW, FRAME_H)[1]
        except Exception:
            pass
        try:
            prev_after = f.getSpaceAfter()
        except Exception:
            prev_after = 0.0
    return h + prev_after


def build_story():
    """章ごとに分割不能のかたまりにして並べる"""
    out = []
    for i, (name, fl) in enumerate(sections):
        group = list(fl)
        if i > 0:
            group.insert(0, Spacer(1, H2_BEFORE * mm))
        out.append(KeepTogether(group))
    return out


def measure():
    print("枠の高さ: %.1fmm" % (FRAME_H / mm))
    used, page, pages = 0.0, 1, []
    for i, (name, fl) in enumerate(sections):
        h = section_height(fl) + (H2_BEFORE * mm if i > 0 else 0)
        if used + h > FRAME_H + 0.5:
            pages.append((page, used))
            page += 1
            used = 0.0
        used += h
        print("  p%d  %-28s %6.1fmm" % (page, name, h / mm))
    pages.append((page, used))
    print("---")
    for p, u in pages:
        print("  ページ%d  使用 %.1fmm  空き %.1fmm" % (p, u / mm, (FRAME_H - u) / mm))


def on_page(canv, doc):
    canv.saveState()
    canv.setFont("JP", 7.4)
    canv.setFillColor(colors.HexColor("#98a0b8"))
    canv.drawCentredString(PW / 2, 8 * mm,
                           "視聴リスト 使い方ガイド　—　https://kuru77.github.io/watchlist/　—　%d" % doc.page)
    canv.setStrokeColor(colors.HexColor("#e6ebf5"))
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 11.5 * mm, PW - MARGIN, 11.5 * mm)
    canv.restoreState()


def main():
    if "--measure" in sys.argv:
        measure()
        return
    _default = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "視聴リスト_使い方ガイド.pdf")
    out_path = os.environ.get("OUT_PDF") or _default
    doc = BaseDocTemplate(out_path, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=TOP_MARGIN, bottomMargin=BOT_MARGIN,
                          title="視聴リスト 使い方ガイド", author="視聴リスト",
                          subject="アニメ・映画・地上波の視聴リスト アプリの使い方")
    frame = Frame(MARGIN, BOT_MARGIN, CW, FRAME_H, id="body",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
    doc.build(build_story())
    print("OK:", out_path)


if __name__ == "__main__":
    main()
