#!/usr/bin/env python3
"""THE DAILY PICTURE - news-image-20261122
Stdlib-only deterministic PNG front page for Sunday 22 November 2026.
"""
import os, struct, zlib

W, H = 1024, 768

# ---------- PNG encoder ----------
def png_bytes(w, h, rgb):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
    raw = b""
    stride = w * 3
    for y in range(h):
        raw += b"\x00" + rgb[y*stride:(y+1)*stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

# ---------- Canvas ----------
class Canvas:
    def __init__(self, w, h, bg=(255,255,255)):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w*h))
    def px(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y*self.w + x)*3
            self.buf[i:i+3] = bytes(col)
    def rect(self, x, y, w, h, col):
        for yy in range(max(0,y), min(self.h, y+h)):
            for xx in range(max(0,x), min(self.w, x+w)):
                self.px(xx, yy, col)
    def hline(self, x, y, w, col, t=1):
        self.rect(x, y, w, t, col)
    def vline(self, x, y, h, col, t=1):
        self.rect(x, y, t, h, col)
    def line(self, x0, y0, x1, y1, col, t=1):
        dx, dy = x1-x0, y1-y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps+1):
            x = int(x0 + dx*i/steps); y = int(y0 + dy*i/steps)
            self.rect(x, y, t, t, col)
    def tri(self, x0,y0,x1,y1,x2,y2,col):
        minx, maxx = min(x0,x1,x2), max(x0,x1,x2)
        miny, maxy = min(y0,y1,y2), max(y0,y1,y2)
        def sign(ax,ay,bx,by,cx,cy): return (ax-cx)*(by-cy)-(bx-cx)*(ay-cy)
        for y in range(miny, maxy+1):
            for x in range(minx, maxx+1):
                d1=sign(x,y,x0,y0,x1,y1); d2=sign(x,y,x1,y1,x2,y2); d3=sign(x,y,x2,y2,x0,y0)
                if (d1>=0 and d2>=0 and d3>=0) or (d1<=0 and d2<=0 and d3<=0):
                    self.px(x,y,col)
    def circle(self, cx, cy, r, col):
        for y in range(cy-r, cy+r+1):
            for x in range(cx-r, cx+r+1):
                if (x-cx)**2 + (y-cy)**2 <= r*r: self.px(x,y,col)
    def ellipse(self, cx, cy, rx, ry, col):
        for y in range(cy-ry, cy+ry+1):
            for x in range(cx-rx, cx+rx+1):
                if rx and ry and ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1: self.px(x,y,col)

# ---------- 5x7 bitmap font ----------
FONT = {
'A':["01110","10001","10001","11111","10001","10001","10001"],
'B':["11110","10001","10001","11110","10001","10001","11110"],
'C':["01110","10001","10000","10000","10000","10001","01110"],
'D':["11100","10010","10001","10001","10001","10010","11100"],
'E':["11111","10000","10000","11110","10000","10000","11111"],
'F':["11111","10000","10000","11110","10000","10000","10000"],
'G':["01110","10001","10000","10111","10001","10001","01111"],
'H':["10001","10001","10001","11111","10001","10001","10001"],
'I':["01110","00100","00100","00100","00100","00100","01110"],
'J':["00111","00010","00010","00010","00010","10010","01100"],
'K':["10001","10010","10100","11000","10100","10010","10001"],
'L':["10000","10000","10000","10000","10000","10000","11111"],
'M':["10001","11011","10101","10101","10001","10001","10001"],
'N':["10001","10001","11001","10101","10011","10001","10001"],
'O':["01110","10001","10001","10001","10001","10001","01110"],
'P':["11110","10001","10001","11110","10000","10000","10000"],
'Q':["01110","10001","10001","10001","10101","10010","01101"],
'R':["11110","10001","10001","11110","10100","10010","10001"],
'S':["01111","10000","10000","01110","00001","00001","11110"],
'T':["11111","00100","00100","00100","00100","00100","00100"],
'U':["10001","10001","10001","10001","10001","10001","01110"],
'V':["10001","10001","10001","10001","10001","01010","00100"],
'W':["10001","10001","10001","10101","10101","10101","01010"],
'X':["10001","01010","00100","00100","00100","01010","10001"],
'Y':["10001","10001","01010","00100","00100","00100","00100"],
'Z':["11111","00001","00010","00100","01000","10000","11111"],
'0':["01110","10001","10011","10101","11001","10001","01110"],
'1':["00100","01100","00100","00100","00100","00100","01110"],
'2':["01110","10001","00001","00110","01000","10000","11111"],
'3':["11110","00001","00001","01110","00001","00001","11110"],
'4':["00010","00110","01010","10010","11111","00010","00010"],
'5':["11111","10000","11110","00001","00001","10001","01110"],
'6':["00110","01000","10000","11110","10001","10001","01110"],
'7':["11111","00001","00010","00100","01000","01000","01000"],
'8':["01110","10001","10001","01110","10001","10001","01110"],
'9':["01110","10001","10001","01111","00001","00010","01100"],
' ':["00000","00000","00000","00000","00000","00000","00000"],
'.':["00000","00000","00000","00000","00000","01100","01100"],
',':["00000","00000","00000","00000","01100","00100","01000"],
':':["00000","01100","01100","00000","01100","01100","00000"],
';':["00000","01100","01100","00000","01100","00100","01000"],
'!':["00100","00100","00100","00100","00100","00000","00100"],
'?':["01110","10001","00001","00110","00100","00000","00100"],
'-':["00000","00000","00000","01110","00000","00000","00000"],
"'": ["00100","00100","01000","00000","00000","00000","00000"],
'"':["01010","01010","00000","00000","00000","00000","00000"],
'%':["11001","11010","00010","00100","01000","01011","10011"],
'/':["00001","00010","00010","00100","01000","01000","10000"],
'(':["00010","00100","01000","01000","01000","00100","00010"],
')':["01000","00100","00010","00010","00010","00100","01000"],
'+':["00000","00100","00100","01110","00100","00100","00000"],
'&':["01100","10010","10100","01000","10101","10010","01101"],
}
def text_width(s, scale=1):
    return len(s)*(5*scale + scale) - scale if s else 0
def draw_text(c, x, y, s, col, scale=1):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == '1':
                    c.rect(cx+rx*scale, y+ry*scale, scale, scale, col)
        cx += 6*scale
    return cx
def draw_centered(c, cx, y, s, col, scale=1):
    return draw_text(c, cx - text_width(s, scale)//2, y, s, col, scale)
def wrap_lines(s, max_chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur+" "+w).strip()
        if len(t) <= max_chars: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

# ---------- colours ----------
INK=(20,20,20); PAPER=(250,248,240); GREY=(110,110,110); LGREY=(200,200,195)
RED=(178,30,30); BLUE=(30,70,140); SKY=(150,170,190); DSKY=(90,105,125)
BROWN=(120,85,55); RUBBLE=(140,125,105); ORANGE=(230,120,20); YELLOW=(240,200,40)
SEA=(40,110,150); GREEN=(50,130,70); SAND=(220,200,160)

def person(c, x, y, s, shirt, pants=(40,40,60)):
    c.circle(x, y, 3*s//2, (240,200,160))  # head approx
    c.rect(x-s, y+2*s, 2*s, 5*s, shirt)
    c.rect(x-s, y+7*s, s, 5*s, pants); c.rect(x, y+7*s, s, 5*s, pants)

def scene_brazil(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    # storm clouds
    for cx, cy, rx in [(x+60,y+22,55),(x+150,y+16,70),(x+280,y+24,60),(x+380,y+18,55)]:
        c.ellipse(cx, cy, rx, 14, DSKY); c.ellipse(cx, cy+8, rx-10, 12, (110,120,135))
    # rain streaks
    for i in range(0, w, 28):
        c.line(x+i, y+38, x+i-6, y+52, (220,230,240), 1)
    gy = y + h - 52
    c.rect(x, gy, w, h-(gy-y), (165,150,125))  # ground
    # collapsed house left: tilted walls, no roof
    c.rect(x+28, gy-62, 110, 62, (235,225,200))
    c.line(x+28, gy-62, x+138, gy-62, INK, 3)
    c.rect(x+62, gy-34, 22, 34, (90,60,40))
    c.rect(x+96, gy-52, 20, 20, (170,200,220))
    c.line(x+20, gy-78, x+90, gy-60, BROWN, 5); c.line(x+90, gy-60, x+150, gy-84, BROWN, 5)
    # roofless house right
    c.rect(x+300, gy-56, 120, 56, (225,210,185))
    c.rect(x+338, gy-30, 24, 30, (90,60,40)); c.rect(x+376, gy-46, 22, 20, (170,200,220))
    c.line(x+292, gy-56, x+428, gy-56, RED, 4)
    # fallen roof in middle
    c.tri(x+165, gy, x+235, gy-38, x+295, gy, BROWN)
    c.tri(x+175, gy, x+235, gy-30, x+285, gy, (160,110,70))
    # rubble piles
    for bx, bw in [(x+10,90),(x+150,120),(x+330,110)]:
        c.tri(bx, gy+34, bx+bw//2, gy+6, bx+bw, gy+34, RUBBLE)
        for dx in range(8, bw-8, 18): c.rect(bx+dx, gy+24, 10, 6, GREY)
    # rescue workers in orange
    for wx, col in [(x+178, ORANGE),(x+218, ORANGE),(x+258, YELLOW)]:
        c.circle(wx, gy-26, 6, (240,200,160)); c.rect(wx-7, gy-32, 14, 5, YELLOW)
        c.rect(wx-6, gy-20, 12, 18, col); c.rect(wx-6, gy-2, 5, 12, (40,40,60)); c.rect(wx+1, gy-2, 5, 12, (40,40,60))

def scene_tanker(c, x, y, w, h):
    c.rect(x, y, w, h//2+10, (170,195,220))
    c.rect(x, y+h//2+10, w, h-h//2-10, SEA)
    for i in range(0, w, 36): c.hline(x+i, y+h//2+26, 18, (120,200,230), 2)
    # skyline
    for bx, bh in [(4,26),(28,38),(58,20),(210,30),(238,22)]:
        c.rect(x+bx, y+h//2+10-bh, 18, bh, (120,130,145))
    # tanker hull
    hy = y + h//2 - 6
    c.rect(x+30, hy, w-70, 22, (60,60,70)); c.rect(x+30, hy, w-70, 6, RED)
    c.tri(x+w-40, hy, x+w-14, hy+11, x+w-40, hy+22, (60,60,70))
    c.rect(x+52, hy-20, 46, 20, (230,230,230)); c.rect(x+150, hy-14, 90, 14, (200,90,40))
    # smoke
    for sx, sy, r in [(64,hy-30,8),(74,hy-40,10),(86,hy-48,11)]:
        c.circle(x+sx, y+sy if False else sy, r, (90,90,90))
    c.rect(x, y, w, h, (0,0,0)) if False else None

def scene_peru(c, x, y, w, h):
    c.rect(x, y, w, h, (190,210,230))
    # mountains
    c.tri(x, y+h-28, x+80, y+18, x+165, y+h-28, (110,100,120))
    c.tri(x+90, y+h-28, x+175, y+8, x+265, y+h-28, (90,85,110))
    c.tri(x+185, y+h-28, x+250, y+30, x+w, y+h-28, (120,110,125))
    c.tri(x+158, y+26, x+175, y+8, x+192, y+26, (255,255,255))
    c.tri(x+68, y+34, x+80, y+18, x+92, y+34, (255,255,255))
    c.rect(x, y+h-28, w, 28, (150,125,90))
    # cracked ground
    c.line(x+20, y+h-14, x+70, y+h-20, INK, 2); c.line(x+70, y+h-20, x+120, y+h-10, INK, 2)
    c.line(x+120, y+h-10, x+190, y+h-22, INK, 2); c.line(x+190, y+h-22, x+250, y+h-12, INK, 2)
    # seismograph line in a white box
    c.rect(x+w-118, y+10, 108, 34, (255,255,255))
    pts=[0,0,2,-2,1,10,-12,14,-8,3,0,1]
    for i in range(len(pts)-1):
        c.line(x+w-112+i*9, y+27+pts[i], x+w-112+(i+1)*9, y+27+pts[i+1], RED, 2)

def scene_cop(c, x, y, w, h):
    c.rect(x, y, w, h, (210,225,205))
    # globe
    c.circle(x+62, y+h//2, 42, (70,140,200))
    c.ellipse(x+48, y+h//2-12, 20, 12, GREEN); c.ellipse(x+78, y+h//2+14, 16, 10, GREEN)
    c.ellipse(x+80, y+h//2-20, 10, 8, GREEN)
    # thermometer
    tx = x+128
    c.rect(tx, y+12, 12, 50, (255,255,255)); c.circle(tx+6, y+70, 11, RED)
    c.rect(tx+3, y+28, 6, 36, RED)
    for i in range(5): c.hline(tx+14, y+22+i*12, 8, INK, 2)
    # conference table + people
    c.rect(x+165, y+h//2+24, w-180, 12, BROWN)
    for px_ in [x+185, x+225, x+265]:
        c.circle(px_, y+h//2-2, 6, (240,200,160))
        c.rect(px_-6, y+h//2+4, 12, 20, BLUE)
    c.rect(x+168, y+8, 90, 20, (255,255,255))
    draw_text(c, x+175, y+15, "COP31", RED, 2)

# ---------- layout ----------
def main():
    c = Canvas(W, H, PAPER)
    # border
    c.rect(0,0,W,6,INK); c.rect(0,H-6,W,6,INK); c.rect(0,0,6,H,INK); c.rect(W-6,0,6,H,INK)
    # masthead
    draw_centered(c, W//2, 18, "THE DAILY PICTURE", INK, 7)
    c.hline(24, 78, W-48, INK, 3); c.hline(24, 84, W-48, INK, 1)
    draw_centered(c, W//2, 92, "SUNDAY 22 NOVEMBER 2026", RED, 4)
    draw_text(c, 24, 94, "NO. 2211", GREY, 2)
    c.hline(24, 124, W-48, INK, 2)
    # LEAD: left 2/3
    lx, ly, lw = 24, 134, 640
    scene_brazil(c, lx, ly, lw, 236)
    c.rect(lx, ly, lw, 236, PAPER) if False else None
    # frame around lead image
    for t in range(2):
        c.hline(lx-t, ly-t, lw+2*t, INK, 1); c.hline(lx-t, ly+236+t, lw+2*t, INK, 1)
        c.vline(lx-t, ly-t, 236+2*t, INK, 1); c.vline(lx+lw+t, ly-t, 236+2*t, INK, 1)
    hy = ly + 246
    for i, line in enumerate(["BRAZIL TOWN DIGS OUT", "AFTER DEADLY STORM"]):
        draw_text(c, lx, hy + i*40, line, INK, 5)
    cap = ["RESIDENTS CLEAR RUBBLE FROM COLLAPSED HOMES.",
           '"WE LOST EVERYTHING," ONE SURVIVOR TOLD AFP.',
           "RESCUE TEAMS SEARCH THE WRECKAGE. (AFP)"]
    for i, line in enumerate(cap):
        draw_text(c, lx, hy+86+i*16, line, (60,60,60), 2)
    # RIGHT column: tanker + peru stacked
    rx, rw = 688, 312
    c.vline(676, 134, 470, LGREY, 2)
    draw_text(c, rx, 134, "MIDDLE EAST", RED, 3)
    scene_tanker(c, rx, 160, rw, 110)
    for i, line in enumerate(["HOUTHIS STRIKE RIYADH;", "IRAN HITS 3 GULF TANKERS"]):
        draw_text(c, rx, 276+i*16, line, INK, 2)
    c.hline(rx, 312, rw, LGREY, 2)
    draw_text(c, rx, 322, "PERU QUAKE 6.7", RED, 3)
    scene_peru(c, rx, 348, rw, 110)
    for i, line in enumerate(["ANDES QUAKE, MAG. 6.7.", "NO DEATHS REPORTED."]):
        draw_text(c, rx, 464+i*16, line, INK, 2)
    # BOTTOM LEFT: COP31 wide strip under lead
    c.hline(24, 512, W-48, INK, 2)
    draw_text(c, 24, 522, "COP31 TALKS DEADLOCKED", RED, 3)
    scene_cop(c, 24, 548, 470, 92)
    for i, line in enumerate(["CLIMATE TALKS IN ANTALYA", "INTO OVERTIME, STUCK ON", "FOSSIL FUELS. TALKS GO ON"]):
        draw_text(c, 504, 556+i*20, line, INK, 2)
    draw_text(c, 504, 622, "ANTALYA, TURKIYE", GREY, 2)
    # weather / index box right of COP text
    c.rect(816, 548, 184, 92, (235,232,220))
    draw_text(c, 828, 558, "TODAY IN BRIEF", INK, 2)
    for i, line in enumerate(["BRAZIL STORM", "PERU QUAKE 6.7", "ANTALYA TALKS", "GULF TANKERS"]):
        draw_text(c, 828, 578+i*16, line, (60,60,60), 2)
    # TICKER
    ty = 648
    c.rect(12, ty, W-24, 108, INK)
    draw_text(c, 24, ty+6, "LATEST WIRE", YELLOW, 2)
    ticker = [
        "MEXICO CAPTURES CARTEL KINGPIN EL CHAPO ISIDRO",
        "NVIDIA FACES US ACCOUNTING PROBE",
        "TRUMP VOWS PUSH TO CAP CARD RATES AT 10%",
        "AIR NIUGINI JET LANDS SAFELY AFTER ENGINE SCARE - ALL 146 SAFE",
    ]
    for i, line in enumerate(ticker):
        draw_text(c, 24, ty+28+i*19, line, (255,255,255), 2)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or ("/output" if os.path.isdir("/output") else "./out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(W, H, bytes(c.buf)))
    print(f"wrote {path}")

if __name__ == "__main__":
    main()
