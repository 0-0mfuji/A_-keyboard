import pcbnew as p,json,pathlib,math,sys
mm=p.FromMM
vec=lambda x,y:p.VECTOR2I(mm(x),mm(y))
for side,num in [(sys.argv[1],1 if sys.argv[1]=='left' else 2)]:
 path='hardware/routing-work/'+side+'/keyboard.kicad_pcb';b=p.LoadBoard(path);fs={f.GetReference():f for f in b.GetFootprints()};netmap=json.load(open('hardware/routing-work/'+side+'-netmap.json'))
 for name in set(netmap.values()):
  if not b.FindNet(name):b.Add(p.NETINFO_ITEM(b,name))
 for f in b.GetFootprints():
  for pad in f.Pads():
   name=netmap.get(f.GetReference()+':'+pad.GetNumber())
   if name is not None:pad.SetNet(b.FindNet(name))
 # Remove initial incomplete tracks for coherent new layout; original remains backed up.
 removed_tracks=list(b.GetTracks())
 for t in removed_tracks:b.Remove(t)
 # Pack power block in free area below MCU, respecting through-hole footprints.
 placements={
 'U_RGB':(146,37,0),'L_RGB':(146,33.8,0),'C_RGB_IN':(143,36.8,90),
 'C_RGB_OUT1_':(149,37,90),'C_RGB_OUT2_':(151.5,37,90),'C_RGB_BULK':(153.8,37,90),
 'R_RGB_FB_TOP':(146.5,40,0),'R_RGB_FB_BOT':(143.2,40,0),'R_RGB_EN_PD':(139.8,40,0),
 'U_LS':(135.8,34.5,0),'C_LS':(136,31.5,0),'R_RGB_DATA':(135.8,38,0)}
 for prefix,(x,y,a) in placements.items():
  if side=='right':x=328.65-x
  f=fs[prefix+str(num)];f.SetOrientationDegrees(a);f.SetPosition(vec(x,y))
 # Ensure references for board-only mechanical items are unique without changing geometry.
 counters={}
 for f in b.GetFootprints():
  ref=f.GetReference()
  if ref in ['H','STAB']:
   counters[ref]=counters.get(ref,0)+1;f.SetReference(ref+str(counters[ref]));f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY);f.SetLocked(True)
  if ref.startswith('LED'):
   # Retain opening and pad anchors; move copper outerwards by 0.21mm.
   for pad in f.Pads():
    old=pad.GetOffset();pad.SetOffset(p.VECTOR2I(mm(.56 if old.x>0 else -.56),old.y))
  # Hide redundant values only; keep designators and polarity symbols.
  f.Value().SetVisible(False)
 p.SaveBoard(path,b)
 pro=pathlib.Path(path.replace('.kicad_pcb','.kicad_pro'));d=json.loads(pro.read_text());d['board']['design_settings']['rules']['min_copper_edge_clearance']=.3
 for cl in d['net_settings']['classes']:
  if cl['name']=='Default':cl.update(track_width=.25,clearance=.2,via_diameter=.65,via_drill=.3)
 pro.write_text(json.dumps(d,indent=2))
 print(side,'prepared',len(b.GetFootprints()))
