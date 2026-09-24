import pcbnew as p,json,sys,os
from pathlib import Path
side=sys.argv[1];root=Path(__file__).parent/side;b=p.LoadBoard(str(root/'keyboard.kicad_pcb'))
if side=='right':
 f=next(f for f in b.GetFootprints() if f.GetReference()=='J2');f.SetPosition(p.VECTOR2I(p.FromMM(177.5),p.FromMM(24)))
d=json.load(open('/tmp/v2-'+side+'-placed2.json'));bad={i['uuid'] for v in d['violations'] if v['severity']=='error' for i in v['items']}
tracks=list(b.GetTracks())
for t in tracks:
 if t.m_Uuid.AsString() in bad:b.Remove(t)
p.SaveBoard(str(root/'keyboard.kicad_pcb'),b)
p.ExportSpecctraDSN(b,str(root/'route.dsn'))
sys.stdout.flush();os._exit(0)
