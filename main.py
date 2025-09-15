from PIL import ImageGrab, ImageDraw
from itertools import combinations
from tkinter import messagebox
import tkinter as tk
import requests
import sys
import os

version = open("version.txt").read().strip()

sys.setrecursionlimit(10**6)

root = tk.Tk()
root.title(f"solvr [ic3dwtf] [v.{version}]")
root.configure(bg="#2e2e2e")
root.attributes('-topmost', True)
root.resizable(False, False)
root.geometry("300x0")
root.iconbitmap("icon.ico")

def check_version():
    try:
        r = requests.get("https://raw.githubusercontent.com/ic3dwtf/solvr/refs/heads/main/version.txt")
        if r.status_code == 200:
            latest = r.text.strip()
            if latest != version:
                messagebox.showwarning("wrong version!", f"your version is {version}, latest is {latest}\nupdate at github.com/ic3dwtf/solvr")
        else:
            messagebox.showerror("version check failed", "could not fetch version info")
    except Exception as e:
        tk.messagebox.showerror("version check error", str(e))

check_version()

size = 480
ox, oy = 0, 17
cellsz, grid = 16, 30
px, py = 8, 3

board = []
crop = None
path = os.path.abspath("images/grid.png")
os.makedirs("images", exist_ok=True)

def capture_board():
    global crop, board
    img = ImageGrab.grab()
    w, h = img.size
    cw, ch = 480, 480
    l, t = (w - cw)//2 + ox, (h - ch)//2 + oy
    r, b = l + cw, t + ch
    crop = img.crop((l, t, r, b))

    def get_state(cx,cy):
        c = crop.getpixel((cx+px, cy+(cellsz-1-py)))
        c9 = crop.getpixel((cx+9, cy+(cellsz-1-3)))
        if c==(163,163,163): return "U"
        if c==(162,162,162) or c==(162,150,93): return "F"
        if c==(188,188,188) and c9!=(35,35,139): return "E"
        if c==(41,41,241) or c==(47,42,227): return "1"
        if c==(0,102,0): return "2"
        if c==(251,10,10) or c==(253,11,7): return "3"
        if c9==(35,35,139): return "4"
        if c==(130,7,7): return "5"
        if c==(7,130,130): return "6"
        return "X"

    board = []
    for y in range(grid):
        row=[]
        for x in range(grid):
            state=get_state(x*cellsz,y*cellsz)
            row.append(state)
        board.append(row)

    crop.save(path, "PNG")
    return crop

def get_neighbors(x,y):
    return [(x+dx,y+dy) for dy in [-1,0,1] for dx in [-1,0,1] if not(dx==0 and dy==0) and 0<=x+dx<grid and 0<=y+dy<grid]

def mark_cell(x,y,state,color):
    if board[y][x]!=state:
        board[y][x]=state
        draw = ImageDraw.Draw(crop)
        draw.text((x*cellsz+4,y*cellsz+2),state,fill=color)
        return True
    return False

def solve_board():
    changed=True
    
    while changed:
        changed=False
        constraints=[]
        for y in range(grid):
            for x in range(grid):
                c=board[y][x]
                if c in "123456":
                    n=int(c)
                    nbs=get_neighbors(x,y)
                    unknowns=[(nx,ny) for nx,ny in nbs if board[ny][nx]=="U"]
                    flags=sum(1 for nx,ny in nbs if board[ny][nx]=="F")
                    if unknowns:
                        constraints.append((set(unknowns), n-flags))
                        if n-flags==len(unknowns):
                            for ux,uy in unknowns: changed|=mark_cell(ux,uy,"F","red")
                        if n-flags==0:
                            for ux,uy in unknowns: changed|=mark_cell(ux,uy,"S","green")

        for i,(cells1,n1) in enumerate(constraints):
            for j,(cells2,n2) in enumerate(constraints):
                if i>=j: continue
                inter=cells1 & cells2
                if not inter: continue
                diff1=cells1-cells2
                diff2=cells2-cells1
                if diff1 and n1-n2==len(diff1):
                    for x,y in diff1: changed|=mark_cell(x,y,"F","red")
                if diff2 and n2-n1==len(diff2):
                    for x,y in diff2: changed|=mark_cell(x,y,"F","red")

        for cells,n in constraints:
            if 1 <= len(cells) <= 20:
                if n < 0 or n > len(cells):
                    continue
                sols=[]
                for mines in combinations(cells,n):
                    sols.append(set(mines))
                if not sols: continue
                common_mines=set.intersection(*sols)
                for x,y in common_mines: changed|=mark_cell(x,y,"F","red")

overlay = tk.Toplevel()
overlay.overrideredirect(True)
overlay.attributes("-topmost", True)
overlay.attributes("-transparentcolor", "white")
overlay.config(bg="white")

screen_w = overlay.winfo_screenwidth()
screen_h = overlay.winfo_screenheight()
cw, ch = 480, 480 
x_pos = (screen_w - cw)//2 + ox
y_pos = (screen_h - ch)//2 + oy
overlay.geometry(f"{cw}x{ch}+{x_pos}+{y_pos}")

overlay_canvas = tk.Canvas(overlay, width=cw, height=ch, bg="white", highlightthickness=0)
overlay_canvas.pack()

def update_overlay():
    overlay_canvas.delete("all")
    for y in range(grid):
        for x in range(grid):
            c = board[y][x]
            x1, y1 = x*cellsz+1, y*cellsz+1
            x2, y2 = (x+1)*cellsz-1, (y+1)*cellsz-1
            if c=="F":
                overlay_canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=1)
            elif c=="S":
                overlay_canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="light green", width=1)
    overlay_canvas.update()

def update_loop():
    capture_board()
    solve_board()
    update_overlay()
    root.after(200, update_loop)

update_loop()
root.mainloop()