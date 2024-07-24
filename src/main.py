from helper import *
from matrix import *
import numpy as np
import pygame as py
from renderer import *
from stl import mesh
from time import time


def main(stl_paths: list[str]) -> None:
    # Pull data to RAM
    stl_meshes = []
    for path in stl_paths:
        stl_meshes.append(FullMesh(mesh.Mesh.from_file(path)))

    # Finish populating the list of objects
    for stl_mesh in stl_meshes:
        # Adjust points to 4D
        w_to_append = np.ones((stl_mesh.mesh.vectors.shape[0], 3, 1))
        stl_mesh.points_4d = np.concatenate((stl_mesh.mesh.vectors, w_to_append), axis=2)

        w_to_append = np.ones((stl_mesh.mesh.vectors.shape[0], 1))
        stl_mesh.normals_4d = np.concatenate((stl_mesh.mesh.normals / np.max(stl_mesh.mesh.normals), w_to_append), axis=1)

        # Calculate the centroid translation matrices of the shape
        centroid_3d = np.mean(stl_mesh.mesh.centroids, axis = 0)
        stl_mesh.remove_centroid = np.array([
                [1, 0, 0, -centroid_3d[0]],
                [0, 1, 0, -centroid_3d[1]],
                [0, 0, 1, -centroid_3d[2]],
                [0, 0, 0, 1]
            ])
        stl_mesh.add_centroid = np.array([
                [1, 0, 0, centroid_3d[0]],
                [0, 1, 0, centroid_3d[1]],
                [0, 0, 1, centroid_3d[2]],
                [0, 0, 0, 1]
            ])

    # Start pygame
    py.init()
    
    # Window size
    width  = 800
    height = 750

    # Screen creation - Shows up and then the program ends
    canvas = py.display.set_mode((width, height))  
    canvas_color = np.array([57, 3, 66], dtype=np.uint8)

    # Boxes dimensions
    ORTHO_BOX_DIMENSIONS = np.array([3, 3, 3], dtype=np.float32)
    Z_FAR  = np.float32(100)

    # Camera
    FOV          = np.float32(np.pi / 5)
    delta_FOV    = np.float32(np.pi / 36)
    min_FOV      = np.float32(np.pi / 8)
    max_FOV      = np.float32(np.pi / 2)
    camera_pos   = np.array([0, 0, -5, 0], dtype=np.float32)
    camera_speed = np.array([5, 5, 5, 0], dtype=np.float32)

    # Light source
    #                                        x  y  z 
    light_direction = normalize_1d(np.array([1, 0, 0], dtype=np.float32))

    # Angular definition
    angular_position = np.float32(0)
    angular_speed    = np.float32(10)    # Degrees/second

    # Define Transformation matrices
    ortho_to_screen = define_ortho_to_screen_matrix(
            ORTHO_BOX_DIMENSIONS, 
            np.array([py.display.Info().current_w, py.display.Info().current_h, 100, 1], dtype=np.uint16),
            camera_pos
        )
    persp_to_screen = define_persp_to_screen_matrix(
            np.array([py.display.Info().current_w, py.display.Info().current_h, 100, 1], dtype=np.uint16),
            FOV,
            Z_FAR,
            camera_pos
        )
    rotation = define_rotation_matrix()

    # Define Rendering matrices
    depth_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h), np.inf, dtype=np.float32)
    pixel_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h, 3), canvas_color, dtype=np.float32)

    # Configs
    ROTATE_ON_CENTROID = True
    PROJECTION         = Projection.PERSP
    RENDER             = RenderType.FILL
    last_input        = time()
    min_toggle_delta   = 2                  # In seconds
    game_start_time    = time()

    # Render data
    rendered_tris_count = 0
    font = py.font.SysFont(None, 24)

    # Game loop
    running = True  # If the program should be running or not - Used to close it
    clock   = py.time.Clock()
    while running:  
        # Setting max fps
        clock.tick(500)  
        fps = clock.get_fps()

        # Showing some info in the game's caption
        py.display.set_caption(
            f"Tri count: {sum([m.mesh.points.shape[0] for m in stl_meshes])}. Rendered: {int(rendered_tris_count)}. FPS: {int(fps)}"
        )  
        rendered_tris_count = 0

        # Filling the canvas one color
        canvas.fill(canvas_color)  

        # Set projection type
        match PROJECTION:
            case Projection.ORTHO: projection = ortho_to_screen
            case Projection.PERSP: projection = persp_to_screen
                                                
        # Rendering
        for stl_mesh in stl_meshes:
            # Define rotation matrix
            angular_position = (angular_speed * (time() - game_start_time)) % 360
            rotation_basic   = define_rotation_matrix(180, angular_position, angular_position)
            if ROTATE_ON_CENTROID:
                rotation = stl_mesh.add_centroid @ rotation_basic @ stl_mesh.remove_centroid
            else:
                rotation = rotation_basic

            # Define final projection matrix
            projection = projection @ rotation

            # Deal with the triangles of the current mesh
            for i, tri in enumerate(stl_mesh.points_4d): 
                (A, B, C) = tri
                
                # Apply transformations       
                screen_space_verts = [
                    projection @ A,                  
                    projection @ B, 
                    projection @ C
                ]

                # Divide by z if possible
                for p in range(3):
                    if screen_space_verts[p][3] != 0:
                        screen_space_verts[p] /= screen_space_verts[p][3]

                # Ignore triangles that point away from the screen
                edge0 = (screen_space_verts[1] - screen_space_verts[0])[:3]
                edge1 = (screen_space_verts[2] - screen_space_verts[0])[:3]
                z_cross = get_z_cross(edge0, edge1)
                if z_cross >= 0: continue

                # Define shading
                shade = get_face_color(edge0, edge1, light_direction)         
                tri_color = np.array((shade, shade, shade))
                if RENDER == RenderType.FILL:
                    fill_triangle(
                        pixel_buffer,
                        tri_color,
                        screen_space_verts,
                        depth_buffer
                    )

                elif RENDER == RenderType.WIRE:
                    py.draw.polygon(
                        canvas, 
                        np.array([255, 255, 255], dtype=np.uint8), 
                        [screen_space_verts[0][:2], screen_space_verts[1][:2], screen_space_verts[2][:2]], 
                        1
                    )

                rendered_tris_count += 1

        # Blit to canvas
        if RENDER == RenderType.FILL:
            py.surfarray.blit_array(canvas, pixel_buffer)

        # Overlaying instructions
        render_overlay(canvas, font, PROJECTION, RENDER, FOV)

        # Reset render matrices
        depth_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h), np.inf, dtype=np.float32)
        pixel_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h, 3), canvas_color, dtype=np.float32)

        # Updating the canvas
        py.display.flip() 

        # Handle events happening in game
        for event in py.event.get():
            if event.type == py.QUIT: 
                running = False
            
        # Check last input time
        if (time() - last_input) < min_toggle_delta:
            continue

        # Get the state of all keyboard buttons
        keys = py.key.get_pressed()

        # Toggle transformation type
        if keys[py.K_p]: 
            if   PROJECTION == Projection.ORTHO: PROJECTION = Projection.PERSP
            elif PROJECTION == Projection.PERSP: PROJECTION = Projection.ORTHO
            last_input = time()

        # Toggle render type
        if keys[py.K_r]: 
            if   RENDER == RenderType.FILL: RENDER = RenderType.WIRE
            elif RENDER == RenderType.WIRE: RENDER = RenderType.FILL
            last_input = time()

        # Change FOV
        if keys[py.K_EQUALS]:                 
            FOV = min(FOV + delta_FOV, max_FOV)

            # Recalculate the perspective tranform
            persp_to_screen = define_persp_to_screen_matrix(
                    np.array([py.display.Info().current_w, py.display.Info().current_h, 100, 1], dtype=np.uint16),
                    FOV,
                    Z_FAR,
                    camera_pos
                )

            last_input = time()

        if keys[py.K_MINUS]:  
            FOV = max(FOV - delta_FOV, min_FOV)

            # Recalculate the perspective tranform
            persp_to_screen = define_persp_to_screen_matrix(
                    np.array([py.display.Info().current_w, py.display.Info().current_h, 100, 1], dtype=np.uint16),
                    FOV,
                    Z_FAR,
                    camera_pos
                )

            last_input = time()



if __name__ == '__main__':
    main(["STL/monka.stl"])