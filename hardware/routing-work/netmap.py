import sexpdata as s,json
from pathlib import Path
get=lambda n,k:next((x for x in n if isinstance(x,list) and str(x[0])==k),None)
for side in ['left','right']:
 a=s.loads(Path('hardware/routing-work/'+('right-fixed' if side=='right' else 'left')+'.net').read_text());m={}
 for n in get(a,'nets')[1:]:
  name=get(n,'name')[1]
  for node in n:
   if isinstance(node,list) and str(node[0])=='node':m[get(node,'ref')[1]+':'+get(node,'pin')[1]]=name
 Path('hardware/routing-work/'+side+'-netmap.json').write_text(json.dumps(m))
 if side=='right': print({k:v for k,v in m.items() if k.startswith(('L_RGB2:','U_RGB2:'))})
