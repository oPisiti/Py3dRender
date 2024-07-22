from numba import jit
import numpy as np
import pygame as py

# @jit()
def fill_triangle(
        pixel_buffer: np.array, 
        color:        np.array, 
        tri:          list[np.array],
        depth:        np.array 
        ) -> None:
    
    ordered_points = sorted(tri, key=lambda t: t[1])
    (A, B, C) = ordered_points

    deltas = np.array([
        [ # AB
            (B[0] - A[0]) / (B[1] - A[1]) if B[1] != A[1] else 0,
            1,
            (B[2] - A[2]) / (B[1] - A[1]) if B[1] != A[1] else 0,
            0
        ],
        [  # BC
            (C[0] - B[0]) / (C[1] - B[1]) if C[1] != B[1] else 0,
            1,
            (C[2] - B[2]) / (C[1] - B[1]) if C[1] != B[1] else 0,
            0
        ],
        [  # AC
            (C[0] - A[0]) / (C[1] - A[1]) if A[1] != C[1] else 0,
            1,
            (C[2] - A[2]) / (C[1] - A[1]) if A[1] != C[1] else 0,
            0
        ]
    ], dtype=np.float32)


    # if int(B[1]) - int(A[1]) > 1:
    # Edges
    point1, point2 = ordered_points[0].copy(), ordered_points[0].copy()

    # Top half
    while point1[1] <= ordered_points[1][1]:
        point1 += deltas[0]
        point2 += deltas[2]

        # Make sure the two points don't have the same x value
        if int(point1[0]) == int(point2[0]): continue

        # Make sure the left point is assigned left
        if point1[0] <= point2[0]: left, right = point1, point2
        else:                      left, right = point2, point1

        # y is out of bounds
        if left[1] < 0: continue
        if left[1] >= pixel_buffer.shape[1]: break

        # Fill the line
        _fill_line(left, right, pixel_buffer, depth, color)

    # There is no bottom half
    if B[0] == C[0]: return

    # Edges
    point1, point2 = ordered_points[2].copy(), ordered_points[2].copy()

    # Bottom half
    while point1[1] >= ordered_points[1][1]:
        point1 -= deltas[1]
        point2 -= deltas[2]

        # Make sure the two points don't have the same x value
        if point1[0] == point2[0]: continue

        # Make sure the left point is assigned left
        if point1[0] <= point2[0]: left, right = point1, point2
        else:                      left, right = point2, point1

        # y is out of bounds
        if left[1] >= pixel_buffer.shape[1]: continue
        if left[1] < 0: break

        # Fill the line
        _fill_line(left, right, pixel_buffer, depth, color)


@jit(parallel=True)
def _fill_line(
        left, 
        right, 
        pixel_buffer, 
        depth, 
        color
        ) -> None:

    x, y, z = max(np.int32(left[0]), 0), np.int32(left[1]), left[2]
    delta_z = (right[2] - left[2]) / (right[0] - left[0])
    while x <= min(right[0], pixel_buffer.shape[0]):
        # Check the z value
        if z < depth[x][y]:
            depth[x][y] = z
            pixel_buffer[x][y] = color

        x += 1
        z += delta_z
    


def render_triangle(
        pixel_buffer: np.array, 
        color:        np.array, 
        tri:          list[np.array],
        ) -> None:

    sorted_tris = sorted(tri, key=lambda t: t[1])
    (A, B, C) = sorted_tris

    deltas = np.array([
        np.float32((B[0] - A[0]) / (B[1] - A[1]) if B[1] != A[1] else 0),
        np.float32((C[0] - B[0]) / (C[1] - B[1]) if C[1] != B[1] else 0),
        np.float32((A[0] - C[0]) / (A[1] - C[1]) if A[1] != C[1] else 0)
    ])

    for i, y in enumerate((np.int32(A[1]), np.int32(B[1]), np.int32(C[1]))):
        x = sorted_tris[i][0]

        # Render each line
        while y < sorted_tris[(i+1)%3][1]:
            x_int16 = np.int16(x)

            # Out of bounds
            if x_int16 < 0 or x_int16 >= pixel_buffer.shape[0] or \
               y < 0 or y >= pixel_buffer.shape[1]:
                break

            pixel_buffer[x_int16][y] = color

            x += deltas[i]
            y += 1
