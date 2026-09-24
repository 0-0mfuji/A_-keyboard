from pathlib import Path
import re,sys
from shapely.geometry import Polygon
side=sys.argv[1];p=Path(__file__).parent/side/'route.dsn';s=p.read_text()
def expand(m):
 v=list(map(float,m[1].split()));poly=Polygon(list(zip(v[::2],v[1::2]))).buffer(175,join_style=2)
 return '(keepout "" (polygon signal 0 '+ ' '.join(f'{x:.1f} {y:.1f}' for x,y in poly.exterior.coords)+'))'
s=re.sub(r'\(keepout "" \(polygon signal 0\s+([0-9.\s-]+)\)\)',expand,s)
s=s.replace('(clearance 37.5 (type smd_smd))','(clearance 150 (type smd_smd))').replace('(width 600)','(width 250)')
(Path(__file__).parent/side/'route2.dsn').write_text(s)
