import pcbnew as p,sys,math
s=sys.argv[1];path='hardware/routing-work/'+s+'/keyboard.kicad_pcb';b=p.LoadBoard(path);fs={f.GetReference():f for f in b.GetFootprints()}
for r,f in fs.items():
 if r.startswith('LED'):
  cap=fs.get('C_RGB'+r[3:]);a=math.radians(f.GetOrientationDegrees());pos=f.GetPosition()
  cap.SetPosition(p.VECTOR2I(pos.x+p.FromMM(6.5*math.cos(a)),pos.y-p.FromMM(6.5*math.sin(a))))
  cap.SetOrientationDegrees(f.GetOrientationDegrees()-90)
if s=='right':fs['R_RGB_DATA2'].SetPosition(p.VECTOR2I(p.FromMM(191.5),p.FromMM(25)))
p.SaveBoard(path,b)
