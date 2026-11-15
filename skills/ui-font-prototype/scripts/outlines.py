"""Original printable-ASCII centerlines and pure geometric stroke construction.

No existing font outlines are loaded. Rounded and angular variants share this skeleton.
"""
import math

def path(s):return [tuple(map(float,p.split(','))) for p in s.split()]
def ellipse(x,y,rx,ry,n=24):return [(x+rx*math.cos(i*2*math.pi/n),y+ry*math.sin(i*2*math.pi/n)) for i in range(n+1)]
S={}
def put(chars,*lines):
 for c in chars:S[c]=[path(l) if isinstance(l,str) else l for l in lines]
put('A','0,0 3,8 6,0','1.1,3 4.9,3');put('B','0,0 0,8 3.7,8 5.7,7 5.7,5.4 3.7,4 0,4','3.7,4 6,2.8 6,1.2 4,0 0,0')
put('C','6,7 4.6,8 1.6,8 0,6.4 0,1.6 1.6,0 4.6,0 6,1');put('D','0,0 0,8 3.5,8 6,6 6,2 3.5,0 0,0')
put('E','6,8 0,8 0,0 6,0','0,4 4.8,4');put('F','0,0 0,8 6,8','0,4 4.8,4')
put('G','6,7 4.6,8 1.6,8 0,6.4 0,1.6 1.6,0 4.6,0 6,1.6 6,4 3.5,4')
put('H','0,0 0,8','6,0 6,8','0,4 6,4');put('I','1,8 5,8','3,8 3,0','1,0 5,0')
put('J','1,8 6,8 6,1.6 4.4,0 1.6,0 0,1.6');put('K','0,0 0,8','6,8 0,3.8 6,0')
put('L','0,8 0,0 6,0');put('M','0,0 0,8 3,3.7 6,8 6,0');put('N','0,0 0,8 6,0 6,8')
put('O',ellipse(3,4,3,4));put('P','0,0 0,8 4.2,8 6,6.7 6,5.2 4.2,4 0,4')
put('Q',ellipse(3,4,3,4),'3.6,2 6.7,-0.7');put('R','0,0 0,8 4.2,8 6,6.7 6,5.2 4.2,4 0,4','3.3,4 6,0')
put('S','6,7 4.6,8 1.5,8 0,6.5 0.6,4.8 5.4,3.2 6,1.5 4.5,0 1.4,0 0,1')
put('T','0,8 6,8','3,8 3,0');put('U','0,8 0,1.7 1.5,0 4.5,0 6,1.7 6,8')
put('V','0,8 3,0 6,8');put('W','0,8 1.3,0 3,4.5 4.7,0 6,8');put('X','0,8 6,0','0,0 6,8');put('Y','0,8 3,4 6,8','3,4 3,0');put('Z','0,8 6,8 0,0 6,0')
# Lowercase drawn independently rather than borrowed or small-cap substitutions.
put('a',ellipse(2.7,2.7,2.7,2.7),'5.4,5.4 5.4,0');put('b','0,0 0,8',ellipse(2.7,2.7,2.7,2.7));put('c','5.4,4.6 4.2,5.4 1.4,5.4 0,4 0,1.4 1.4,0 4.2,0 5.4,0.8');put('d',ellipse(2.7,2.7,2.7,2.7),'5.4,0 5.4,8')
put('e','0,2.7 5.4,2.7 5.4,4 4,5.4 1.4,5.4 0,4 0,1.4 1.4,0 4.2,0 5.4,0.8');put('f','1.8,0 1.8,6.4 3,8 5,8','0,5.4 4.4,5.4')
put('g',ellipse(2.7,2.7,2.7,2.7),'5.4,5.4 5.4,-1.6 4.2,-2.5 1.4,-2.5 0,-1.8');put('h','0,0 0,8','0,4 1.4,5.4 3.8,5.4 5.4,4 5.4,0')
put('i','2.5,0 2.5,5.4','2.5,7.4 2.5,7.5');put('j','3.5,5.4 3.5,-1.4 2.5,-2.5 0.8,-2.5','3.5,7.4 3.5,7.5');put('k','0,0 0,8','5.4,5.4 0,2.7 5.4,0');put('l','2,8 2,1 3,0 4,0')
put('m','0,0 0,5.4','0,4.2 1,5.4 2,5.4 3,4.2 3,0','3,4.2 4,5.4 5,5.4 6,4.2 6,0');put('n','0,0 0,5.4','0,4 1.4,5.4 3.8,5.4 5.4,4 5.4,0')
put('o',ellipse(2.7,2.7,2.7,2.7));put('p','0,-2.5 0,5.4',ellipse(2.7,2.7,2.7,2.7));put('q',ellipse(2.7,2.7,2.7,2.7),'5.4,5.4 5.4,-2.5');put('r','0,0 0,5.4','0,4 1.4,5.4 3.7,5.4 5,4.5')
put('s','5.4,4.6 4,5.4 1.4,5.4 0,4.2 1.2,2.8 4.2,2.2 5.4,1 4,0 1.4,0 0,0.8');put('t','2,7.5 2,1.2 3.2,0 5,0','0,5.4 4.5,5.4');put('u','0,5.4 0,1.4 1.4,0 3.8,0 5.4,1.4','5.4,5.4 5.4,0');put('v','0,5.4 2.7,0 5.4,5.4');put('w','0,5.4 1.3,0 3,3 4.7,0 6,5.4');put('x','0,5.4 5.4,0','0,0 5.4,5.4');put('y','0,5.4 2.7,0','5.4,5.4 1.6,-2.5 0,-2.5');put('z','0,5.4 5.4,5.4 0,0 5.4,0')
put('0',ellipse(3,4,3,4),'1.2,1.5 4.8,6.5');put('1','1,6.5 3,8 3,0','0.8,0 5.2,0');put('2','0,6.5 1.5,8 4.5,8 6,6.5 6,5 0,0 6,0');put('3','0,7 1.5,8 4.5,8 6,6.5 4,4 2.5,4','4,4 6,2.5 6,1.5 4.5,0 1.5,0 0,1');put('4','4.5,0 4.5,8 0,2.5 6,2.5');put('5','6,8 0,8 0,4.5 4.5,4.5 6,3 6,1.5 4.5,0 1.5,0 0,1');put('6','5.5,7.5 4,8 1.5,7 0,4.5 0,1.5 1.5,0 4.5,0 6,1.5 6,3.5 4.5,5 2,5 0,3.5');put('7','0,8 6,8 1.5,0');put('8',ellipse(3,6,2.5,2),ellipse(3,2,3,2));put('9','6,4.5 4.5,3 1.5,3 0,4.5 0,6.5 1.5,8 4.5,8 6,6.5 6,3 4.5,0 1,0')
for c,lines in {'.':['3,0 3,0.1'],',':['3,0.8 2,-1.2'],':':['3,5 3,5.1','3,0 3,0.1'],';':['3,5 3,5.1','3,0.8 2,-1.2'],'!':['3,8 3,2.2','3,0 3,0.1'],'?':['0,6.5 1.5,8 4.5,8 6,6.5 5,4.5 3,3.5 3,2','3,0 3,0.1'],'-':['1,3 5,3'],'_':['0,-1 6,-1'],'=':['0,2 6,2','0,5 6,5'],'+':['0,3.5 6,3.5','3,0.5 3,6.5'],'/':['0,-1 6,9'],'\\':['0,9 6,-1'],'(':['4,9 2,7 1,4 2,1 4,-1'],')':['2,9 4,7 5,4 4,1 2,-1'],'[':['4,9 1,9 1,-1 4,-1'],']':['2,9 5,9 5,-1 2,-1'],'<':['5,7 1,4 5,1'],'>':['1,7 5,4 1,1'],'|':['3,-1 3,9'],"'":['3,8 3,6'],'"':['2,8 2,6','4,8 4,6'],'*':['3,7 3,2','0.5,5.8 5.5,3.2','0.5,3.2 5.5,5.8'],'#':['2,0 3,8','4,0 5,8','0,2.5 6,2.5','0,5.5 6,5.5'],'^':['1,6 3,8 5,6'],'`':['2,8 3,6.5'],'~':['0,3 1.5,4 4.5,2 6,3'],'{':['5,9 3,9 2,7 2,5 1,4 2,3 2,1 3,-1 5,-1'],'}':['1,9 3,9 4,7 4,5 5,4 4,3 4,1 3,-1 1,-1']}.items():put(c,*lines)
put('$',*S['S'],[(3,-1),(3,9)]);put('%',ellipse(1,6.5,1,1.5),ellipse(5,1.5,1,1.5),'0,0 6,8');put('&','6,0 1,6 1,7.3 2,8 3.5,8 4.5,7 4,5.5 0,2.5 0,1 1.5,0 3.5,0 6,3.5');put('@',ellipse(3,4,3.5,4),ellipse(3,4,1.5,2),'4.5,6 4.5,2 6,2 6.5,4')


def contours(character, stroke=70, width=1.0, construction="rounded"):
    """Return clockwise filled polygons; overlaps are deliberately retained."""
    if construction not in {"rounded", "angular"}:
        raise ValueError("Unknown construction")
    if not math.isfinite(stroke) or not 40 <= stroke <= 100:
        raise ValueError("Stroke must be finite and between 40 and 100")
    if not math.isfinite(width) or not 0.7 <= width <= 1.3:
        raise ValueError("Width must be finite and between 0.7 and 1.3")
    result = []
    for centerline in S.get(character, []):
        points = [(x * width * 80, y * 80) for x, y in centerline]
        for a, b in zip(points, points[1:]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            length = math.hypot(dx, dy)
            if length == 0:
                continue
            nx, ny = -dy / length * stroke / 2, dx / length * stroke / 2
            result.append([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)])
        if construction == "rounded":
            for x, y in points:
                result.append([(x+stroke/2*math.cos(-i*math.tau/16), y+stroke/2*math.sin(-i*math.tau/16)) for i in range(16)])
    if not result:
        return [], 300
    xmin = min(x for polygon in result for x, _ in polygon)
    xmax = max(x for polygon in result for x, _ in polygon)
    shifted = [[(round(x-xmin+70), round(y)) for x, y in polygon] for polygon in result]
    return shifted, round(xmax-xmin+140)
