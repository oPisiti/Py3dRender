from math import sin, cos, pi, inf
import numpy as np
import pygame as py
from renderer import *
from stl import mesh


class vf3d:
    def __init__(self, values: list[float]) -> None:
        self.x = values[0]
        self.y = values[1]
        self.z = values[2]


class Globals:
    ORTHO_BOX_DIMENSIONS = vf3d([150, 150, 100])
    Z_NEAR               = 50


class FullMesh:
    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.points_4d = None
        self.centroid_4d = None
        self.normals_4d = None


def define_ortho_to_screen_matrix() -> np.array:
    w = py.display.Info().current_w
    h = py.display.Info().current_h
    return np.array([
        [w/(Globals.ORTHO_BOX_DIMENSIONS.x), 0, 0, 0],
        [0, h/(Globals.ORTHO_BOX_DIMENSIONS.y), 0, 0],
        [0, 0, w/(Globals.ORTHO_BOX_DIMENSIONS.z), 0],
        [0, 0, 0, 1]   
    ])


def define_rotation_matrix(yaw_degrees: float = 0, pitch_degrees: float = 0, roll_degrees: float = 0) -> np.array:
    alpha_rad = yaw_degrees   * pi / 180
    beta_rad  = pitch_degrees * pi / 180
    gamma_rad = roll_degrees  * pi / 180

    yaw = np.array([
        [cos(alpha_rad), -sin(alpha_rad), 0, 0],
        [sin(alpha_rad), cos(alpha_rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    pitch = np.array([
        [cos(beta_rad), 0, sin(beta_rad), 0],
        [0, 1, 0, 0],
        [-sin(beta_rad), 0, cos(beta_rad), 0],
        [0, 0, 0, 1],
    ])

    roll = np.array([
        [1, 0, 0, 0],
        [0, cos(gamma_rad), -sin(gamma_rad), 0],
        [0, sin(gamma_rad), cos(gamma_rad), 0],
        [0, 0, 0, 1]
    ])

    return yaw @ pitch @ roll


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

        # Calculate the centroid of the shape
        centroid_3d = np.mean(stl_mesh.mesh.centroids, axis = 0)
        stl_mesh.centroid_4d = np.array([centroid_3d[0], centroid_3d[1], centroid_3d[2], 0])

    # Start pygame
    py.init()
    width  = 800
    height = 800

    # Screen creation - Shows up and then the program ends
    canvas = py.display.set_mode(       
        (width, height), py.RESIZABLE
    )  

    canvas_color = (57, 3, 66)

    # Camera
    camera_pos   = np.array([-50, -50, 0, 0])
    camera_speed = vf3d([5, 5, 5])

    # Light source - Make it a normal vector pls, thanks
    # the w value only exists for multiplication purposes. Just set it to 0
    #                           x  y  z  w
    light_direction = np.array([0, 0, 1, 0])

    # Angles
    angular_position = 0
    angular_speed    = 15    # Degrees/second

    # Define Transformation matrices
    ortho_to_screen = define_ortho_to_screen_matrix()
    rotation        = define_rotation_matrix()

    # Define Rendering matrices
    pixels_depth = np.full((py.display.Info().current_w, py.display.Info().current_h), inf)

    # Game loop
    running = True  # If the program should be running or not - Used to close it
    clock   = py.time.Clock()
    while running:  
        # Setting max fps to 120
        clock.tick(500)  
        fps = clock.get_fps()

        # Showing the fps in the game title
        py.display.set_caption(
            f"Success FPS:{int(fps)}"
        )  

        # Filling the canvas one color
        canvas.fill(canvas_color)  

        # Update angular position matrix
        angular_position += (angular_speed * (1/fps if fps != 0 else 0)) % 2*pi
        rotation          = define_rotation_matrix(45, angular_position, angular_position)
                                                             
        # Rendering
        for stl_mesh in stl_meshes:
            for i, tri in enumerate(stl_mesh.points_4d):
                # TODO: Make nicer   
                # Apply translations       
                screen_space_tris = [
                    ortho_to_screen @ (rotation @ (tri[0] - stl_mesh.centroid_4d) + stl_mesh.centroid_4d - camera_pos),                  
                    ortho_to_screen @ (rotation @ (tri[1] - stl_mesh.centroid_4d) + stl_mesh.centroid_4d - camera_pos), 
                    ortho_to_screen @ (rotation @ (tri[2] - stl_mesh.centroid_4d) + stl_mesh.centroid_4d - camera_pos)
                ]

                # Ignore triangles that point away from the screen
                rotated_normal = rotation @ stl_mesh.normals_4d[i]
                if rotated_normal[2] >= 0: continue

                # Define shading
                intensity = int(-180 * np.dot(light_direction, rotated_normal)) + 25

                render_triangle(
                    canvas,
                    # (i, (i * 5) % 256, (i * 7) % 256),
                    (intensity, intensity, intensity),
                    [screen_space_tris[0][:2], screen_space_tris[1][:2], screen_space_tris[2][:2]],
                    pixels_depth
                )
                py.draw.polygon(
                    canvas, 
                    (255, 255, 255), 
                    [screen_space_tris[0][:2], screen_space_tris[1][:2], screen_space_tris[2][:2]], 
                    1
                )

        # Updating the canvas
        py.display.update() 

        # py.event.get() contains all events happening in a game
        for (event) in py.event.get():
            if event.type == py.QUIT: 
                running = False

            # Get the state of all keyboard buttons
            keys = py.key.get_pressed()

            if keys[py.K_w]: camera_pos.z -= camera_speed.z
            if keys[py.K_a]: camera_pos.x += camera_speed.x
            if keys[py.K_s]: camera_pos.z += camera_speed.z
            if keys[py.K_d]: camera_pos.x -= camera_speed.x

            # Update transform matrix
            if keys[py.K_w] or keys[py.K_a] or keys[py.K_s] or keys[py.K_d]:
                ortho_to_screen = define_ortho_to_screen_matrix(camera_pos)

        # Reset depth matrix
        pixels_depth = np.full((py.display.Info().current_w, py.display.Info().current_h), inf)

if __name__ == '__main__':
    # main("STL/20mm_cube.stl")
    main(["STL/20mm_cube.stl", "STL/dodecahedron.stl"])
    # main("STL/Cube.stl")