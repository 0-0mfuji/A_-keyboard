import json, shutil, sys
import pcbnew

src, drc, out = sys.argv[1:]
shutil.copy2(src, out)
board = pcbnew.LoadBoard(out)
data = json.load(open(drc))
remove = set()
for v in data.get('violations', []):
    if v.get('severity') == 'error':
        for item in v.get('items', []):
            if item.get('uuid'):
                remove.add(item['uuid'])
removed = []
for item in list(board.GetTracks()):
    uid = item.m_Uuid.AsString()
    if uid in remove:
        removed.append((uid, item.GetNetname(), type(item).__name__))
        board.Remove(item)
board.Save(out)
print('removed', len(removed))
for row in removed: print(*row)
