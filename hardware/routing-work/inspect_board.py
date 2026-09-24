import pcbnew as p,json,pathlib
mm=lambda v: [p.ToMM(v.x),p.ToMM(v.y)]
for side in ['left','right']:
 b=p.LoadBoard('hardware/routing-work/'+side+'/keyboard.kicad_pcb');out={'footprints':[],'edges':[]}
 for g in b.GetDrawings():
  if g.GetLayer()==p.Edge_Cuts:out['edges'].append({'start':mm(g.GetStart()),'end':mm(g.GetEnd()),'shape':g.GetShapeStr()})
 for f in b.GetFootprints():
  out['footprints'].append({'ref':f.GetReference(),'pos':mm(f.GetPosition()),'angle':f.GetOrientationDegrees(),'layer':f.GetLayerName(),'value':f.GetValue(),'pads':[{'n':a.GetNumber(),'pos':mm(a.GetPosition()),'size':mm(a.GetSize()),'drill':mm(a.GetDrillSize()),'angle':a.GetOrientationDegrees(),'net':a.GetNetname(),'attr':a.GetAttribute()} for a in f.Pads()]})
 pathlib.Path('hardware/routing-work/'+side+'-geometry.json').write_text(json.dumps(out))
