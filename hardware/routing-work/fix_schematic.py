import sexpdata as s,uuid,copy
from pathlib import Path
get=lambda n,k:next((x for x in n if isinstance(x,list) and str(x[0])==k),None)
p=Path('hardware/routing-work/right/power.kicad_sch');a=s.loads(p.read_text())
ids={'18900111-610d-424b-9526-1f70ead8655b','dca11b0b-c97d-58c5-aaf8-5c956bf70a85'}
a=[n for n in a if not (isinstance(n,list) and get(n,'uuid') and get(n,'uuid')[1] in ids)]
label=copy.deepcopy(next(n for n in a if isinstance(n,list) and str(n[0])=='label' and n[1]=='RGB_SW_RIGHT'))
get(label,'at')[1:3]=[121.92,175.26];get(label,'uuid')[1]=str(uuid.uuid4());a.append(label)
p.write_text(s.dumps(a))
print('Separated TPS61023 VIN and SW in working schematic')
