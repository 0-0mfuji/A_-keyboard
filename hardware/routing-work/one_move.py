import pcbnew as p
path='hardware/routing-work/right/keyboard.kicad_pcb';b=p.LoadBoard(path)
f=next(f for f in b.GetFootprints() if f.GetReference()=='C_RGB42');f.SetPosition(p.VECTOR2I(p.FromMM(231.625),p.FromMM(75.7)));p.SaveBoard(path,b)
