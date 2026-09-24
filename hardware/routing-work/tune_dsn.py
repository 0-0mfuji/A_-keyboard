import re,sys
from pathlib import Path
from shapely.geometry import Polygon
side=sys.argv[1];p=Path('hardware/routing-work/'+side+'.dsn');text=p.read_text()
def expand(m):
 vals=list(map(float,m[1].split()));pts=list(zip(vals[::2],vals[1::2]));poly=Polygon(pts).buffer(170,join_style=2)
 return '(keepout "" (polygon signal 0 '+ ' '.join(f'{x:.1f} {y:.1f}' for x,y in poly.exterior.coords)+'))'
text=re.sub(r'\(keepout "" \(polygon signal 0\s+([0-9.\s-]+)\)\)',expand,text)
text=text.replace('(clearance 37.5 (type smd_smd))','(clearance 150 (type smd_smd))')
p.write_text(text)
