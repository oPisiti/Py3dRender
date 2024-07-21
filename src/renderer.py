from math import tan
import numpy as np
import pygame as py


def solve_equation(A: np.array, y: int, m: float) -> float:
    return int(A[0] + m * (y - A[1]))



def render_triangle(
        canvas: py.Surface, 
        color:  np.array, 
        tri:    list[np.array],
        depth:  np.array 
        ) -> None:
    
    ordered_tris = sorted(tri, key=lambda t: t[1])

    # The x inclination of the three lines
    mAB_x = (ordered_tris[1][0] - ordered_tris[0][0]) / (ordered_tris[1][1] - ordered_tris[0][1]) if (ordered_tris[1][1] - ordered_tris[0][1]) != 0 else 0
    mAC_x = (ordered_tris[2][0] - ordered_tris[0][0]) / (ordered_tris[2][1] - ordered_tris[0][1]) if (ordered_tris[2][1] - ordered_tris[0][1]) != 0 else 0
    mBC_x = (ordered_tris[2][0] - ordered_tris[1][0]) / (ordered_tris[2][1] - ordered_tris[1][1]) if (ordered_tris[2][1] - ordered_tris[1][1]) != 0 else 0

    # # The z inclination
    # mAB_z = (ordered_tris[1][0] - ordered_tris[0][0]) / (ordered_tris[1][1] - ordered_tris[0][1]) if (ordered_tris[1][1] - ordered_tris[0][1]) != 0 else 0
    # mAC_z = (ordered_tris[2][0] - ordered_tris[0][0]) / (ordered_tris[2][1] - ordered_tris[0][1]) if (ordered_tris[2][1] - ordered_tris[0][1]) != 0 else 0
    # mBC_z = (ordered_tris[2][0] - ordered_tris[1][0]) / (ordered_tris[2][1] - ordered_tris[1][1]) if (ordered_tris[2][1] - ordered_tris[1][1]) != 0 else 0

    y = int(ordered_tris[0][1])

    # Top half
    while y <= ordered_tris[1][1]:
        xAB = solve_equation(ordered_tris[0], y, mAB_x)
        xAC = solve_equation(ordered_tris[0], y, mAC_x)

        # # Fill horizontal line
        # zAB = solve_equation((ordered_tris[0][2], ordered_tris[0][1]), y, mAB_x)
        # zAC = solve_equation((ordered_tris[0][2], ordered_tris[0][1]), y, mAC_x)
        # if zABdepth[xAB, y]
        py.draw.line(canvas, color, (xAB, y), (xAC, y))

        # for x in range(min(xAB, xAC), max(xAB, xAC)):
        #     # if depth[x, y]
        #     canvas.set_at([x, y], color)
        
        y += 1


    # # Bottom half
    # while y <= ordered_tris[2][1]:
    #     xAC = solve_equation(ordered_tris[0], y, mAC_x)
    #     xBC = solve_equation(ordered_tris[1], y, mBC_x)

    #     # Fill horizontal line
    #     py.draw.line(canvas, color, (xAC, y), (xBC, y))
    #     # for x in range(min(xAB, xBC), max(xAB, xBC)):
    #     #     canvas.set_at([x, y], color)

    #     y += 1
