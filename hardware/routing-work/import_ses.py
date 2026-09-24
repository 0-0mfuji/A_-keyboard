import pcbnew as p,sys
s=sys.argv[1];path='hardware/routing-work/'+s+'/keyboard.kicad_pcb';b=p.LoadBoard(path)
print('import',p.ImportSpecctraSES(b,'hardware/routing-work/'+s+'.ses'));p.SaveBoard('hardware/routing-work/'+s+'/candidate1.kicad_pcb',b);print('tracks',len(b.GetTracks()),'vias',sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks()))
