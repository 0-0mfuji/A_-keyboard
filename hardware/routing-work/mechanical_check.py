import sexpdata as s,json,pathlib
get=lambda n,k:next((x for x in n if isinstance(x,list) and str(x[0])==k),None)
def snapshot(path):
 a=s.loads(pathlib.Path(path).read_text());edges=[];holes=[];switches=[]
 for n in a:
  if not isinstance(n,list):continue
  if str(n[0]).startswith('gr_') and get(n,'layer') and get(n,'layer')[1]=='Edge.Cuts':edges.append(s.dumps([x for x in n if not(isinstance(x,list) and str(x[0])=='uuid')]))
  if str(n[0])=='footprint':
   ref=next(x[2] for x in n if isinstance(x,list) and str(x[0])=='property' and x[1]=='Reference');pos=get(n,'at')
   for pad in n:
    if isinstance(pad,list) and str(pad[0])=='pad' and str(pad[2])=='np_thru_hole':holes.append((str(get(n,'uuid')[1]),s.dumps(pos),s.dumps(get(pad,'at')),s.dumps(get(pad,'drill'))))
   if ref.startswith('SW') and not ref.startswith('SWP'):switches.append((ref,s.dumps(pos)))
 return dict(edges=sorted(edges),holes=sorted(holes),switches=sorted(switches))
result={}
for side in ['left','right']:
 a=snapshot('hardware/routing-work/original-keyboard/'+side+'/keyboard.kicad_pcb');b=snapshot('hardware/routing-work/'+side+'/keyboard.kicad_pcb');result[side]={k:{'unchanged':a[k]==b[k],'count':len(a[k])} for k in a}
print(json.dumps(result,indent=2));pathlib.Path('hardware/routing-work/mechanical-verification.json').write_text(json.dumps(result,indent=2))
