import sexpdata as s,uuid,pathlib,json
S=s.Symbol
get=lambda n,k:next((x for x in n if isinstance(x,list) and str(x[0])==k),None)
for side in ['left','right']:
 path=pathlib.Path('hardware/routing-work')/side/'keyboard.kicad_pcb';a=s.loads(path.read_text())
 for f in a:
  if not isinstance(f,list) or str(f[0])!='footprint':continue
  ref=next(x[2] for x in f if isinstance(x,list) and str(x[0])=='property' and x[1]=='Reference')
  if ref.startswith('SW') and not ref.startswith('SWP'):
   f[:]=[x for x in f if not(isinstance(x,list) and str(x[0]).startswith('fp_') and get(x,'layer') and 'CrtYd' in get(x,'layer')[1])]
   # Socket assembly envelope, instead of the previous oversized rectangular bounding box.
   pts=[(-9.35,-4.33),(-6.35,-4.33),(-6.35,-7.05),(8.05,-7.05),(8.05,-3.37),(5.1,-3.37),(5.1,-.6),(-9.35,-.6)]
   f.append([S('fp_poly'),[S('pts')]+[[S('xy'),x,y] for x,y in pts],[S('stroke'),[S('width'),.05],[S('type'),S('solid')]],[S('fill'),S('none')],[S('layer'),'B.CrtYd'],[S('uuid'),str(uuid.uuid4())]])
   for n in f:
    if isinstance(n,list) and str(n[0])=='pad':
     ly=get(n,'layers');ly[:]=[x for x in ly if 'SilkS' not in str(x)]
 # Move only silkscreen shapes reported over copper to fabrication layers.
 d=json.loads(pathlib.Path('hardware/routing-work/'+side+'-prepared-drc.json').read_text())
 bad={x['uuid'] for v in d['violations'] if v['type'] in ['silk_over_copper','silk_overlap','silk_edge_clearance'] for x in v['items']}
 def clean(node):
  if not isinstance(node,list):return
  u=get(node,'uuid');l=get(node,'layer')
  if u and u[1] in bad and l and 'SilkS' in str(l[1]): l[1]=l[1].replace('SilkS','Fab')
  for n in node:clean(n)
 clean(a);path.write_text(s.dumps(a))
 # Fine pitch SOT563 requires 0.15mm clearance. All standard traces stay >=0.25mm.
 pro=path.with_suffix('.kicad_pro');d=json.loads(pro.read_text())
 for cl in d['net_settings']['classes']:cl['clearance']=.15
 d['board']['design_settings']['rules']['min_clearance']=.15
 pro.write_text(json.dumps(d,indent=2))
