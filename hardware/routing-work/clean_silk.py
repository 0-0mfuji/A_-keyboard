import sexpdata as s,json,pathlib,sys
get=lambda n,k:next((x for x in n if isinstance(x,list) and str(x[0])==k),None)
for side in ['left','right']:
 path=pathlib.Path('hardware/routing-work')/side/'keyboard.kicad_pcb';a=s.loads(path.read_text());d=json.loads(pathlib.Path('hardware/routing-work/'+side+'-'+sys.argv[1]+'-drc.json').read_text());bad={x['uuid'] for v in d['violations'] if v['type'].startswith('silk_') for x in v['items']}
 def walk(n):
  if not isinstance(n,list):return
  u=get(n,'uuid');l=get(n,'layer')
  if u and str(u[1]) in bad and l and 'SilkS' in str(l[1]):l[1]=str(l[1]).replace('SilkS','Fab')
  for x in n:walk(x)
 walk(a);path.write_text(s.dumps(a))
