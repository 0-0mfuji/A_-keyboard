from pathlib import Path
import sexpdata as s,uuid,sys
S=s.Symbol
get=lambda n,k:next((x for x in n if isinstance(x,list) and x and str(x[0])==k),None)
side=sys.argv[1];p=Path(__file__).parent/side/'keyboard.kicad_pcb';a=s.loads(p.read_text())
for f in a:
 if not isinstance(f,list) or str(f[0])!='footprint':continue
 ref=next(n[2] for n in f if isinstance(n,list) and str(n[0])=='property' and n[1]=='Reference')
 if ref in ['J1','J2']:
  f[:]=[n for n in f if not (isinstance(n,list) and str(n[0]).startswith('fp_'))]
  for layer in ['F.SilkS','B.SilkS']:
   txt=[S('fp_text'),S('user'),'BAT  -    +',[S('at'),1.75,-2.5,180],[S('layer'),layer],[S('uuid'),str(uuid.uuid4())],[S('effects'),[S('font'),[S('size'),.9,.9],[S('thickness'),.15]]]]
   if layer=='B.SilkS':txt[-1].append([S('justify'),S('mirror')])
   f.append(txt)
 if ref.startswith('C_RGB_BULK'):
  f[:]=[n for n in f if not (isinstance(n,list) and str(n[0]).startswith('fp_'))]
  f.append([S('fp_rect'),[S('start'),-2.3,-1.2],[S('end'),2.3,1.2],[S('stroke'),[S('width'),.05],[S('type'),S('default')]],[S('fill'),S('none')],[S('layer'),'B.CrtYd'],[S('uuid'),str(uuid.uuid4())]])
p.write_text(s.dumps(a))
