from matrix import *
import numpy as np
import pygame as py
from renderer import *
from stl import mesh


class FullMesh:
    def __init__(self, mesh) -> None:
        self.mesh = mesh

        self.points_4d  = None
        self.normals_4d = None

        self.remove_centroid = None
        self.add_centroid    = None


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
    width  = 800
    height = 750

    # Screen creation - Shows up and then the program ends
    canvas = py.display.set_mode(       
        (width, height), py.RESIZABLE
    )  

    canvas_color = np.array([57, 3, 66], dtype=np.uint8)

    # Boxes dimensions
    ORTHO_BOX_DIMENSIONS = np.array([150, 150, 100], dtype=np.float32)

    Z_FAR  = np.float32(100)

    # Camera
    FOV          = np.float32(np.pi / 5)
    camera_pos   = np.array([0, 0, -5, 0], dtype=np.float32)
    camera_speed = np.array([5, 5, 5, 0], dtype=np.float32)

    # Light source - Make it a normal vector pls, thanks
    # the w value only exists for multiplication purposes. Just set it to 0
    #                           x  y  z  w
    light_direction = np.array([0, 0, 1, 0], dtype=np.float32)

    # Angles
    angular_position = np.float32(0)
    angular_speed    = np.float32(2)    # Degrees/second

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
    depth_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h), np.inf)
    pixel_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h, 3), canvas_color)

    # Configs
    ROTATE_ON_CENTROID = True
    ORTHO_TRANSFORM    = False

    # Render data
    rendered_tris_count = 0

    # Game loop
    running = True  # If the program should be running or not - Used to close it
    clock   = py.time.Clock()
    while running:  
        # Setting max fps
        clock.tick(500)  
        fps = clock.get_fps()

        # Showing the fps in the game title
        py.display.set_caption(
            f"Tri count: {sum([m.mesh.points.shape[0] for m in stl_meshes])}. Rendered: {int(rendered_tris_count)}. FPS: {int(fps)}"
        )  
        rendered_tris_count = 0

        # Filling the canvas one color
        canvas.fill(canvas_color)  
                                                
        # Rendering
        for stl_mesh in stl_meshes:
            # Define rotation matrix 
            angular_position += (angular_speed * (1/fps if fps != 0 else 0)) % 2*np.pi
            rotation_basic    = define_rotation_matrix(180, angular_position, angular_position)
            # rotation_basic    = define_rotation_matrix(45, angular_position, angular_position)
            if ROTATE_ON_CENTROID:
                rotation = stl_mesh.add_centroid @ rotation_basic @ stl_mesh.remove_centroid
            else:
                rotation = rotation_basic

            # Set transform type
            transform = ortho_to_screen if ORTHO_TRANSFORM else persp_to_screen
            transform = transform @ rotation

            # Deal with current mesh
            for i, tri in enumerate(stl_mesh.points_4d): 
                (A, B, C) = tri
                
                # Apply transformations       
                screen_space_tris = [
                    transform @ A,                  
                    transform @ B, 
                    transform @ C
                ]

                # Divide by z if possible
                for p in range(3):
                    if screen_space_tris[p][3] != 0:
                        screen_space_tris[p] /= screen_space_tris[p][3]

                # Ignore triangles that point away from the screen
                rotated_normal = rotation_basic @ stl_mesh.normals_4d[i]
                if rotated_normal[2] >= 0: continue

                # Define shading
                intensity = np.uint8(-160 * np.dot(light_direction, rotated_normal)) + 50
                tri_color = np.array((intensity, intensity, intensity))                

                fill_triangle(
                    pixel_buffer,
                    tri_color,
                    screen_space_tris,
                    depth_buffer
                )

                # py.draw.polygon(
                #     canvas, 
                #     np.array([255, 255, 255], dtype=np.uint8), 
                #     [screen_space_tris[0][:2], screen_space_tris[1][:2], screen_space_tris[2][:2]], 
                #     1
                # )

                rendered_tris_count += 1

        # Blit to canvas
        py.surfarray.blit_array(canvas, pixel_buffer)
        
        # Updating the canvas
        py.display.flip() 

        # py.event.get() contains all events happening in a game
        for (event) in py.event.get():
            if event.type == py.QUIT: 
                running = False

        #     # Get the state of all keyboard buttons
        #     keys = py.key.get_pressed()

        #     if keys[py.K_w]: camera_pos.z -= camera_speed.z
        #     if keys[py.K_a]: camera_pos.x += camera_speed.x
        #     if keys[py.K_s]: camera_pos.z += camera_speed.z
        #     if keys[py.K_d]: camera_pos.x -= camera_speed.x

        #     # Update transform matrix
        #     if keys[py.K_w] or keys[py.K_a] or keys[py.K_s] or keys[py.K_d]:
        #         ortho_to_screen = define_ortho_to_screen_matrix(camera_pos)

        # Reset render matrices
        depth_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h), np.inf)
        pixel_buffer = np.full((py.display.Info().current_w, py.display.Info().current_h, 3), canvas_color)


if __name__ == '__main__':
    # main(["STL/20mm_cube.stl"])
    # main(["STL/20mm_cube.stl", "STL/dodecahedron.stl"])
    # main(["STL/teapot.stl"])
    # main(["STL/Cruz.stl"])
    main(["STL/monka.stl"])