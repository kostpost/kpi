import tkinter as tk
import numpy as np
import math

WIDTH, HEIGHT = 1000, 700
CX, CY = WIDTH // 2, HEIGHT // 2
steps_per_phase = 120      
trail_length = 300         

vertices = np.array([
    [-150, -80],
    [ 150, -80],
    [ 220,  80],
    [ -20,  80]
]).T

def to_homogeneous(pts):
    return np.vstack([pts, np.ones(pts.shape[1])])

def from_homogeneous(pts):
    return pts[:2] / pts[2]

trails = [[], [], [], []]

root = tk.Tk()
root.title("Паралелограм: переміщення – обертання – обертання")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111122")
canvas.pack()

phase = 0    
step = 0

def update():
    global phase, step, vertices
    canvas.delete("all")

    if phase == 0:                                      
        t = step / steps_per_phase
        dx = 200 * math.sin(t * math.pi * 2)
        dy = 100 * math.sin(t * math.pi * 4)
        T = np.array([[1, 0, dx],
                      [0, 1, dy],
                      [0, 0,  1]])

    elif phase == 1:                                    # за годинниковою
        angle = math.radians(step / steps_per_phase * 360)
        c, s = math.cos(angle), math.sin(angle)
        T = np.array([[ c, -s, 0],
                      [ s,  c, 0],
                      [ 0,  0, 1]])

    else:                                               # проти годинникової
        angle = math.radians(-step / steps_per_phase * 360)
        c, s = math.cos(angle), math.sin(angle)
        T = np.array([[ c, -s, 0],
                      [ s,  c, 0],
                      [ 0,  0, 1]])

    # застосування перетворення
    homo = to_homogeneous(vertices)
    new_homo = T @ homo
    new_2d = from_homogeneous(new_homo)

    # запис у траєкторії та малювання
    colors = ['#ff0066', '#00ffcc', '#ffff33', '#ff6600']
    for i in range(4):
        x = new_2d[0, i] + CX
        y = new_2d[1, i] + CY
        trails[i].append((x, y))
        if len(trails[i]) > trail_length:
            trails[i].pop(0)
        if len(trails[i]) > 1:
            canvas.create_line(trails[i], fill=colors[i], width=2)

    # Малювання паралелограма та вершин
    points = [ (new_2d[0,i]+CX, new_2d[1,i]+CY) for i in range(4) ]
    flat = [coord for p in points for coord in p]
    canvas.create_polygon(flat, fill='#3388ff', outline='white', width=3)
    for i, (x, y) in enumerate(points):
        canvas.create_oval(x-6, y-6, x+6, y+6, fill=colors[i])

    # до наступного кроку / фази
    step += 1
    if step >= steps_per_phase:
        step = 0
        phase = (phase + 1) % 3

    root.after(30, update)

update()
root.mainloop()