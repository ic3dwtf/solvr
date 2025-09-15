from PIL import ImageGrab, ImageDraw, Image, ImageTk
from itertools import combinations
import tkinter as tk
import os

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
    draw = ImageDraw.Draw(crop)

    #for i in range(grid+1):
        #draw.line([(i*cellsz,0),(i*cellsz,ch)], fill="red")
        #draw.line([(0,i*cellsz),(cw,i*cellsz)], fill="red")

    def get_state(cx,cy):
        c = crop.getpixel((cx+px, cy+(cellsz-1-py)))
        c9 = crop.getpixel((cx+9, cy+(cellsz-1-3)))
        if c==(163,163,163): return "U"
        if c==(162,162,162): return "F"
        if c==(188,188,188) and c9!=(35,35,139): return "E"
        if c==(41,41,241): return "1"
        if c==(0,102,0): return "2"
        if c==(251,10,10): return "3"
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
            #draw.text((x*cellsz+4,y*cellsz+2), state, fill="yellow")
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
            if 1<=len(cells)<=8:
                sols=[]
                for mines in combinations(cells,n):
                    sols.append(set(mines))
                if not sols: continue
                common_mines=set.intersection(*sols)
                for x,y in common_mines: changed|=mark_cell(x,y,"F","red")

root = tk.Tk()
root.title("solvr [ic3dwtf]")
root.configure(bg="#2e2e2e")
root.attributes('-topmost', True)

canvas = tk.Canvas(root, width=480, height=480, bg="#2e2e2e", highlightthickness=0)
canvas.pack(padx=10, pady=10)

img = capture_board()
tk_img = ImageTk.PhotoImage(img)
img_id = canvas.create_image(0,0, anchor='nw', image=tk_img)

def update_loop():
    capture_board()
    solve_board()
    tk_img2 = ImageTk.PhotoImage(crop)
    canvas.itemconfig(img_id, image=tk_img2)
    canvas.image = tk_img2
    root.after(200, update_loop)

update_loop()

root.mainloop()
