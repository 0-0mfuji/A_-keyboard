import sexpdata as s,pathlib,uuid
S=s.Symbol
get=lambda n,k:next((x for x in n if isinstance(x,list) and str(x[0])==k),None)
for side in ['left','right']:
 p=pathlib.Path('hardware/routing-work')/side/'keyboard.kicad_pcb';a=s.loads(p.read_text())
 for f in a:
  if not isinstance(f,list) or str(f[0])!='footprint':continue
  ref=next(n[2] for n in f if isinstance(n,list) and str(n[0])=='property' and n[1]=='Reference')
  # Socket drawings include thick filled art crossing solder lands: preserve on assembly layer.
  if ref.startswith('SW') and not ref.startswith('SWP'):
   for n in f:
    if isinstance(n,list) and str(n[0]).startswith('fp_'):
     l=get(n,'layer')
     if l and 'SilkS' in str(l[1]):l[1]=l[1].replace('SilkS','Fab')
  if ref.startswith('LED'):
   for n in f:
    if isinstance(n,list) and str(n[0])=='fp_text':
     l=get(n,'layer')
     if l and 'SilkS' in str(l[1]):l[1]=l[1].replace('SilkS','Fab')
 p.write_text(s.dumps(a))
p=pathlib.Path('hardware/routing-work/right/power.kicad_sch');a=s.loads(p.read_text())
for n in a:
 if isinstance(n,list) and get(n,'uuid') and str(get(n,'uuid')[1])=='dba11978-c87d-5730-a9f8-5afe6af708ec':get(n,'pts')[2][1]=114.3
p.write_text(s.dumps(a))
