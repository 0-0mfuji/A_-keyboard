import pcbnew, shutil, sys, json

src, drc_path, out = sys.argv[1:]
shutil.copy2(src, out)
b = pcbnew.LoadBoard(out)
mm = pcbnew.FromMM
V = pcbnew.VECTOR2I
F = pcbnew.F_Cu
B = pcbnew.B_Cu

def pos(x, y):
    return V(mm(x), mm(y))

def add_track(net_name, layer, points, width=0.20):
    net = b.FindNet(net_name)
    for a, z in zip(points, points[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pos(*a)); t.SetEnd(pos(*z)); t.SetLayer(layer)
        t.SetWidth(mm(width)); t.SetNet(net); b.Add(t)

def add_via(net_name, x, y, diameter=0.60, drill=0.30):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pos(x, y)); v.SetNet(b.FindNet(net_name))
    v.SetWidth(mm(diameter)); v.SetDrill(mm(drill))
    b.Add(v)

# Remove the known local shorts/crossings from the last checkpoint.
bad = set()
for v in json.load(open(drc_path)).get('violations', []):
    if v.get('severity') == 'error':
        bad.update(i.get('uuid') for i in v.get('items', []) if i.get('uuid'))
for item in list(b.GetTracks()):
    if item.m_Uuid.AsString() in bad:
        b.Remove(item)

# RGB_SW: route above the LED driver on the back layer.
add_via('/power/RGB_SW_LEFT', 151.0, 4.0)
add_via('/power/RGB_SW_LEFT', 145.0, 8.8)
add_track('/power/RGB_SW_LEFT', F, [(151.0, 4.0), (149.8, 4.0)])
add_track('/power/RGB_SW_LEFT', B, [(149.8, 4.0), (149.8, 2.8), (145.0, 2.8), (145.0, 8.8)])
add_track('/power/RGB_SW_LEFT', F, [(145.0, 8.8), (146.2875, 9.0)])

# VBAT: join the local LED/input branch to U1 pad 28 using a back-layer riser.
add_via('/VBAT_LEFT', 147.7125, 9.5)
add_track('/VBAT_LEFT', B, [(147.7125, 9.5), (148.6, 10.5), (148.6, 20.5), (147.619, 21.677), (147.619, 17.125)])

# GND: join the input capacitor and RGB LED ground to the existing U1 ground trunk.
add_track('/GND_LEFT', F, [(144.5, 8.25), (145.5, 8.25), (146.2875, 9.5)])
add_via('/GND_LEFT', 146.2875, 9.5)
add_via('/GND_LEFT', 146.2875, 13.5)
add_track('/GND_LEFT', B, [(146.2875, 9.5), (146.2875, 13.5)])
add_track('/GND_LEFT', F, [(146.2875, 13.5), (146.2875, 15.0), (146.989, 15.597)])

# RGB_EN: connect the XIAO side to the already routed pull-down/LED branch along the outer edge.
add_via('/RGB_EN_LEFT', 145.024, 19.51)
add_track('/RGB_EN_LEFT', B, [(145.024, 19.51), (158.5, 19.51), (158.5, 8.0), (150.5, 9.0)])

# RGB_5V: bring the local LED branch to the existing long trunk using the left side of the module.
add_via('/RGB_5V_LEFT', 146.2875, 8.5)
add_track('/RGB_5V_LEFT', B, [(146.2875, 8.5), (144.0, 7.0), (140.0, 7.0), (136.5, 10.5), (136.5, 24.5), (137.649, 26.313)])
# Connect the output capacitor pair to the same trunk on the outer edge.
add_via('/RGB_5V_LEFT', 153.0, 12.25)
add_track('/RGB_5V_LEFT', B, [(153.0, 12.25), (158.5, 14.0), (158.5, 33.5), (154.704, 35.49)])

# RGB_DATA_SHIFTED: close the remaining short local gap on the back layer.
add_via('/RGB_DATA_SHIFTED_LEFT', 135.636, 38.641)
add_via('/RGB_DATA_SHIFTED_LEFT', 132.026, 35.032)
add_track('/RGB_DATA_SHIFTED_LEFT', B, [(135.636, 38.641), (133.0, 38.641), (132.026, 35.032)])

# RGB_SHIFTED: the existing via is 0.05 mm from the U_LS pad.
add_track('/power/RGB_SHIFTED_LEFT', F, [(140.1, 35.1), (140.1375, 35.15)])

b.Save(out)
print(out)
