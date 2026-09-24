import sys, pcbnew

board_path, dsn_path = sys.argv[1:]
board = pcbnew.LoadBoard(board_path)
if not pcbnew.ExportSpecctraDSN(board, dsn_path):
    raise SystemExit('Specctra export failed')
print(dsn_path)
