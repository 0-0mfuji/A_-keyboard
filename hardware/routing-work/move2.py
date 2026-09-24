import pcbnew as p,sys
s=sys.argv[1];n='1' if s=='left' else '2';path='hardware/routing-work/'+s+'/keyboard.kicad_pcb';b=p.LoadBoard(path);fs={f.GetReference():f for f in b.GetFootprints()}
pos={'left':{'U_LS1':(139,34.2),'C_LS1':(138.5,31.1),'R_RGB_DATA1':(138.5,37.5)},'right':{'U_RGB2':(186.5,36.5),'L_RGB2':(186.5,33.3),'C_RGB_IN2':(189.5,36.5),'U_LS2':(187.5,26),'C_LS2':(187.5,23),'R_RGB_DATA2':(190.5,26),'J2':(181.8,26.5)}}
for r,(x,y) in pos[s].items():fs[r].SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
p.SaveBoard(path,b)
print(s,'moved')
