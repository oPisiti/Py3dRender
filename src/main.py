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
    ORTHO_BOX_DIMENSIONS = vf3d([100, 100, 50])
    ORTHO_Z_NEAR         = 10


def define_ortho_to_screen(camera_pos: vf3d) -> np.array:
    w = py.display.Info().current_w
    h = py.display.Info().current_h
    return np.array([
        [w/(Globals.ORTHO_BOX_DIMENSIONS.x), 0, 0, -camera_pos.x],
        [0, h/(Globals.ORTHO_BOX_DIMENSIONS.y), 0, -camera_pos.y],
        [0, 0, 1/(Globals.ORTHO_BOX_DIMENSIONS.z), -Globals.ORTHO_Z_NEAR],
        [0, 0, 0, 1]   
    ])


def main(stl_path: str) -> None:
    # Pull data to RAM
    stl_mesh = mesh.Mesh.from_file(stl_path)

    # Adjust points to 4D
    w_to_append = np.ones((stl_mesh.vectors.shape[0], 3, 1))
    vectors_4d = np.concatenate((stl_mesh.vectors, w_to_append), axis=2)

    print(stl_mesh.points)

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
    camera_pos   = vf3d([0, 0, 0])
    camera_speed = vf3d([5, 5, 0])

    # Define Transform matrices
    ortho_to_screen = define_ortho_to_screen(camera_pos)

    
    # Game loop
    running = True  # If the program should be running or not - Used to close it
    clock   = py.time.Clock()
    while running:  
        # Setting max fps to 120
        clock.tick(5000)  
        fps = clock.get_fps()

        # Showing the fps in the game title
        py.display.set_caption(
            f"Sucess  N° Points: {stl_mesh.vectors.shape[0]}  FPS:{int(fps)}"
        )  

        # Filling the canvas one color
        canvas.fill(canvas_color)  

        # Rendering
        for tri in vectors_4d:
            # Apply translations         
            # TODO: Make nicer   
            screen_space_tri = [
                ortho_to_screen @ tri[0], 
                ortho_to_screen @ tri[1], 
                ortho_to_screen @ tri[2]
            ]
            py.draw.polygon(canvas, 
            (255, 255, 255), 
            [screen_space_tri[0][:2], screen_space_tri[1][:2], screen_space_tri[2][:2]], 
            1
            )

        # Updating the canvas
        py.display.update() 

        # py.event.get() contains all events happening in a game
        for (event) in py.event.get():
            if event.type == py.QUIT: 
                running = False

            # if event.type == py.MOUSEBUTTONDOWN: 
            #     # --- Zoom --- 
            #     constant = 1.5

            #     # In
            #     if event.button == 4: 
            #         zoom *= constant
            #     # Out
            #     elif event.button == 5:
            #         zoom /= constant

            #     #  Translation. 1: Mouse 01. 2: Scroll Wheel
            #     if event.button == 1 or event.button == 2: 
            #         # When first pressed, gets the (x,y)
            #         mouse_pos0 = (py.mouse.get_pos())  

            # elif event.type == py.MOUSEBUTTONUP: 
            #     if event.button == 2: 
            #         is_rotating = False

            # Get the state of all keyboard buttons
            keys = py.key.get_pressed()

            if keys[py.K_w]: camera_pos.y -= camera_speed.y
            if keys[py.K_a]: camera_pos.x += camera_speed.x
            if keys[py.K_s]: camera_pos.y += camera_speed.y
            if keys[py.K_d]: camera_pos.x -= camera_speed.x

            # Update transform matrix
            if keys[py.K_w] or keys[py.K_a] or keys[py.K_s] or keys[py.K_d]:
                ortho_to_screen = define_ortho_to_screen(camera_pos)



if __name__ == '__main__':
    main("STL/dodecahedron.stl")