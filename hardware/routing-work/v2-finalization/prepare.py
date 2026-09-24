from pathlib import Path
import pcbnew as p, shutil,json,csv,sys
ROOT=Path(__file__).resolve().parents[2]; WORK=ROOT/'routing-work/v2-finalization'; mm=p.FromMM
V=lambda x,y:p.VECTOR2I(mm(x),mm(y))
for side,n in [(sys.argv[1],1 if sys.argv[1]=='left' else 2)]:
 src=ROOT/'keyboard-v2'/side; dst=WORK/side
 if not (WORK/'backup'/side).exists(): shutil.copytree(src,WORK/'backup'/side)
 if not (WORK/'backup/output').exists():shutil.copytree(ROOT/'routing-work/jlcpcb-output-v2',WORK/'backup/output')
 dst.mkdir(exist_ok=True)
 for f in src.iterdir():
  if f.suffix in ['.kicad_pro','.kicad_sch'] or f.name.endswith('lib-table'):shutil.copy2(f,dst/f.name)
 b=p.LoadBoard(str(WORK/'backup'/side/'keyboard.kicad_pcb')); fs={f.GetReference():f for f in b.GetFootprints()}
 # Place the entire power block on the bottom, below the module antenna region.
 placements={'U_RGB':(147,34,180),'L_RGB':(147,30.6,180),'C_RGB_IN':(144,34,90),'C_RGB_OUT1_':(150,34,90),'C_RGB_OUT2_':(153,34,90),'C_RGB_BULK':(156,34.5,90),'R_RGB_FB_TOP':(150,37.3,180),'R_RGB_FB_BOT':(147,37.3,180),'R_RGB_EN_PD':(144,37.3,180),'U_LS':(145,23,180),'C_LS':(148.5,23,90),'R_RGB_DATA':(141.8,23,90)}
 if side=='right':
  placements={'U_RGB':(185,30,180),'L_RGB':(185,26.6,180),'C_RGB_IN':(188,30,90),'C_RGB_OUT1_':(182,30,90),'C_RGB_OUT2_':(179,30,90),'C_RGB_BULK':(175,34,90),'R_RGB_FB_TOP':(182,33,180),'R_RGB_FB_BOT':(185,33,180),'R_RGB_EN_PD':(188,33,180),'U_LS':(186,22,180),'C_LS':(182,22,90),'R_RGB_DATA':(189,22,90)}

 affected=set()
 for pre,(x,y,ang) in placements.items():
  f=fs[pre+str(n)];affected.update(pad.GetNetCode() for pad in f.Pads())
  if f.GetLayer()!=p.B_Cu:f.Flip(f.GetPosition(),False)
  f.SetPosition(V(x,y));f.SetOrientationDegrees(ang)
 print('after move',type(next(iter(fs.values())).GetPosition()),flush=True)
 # Use a real 1206 footprint for the 100uF bulk capacitor.
 f=fs['C_RGB_BULK'+str(n)];f.SetFPIDAsString('Keyboard:C_1206_3216Metric')
 for pad in f.Pads():
  pad.SetSize(V(1.15,1.8));pad.SetPosition(f.GetPosition()+V(0,1.475 if pad.GetNumber()=='1' else -1.475))
 print('after bulk',type(next(iter(fs.values())).GetPosition()),flush=True)
 # J1/J2 become two 1.0mm plated wire holes, 3.5mm pitch; no half holes.
 f=fs['J'+str(n)];f.SetValue('BAT wire pads (+/-)');f.SetFPIDAsString('Keyboard:Battery_Wire_Pads')

 f.SetPosition(V(154,26) if side=='left' else V(177.5,25));anchor=f.GetPosition();px,py=p.ToMM(anchor)
 for pad in f.Pads():
  affected.add(pad.GetNetCode());pad.SetPosition(V(px if pad.GetNumber()=='1' else px-3.5,py));pad.SetSize(V(2.4,2.4));pad.SetDrillSize(V(1,1));pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetAttribute(p.PAD_ATTRIB_PTH)
 print('after bat',type(next(iter(fs.values())).GetPosition()),flush=True)
 # Remove affected electrical nets, preserving matrix and serial data routing.
 removed_tracks=list(b.GetTracks())
 for t in removed_tracks:
  if t.GetNetCode() in affected:b.Remove(t)
 print('after remove',type(next(iter(fs.values())).GetPosition()),flush=True)
 # Hand-assembled parts are excluded from automated placement and assembly BOM.
 for ref,f in fs.items():
  manual=ref in ['U'+str(n),'SWP'+str(n),'J'+str(n),'J3'] or ref.startswith('SW')
  mechanical=ref.startswith(('H','STAB'))
  if manual or mechanical:f.SetAttributes(f.GetAttributes()|p.FP_EXCLUDE_FROM_POS_FILES|p.FP_EXCLUDE_FROM_BOM)
  f.Value().SetVisible(False)
 p.SaveBoard(str(dst/'keyboard.kicad_pcb'),b)
 p.ExportSpecctraDSN(b,str(dst/'route.dsn'))
 print(side,'tracks retained',len(b.GetTracks()),'affected nets',len(affected))
