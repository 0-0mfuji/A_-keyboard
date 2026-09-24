from pathlib import Path
import sexpdata as s,copy,json,uuid,sys,shutil
S=s.Symbol
get=lambda n,k:next((x for x in n if isinstance(x,list) and x and str(x[0])==k),None)
prop=lambda n,k:next((x for x in n if isinstance(x,list) and len(x)>2 and str(x[0])=='property' and x[1]==k),None)
root=Path(__file__).parent;side=sys.argv[1];d=root/side
parts=json.loads((root/'parts.json').read_text()); pcb=d/'keyboard.kicad_pcb';a=s.loads(pcb.read_text());mapping={}
for f in a:
 if not isinstance(f,list) or str(f[0])!='footprint':continue
 ref=prop(f,'Reference')[2];val=prop(f,'Value')[2];mapping[ref]={'footprint':f[1],'value':val}
 manual=ref.startswith(('SW','LED','J')) or ref in ['U1','U2'];mechanical=ref.startswith(('H','STAB'))
 attr=get(f,'attr')
 if attr is None:attr=[S('attr')];f.append(attr)
 for tag in ['exclude_from_pos_files','exclude_from_bom']:
  if (manual or mechanical) and S(tag) not in attr:attr.append(S(tag))
 # Hand-solder pads do not receive stencil paste.
 if manual:
  for pad in f:
   if isinstance(pad,list) and str(pad[0])=='pad':
    layers=get(pad,'layers')
    if layers:layers[:]=[x for x in layers if str(x) not in ['F.Paste','B.Paste']]
 if val in parts and not manual:
  for key,value in [('MPN',parts[val]['mpn']),('LCSC',parts[val]['lcsc'])]:
   old=prop(f,key)
   if old:old[2]=value
   else:f.append([S('property'),key,value,[S('at'),0,0,0],[S('layer'),'B.Fab'],[S('hide'),S('yes')],[S('effects'),[S('font'),[S('size'),1,1],[S('thickness'),.15]]])
pcb.write_text(s.dumps(a))
for sch in d.glob('*.kicad_sch'):
 a=s.loads(sch.read_text())
 for sym in a:
  if not isinstance(sym,list) or str(sym[0])!='symbol' or not prop(sym,'Reference'):continue
  ref=prop(sym,'Reference')[2]
  if ref not in mapping:continue
  val=mapping[ref]['value'];prop(sym,'Value')[2]=val;prop(sym,'Footprint')[2]=mapping[ref]['footprint']
  manual=ref.startswith(('SW','LED','J')) or ref in ['U1','U2']
  bom=get(sym,'in_bom')
  if bom:bom[1]=S('no' if manual else 'yes')
  if val in parts and not manual:
   for key,value in [('MPN',parts[val]['mpn']),('LCSC',parts[val]['lcsc'])]:
    old=prop(sym,key)
    if old:old[2]=value
    else:
     q=copy.deepcopy(prop(sym,'Footprint'));q[1]=key;q[2]=value;sym.append(q)
 sch.write_text(s.dumps(a))
shutil.copy2(root.parents[0]/'Keyboard.kicad_sym',d/'Keyboard.kicad_sym')
(d/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Keyboard")(type "KiCad")(uri "${KIPRJMOD}/Keyboard.kicad_sym")(options "")(descr "")))\n')
# Library path is local to each board so copying the final project preserves dependencies.
(d/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Keyboard")(type "KiCad")(uri "${KIPRJMOD}/Keyboard.pretty")(options "")(descr "v2 production footprints")))\n')
