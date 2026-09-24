import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from matplotlib.transforms import Affine2D
for s in ['left','right']:
 d=json.load(open('hardware/routing-work/'+s+'-geometry.json'));fig,ax=plt.subplots(figsize=(13,10))
 for g in d['edges']:ax.plot(*zip(g['start'],g['end']),color='black',linewidth=.7)
 for f in d['footprints']:
  for a in f['pads']:
   x,y=a['pos'];w,h=a['size'];c='red' if f['layer']=='F.Cu' else 'blue'
   r=Rectangle((x-w/2,y-h/2),w,h,fc=c,alpha=.5);r.set_transform(Affine2D().rotate_deg_around(x,y,-a['angle'])+ax.transData);ax.add_patch(r)
   if a['drill'][0]:ax.add_patch(Circle((x,y),a['drill'][0]/2,fc='white',ec='black',lw=.3))
  ax.text(*f['pos'],f['ref'],fontsize=5)
 ax.set_aspect('equal');ax.invert_yaxis();ax.set_xlim((15,165) if s=='left' else (165,315));ax.set_ylim(135,-5);ax.grid(alpha=.2);fig.savefig('hardware/routing-work/'+s+'-placement.png',dpi=160);plt.close(fig)
