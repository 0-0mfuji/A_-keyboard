import sys, pcbnew

board_path, ses_path, out_path = sys.argv[1:]
board = pcbnew.LoadBoard(board_path)
ok = pcbnew.ImportSpecctraSES(board, ses_path)
print('import', ses_path, ok)
board.Save(out_path)
