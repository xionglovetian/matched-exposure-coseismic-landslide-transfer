"""Emit Figure 8 (GNHR) from one shared primitive list."""
import json, math, csv
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

BASE = Path(r"C:\Users\ASUS\Documents\ChatGPT\灾害信息处理\_cloud_e3_20261015")
OUT = Path(r"C:\Users\ASUS\Desktop\五步协议\论文图表_可编辑矢量\Figure8_GNHR")
W, H = 540.0, 396.0
FONT = "Arial"

ARCHS = {"resunet": "ResUNet", "bottleneckliteask": "Bottleneck-LiteASK"}
ARMS = {"cas-multistream": "source-only", "pooled": "pooled"}
SEEDS = [42, 2026, 777]
DOMS = [("source_val", "CAS validation"), ("hokkaido_iburi_tobu", "Hokkaido"),
        ("lombok", "Lombok"), ("palu", "Palu")]
DOM_COL = {"source_val": "#5F6B76", "hokkaido_iburi_tobu": "#B2182B",
           "lombok": "#D88700", "palu": "#2166AC"}
ARM_COL = {"source-only": "#2166AC", "pooled": "#B2182B"}
SHAPE = {"source_val": "square", "hokkaido_iburi_tobu": "circle", "lombok": "triangle", "palu": "diamond"}
RULE, TXT = "#C8D0D7", "#1A1A1A"
T = 4.302652729911275

def load(arch, arm, seed):
    return json.loads((BASE/"e2_analysis"/"out"/f"q2_x3_{arch}_{arm}_seed{seed}.freqcalib.json").read_text(encoding="utf-8"))

rel = {}
for arm in ARMS:
    for dom, _ in DOMS:
        nb = None; ac = ae = an = None
        for arch in ARCHS:
            for seed in SEEDS:
                bins = load(arch, arm, seed)["domains"][dom]["bins_equal_freq"]
                if nb is None:
                    nb = len(bins); ac = [0.0]*nb; ae = [0.0]*nb; an = [0.0]*nb
                for i, b in enumerate(bins):
                    n = b["pixels"]; ac[i] += b["mean_confidence"]*n; ae[i] += b["error_rate"]*n; an[i] += n
        rel[(arm, dom)] = [(1.0-ac[i]/an[i], ae[i]/an[i]) for i in range(nb)]

hc = {}
for arch in ARCHS:
    for arm in ARMS:
        for dom, _ in DOMS:
            v = [load(arch, arm, seed)["domains"][dom]["high_confidence_error_rate"]*100 for seed in SEEDS]
            m = sum(v)/3; sd = math.sqrt(sum((x-m)**2 for x in v)/2); se = sd/math.sqrt(3)
            hc[(arch, arm, dom)] = (m, m-T*se, m+T*se)

P = []
def line(x1,y1,x2,y2,c=RULE,w=0.6,dash=None): P.append(("line",x1,y1,x2,y2,c,w,dash))
def poly(pts,c,w=1.0,dash=None): P.append(("poly",list(pts),c,w,dash))
def mark(x,y,shape,s,c,open_=False,sc=None): P.append(("mark",x,y,shape,s,c,open_,sc))
def text(x,y,s,size=6.0,c=TXT,anchor="start",bold=False): P.append(("text",x,y,s,size,c,anchor,bold))
def rect(x,y,w,h,fill=None,stroke=None,sw=0.6): P.append(("rect",x,y,w,h,fill,stroke,sw))

# ---------- panel geometry ----------
AX = {"a": (78.0, 282.0, 60.0, 176.0), "b": (318.0, 522.0, 60.0, 176.0), "c": (78.0, 522.0, 250.0, 366.0)}

def sx(panel, v, v0, v1):
    l, r, t, b = panel
    return l + (v - v0)/(v1 - v0)*(r - l)
def sy(panel, v, v0, v1):
    l, r, t, b = panel
    return b - (v - v0)/(v1 - v0)*(b - t)

# ---------- panels a and b: reliability ----------
XR, YR = 0.0, 0.52
for key, arm_key, label in (("a","cas-multistream","a"), ("b","pooled","b")):
    p = AX[key]
    l, r, t, b = p
    for v in (0.0,0.1,0.2,0.3,0.4,0.5):
        y = sy(p, v, XR, YR); line(l, y, r, y)
        x = sx(p, v, XR, YR); line(x, t, x, b)
    line(l, b, r, b, TXT, 0.7); line(l, t, l, b, TXT, 0.7)
    line(sx(p,0,XR,YR), sy(p,0,XR,YR), sx(p,0.5,XR,YR), sy(p,0.5,XR,YR), "#8C97A3", 0.7, "dash")
    for v, lab in ((0.0,"0"),(0.1,"0.1"),(0.2,"0.2"),(0.3,"0.3"),(0.4,"0.4"),(0.5,"0.5")):
        text(sx(p,v,XR,YR), b+7.5, lab, 5.6, TXT, "middle")
        text(l-5.0, sy(p,v,XR,YR)+2.0, lab, 5.6, TXT, "end")
    text((l+r)/2, b+17.5, "mean predicted error (1 - confidence)", 6.0, TXT, "middle")
    text(36.0, (t+b)/2 - 3.5, "observed", 6.0, TXT, "middle")
    text(36.0, (t+b)/2 + 5.5, "error rate", 6.0, TXT, "middle")
    text(l-8.0, t-6.0, label, 8.5, TXT, "start", True)
    for dom, _ in DOMS:
        pts = [(sx(p,x,XR,YR), sy(p,y,XR,YR)) for x, y in rel[(arm_key, dom)]]
        col = DOM_COL[dom]
        poly(pts, col, 0.9)
        for (x, y) in pts:
            mark(x, y, SHAPE[dom], 1.7, col)
text(78.0, 208.0, "source-only arm (CAS replay control)", 6.2, TXT, "start")
text(318.0, 208.0, "pooled-source arm", 6.2, TXT, "start")
# shared domain legend centred below the two top panels
lx = 150.0
for dom, name in DOMS:
    mark(lx, 224.0, SHAPE[dom], 2.0, DOM_COL[dom])
    text(lx+5.0, 226.0, name, 5.9, TXT, "start")
    lx += 8.0 + len(name)*3.15 + 12.0

# ---------- panel c: high-confidence error with seed-stratified intervals ----------
pc = AX["c"]; l, r, t, b = pc
YMAX = 16.0
for v in (0,4,8,12,16):
    y = sy(pc, v, 0, YMAX); line(l, y, r, y)
    text(l-5.0, y+2.0, str(v), 5.6, TXT, "end")
line(l, b, r, b, TXT, 0.7); line(l, t, l, b, TXT, 0.7)
text(34.0, (t+b)/2 - 3.5, "high-confidence", 5.8, TXT, "middle")
text(34.0, (t+b)/2 + 5.5, "error (%)", 5.8, TXT, "middle")
text(l-8.0, t-6.0, "c", 8.5, TXT, "start", True)
centres, xs = [], []
step = (r - l)/len(DOMS)
for i, (dom, name) in enumerate(DOMS):
    cx = l + step*(i + 0.5); centres.append(cx)
    text(cx, b+17.5, name, 6.0, TXT, "middle")
    for j, arm_key in enumerate(("cas-multistream", "pooled")):
        armlab = ARMS[arm_key]; xoff = (-step*0.13) if j == 0 else (step*0.13)
        for k, (arch, shape) in enumerate((("resunet","circle"), ("bottleneckliteask","square"))):
            m, lo, hi = hc[(arch, arm_key, dom)]
            x = cx + xoff + (-step*0.055 if k == 0 else step*0.055)
            col = ARM_COL[armlab]
            y0, y1 = sy(pc, hi, 0, YMAX), sy(pc, lo, 0, YMAX)
            line(x, y0, x, y1, col, 0.6)
            for yy in (y0, y1):
                line(x-2.0, yy, x+2.0, yy, col, 0.6)
            mark(x, sy(pc, m, 0, YMAX), shape, 2.1, col, open_=(j == 1))
            xs.append(x)
# panel c legend
legx = 88.0
mark(legx, 264.0, "circle", 1.9, ARM_COL["source-only"]); text(legx+5.0, 266.0, "source-only arm", 5.9, TXT)
mark(legx+92.0, 264.0, "circle", 1.9, ARM_COL["pooled"], open_=True); text(legx+97.0, 266.0, "pooled-source arm", 5.9, TXT)
text(legx, 278.0, "circle = ResUNet; square = Bottleneck-LiteASK", 5.9, TXT)

print("primitives:", len(P))

# ---------- SVG ----------
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">',
       f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>']
for pr in P:
    if pr[0] == "line":
        _, x1,y1,x2,y2,c,w,dash = pr
        d = f' stroke-dasharray="{4*w+2:.2f},{3*w+1.5:.2f}"' if dash else ""
        svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}"{d}/>')
    elif pr[0] == "poly":
        _, pts,c,w,dash = pr
        d = f' stroke-dasharray="{4*w+2:.2f},{3*w+1.5:.2f}"' if dash else ""
        pts_s = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        svg.append(f'<polyline points="{pts_s}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"{d}/>')
    elif pr[0] == "mark":
        _, x,y,shape,s,c,open_,sc = pr
        fill = "#FFFFFF" if open_ else c
        sw = 0.6 if open_ else 0.0
        if shape == "circle":
            svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{s:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
        elif shape == "square":
            svg.append(f'<rect x="{x-s:.2f}" y="{y-s:.2f}" width="{2*s:.2f}" height="{2*s:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
        elif shape == "triangle":
            svg.append(f'<polygon points="{x:.2f},{y-s:.2f} {x-s:.2f},{y+s:.2f} {x+s:.2f},{y+s:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
        elif shape == "diamond":
            svg.append(f'<polygon points="{x:.2f},{y-s:.2f} {x+s:.2f},{y:.2f} {x:.2f},{y+s:.2f} {x-s:.2f},{y:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
    elif pr[0] == "text":
        _, x,y,s,size,c,anchor,bold = pr
        b = ' font-weight="bold"' if bold else ""
        svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}, Helvetica, sans-serif" font-size="{size}" fill="{c}" text-anchor="{anchor}"{b}>{esc(s)}</text>')
    elif pr[0] == "rect":
        _, x,y,w,h,fill,stroke,sw = pr
        svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
svg.append("</svg>")
svg_txt = "\n".join(svg)
(OUT/"Figure 8.svg").write_text(svg_txt, encoding="utf-8")
print("svg text elements:", svg_txt.count("<text"), "| polylines:", svg_txt.count("<polyline"), "| lines:", svg_txt.count("<line"))

# ---------- PPTX ----------
prs = Presentation()
prs.slide_width = Pt(W); prs.slide_height = Pt(H)
slide = prs.slides.add_slide(prs.slide_layouts[6])
sh = slide.shapes
bg = sh.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Pt(W), Pt(H))
bg.fill.solid(); bg.fill.fore_color.rgb = RGBColor.from_string("FFFFFF"); bg.line.fill.background(); bg.shadow.inherit = False
def emu(v): return Emu(int(round(v*12700)))
n_shapes = 1
for pr in P:
    if pr[0] == "line":
        _, x1,y1,x2,y2,c,w,dash = pr
        cn = sh.add_connector(MSO_CONNECTOR.STRAIGHT, emu(x1), emu(y1), emu(x2), emu(y2))
        cn.line.color.rgb = RGBColor.from_string(c.lstrip("#")); cn.line.width = Pt(w)
        if dash: cn.line.dash_style = 4  # MSO_LINE_DASH_STYLE.DASH
        n_shapes += 1
    elif pr[0] == "poly":
        _, pts,c,w,dash = pr
        fb = sh.build_freeform(emu(pts[0][0]), emu(pts[0][1]), scale=1)
        fb.add_line_segments([(emu(x), emu(y)) for x, y in pts[1:]], close=False)
        sp = fb.convert_to_shape()
        sp.fill.background(); sp.line.color.rgb = RGBColor.from_string(c.lstrip("#")); sp.line.width = Pt(w)
        if dash: sp.line.dash_style = 4
        sp.shadow.inherit = False
        n_shapes += 1
    elif pr[0] == "mark":
        _, x,y,shape,s,c,open_,sc = pr
        st = {"circle": MSO_SHAPE.OVAL, "square": MSO_SHAPE.RECTANGLE, "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE, "diamond": MSO_SHAPE.DIAMOND}[shape]
        sp = sh.add_shape(st, emu(x-s), emu(y-s), emu(2*s), emu(2*s))
        if open_:
            sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
            sp.line.color.rgb = RGBColor.from_string(c.lstrip("#")); sp.line.width = Pt(0.6)
        else:
            sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string(c.lstrip("#")); sp.line.fill.background()
        sp.shadow.inherit = False
        n_shapes += 1
    elif pr[0] == "text":
        _, x,y,s,size,c,anchor,bold = pr
        width = max(20.0, len(s)*size*0.62 + 8.0); hh = size*1.6
        left = x - (width/2 if anchor == "middle" else (width if anchor == "end" else 0))
        tb = sh.add_textbox(emu(left), emu(y - hh*0.72), emu(width), emu(hh))
        tf = tb.text_frame; tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        para = tf.paragraphs[0]
        para.alignment = {"middle": PP_ALIGN.CENTER, "end": PP_ALIGN.RIGHT}.get(anchor, PP_ALIGN.LEFT)
        run = para.add_run(); run.text = s
        run.font.size = Pt(size); run.font.name = FONT; run.font.bold = bool(bold)
        run.font.color.rgb = RGBColor.from_string(c.lstrip("#"))
        n_shapes += 1
prs.save(str(OUT/"Figure 8.pptx"))
print("pptx shapes:", n_shapes)
