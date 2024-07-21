from math import sin, cos, tan, pi
import numpy as np


class vf3d:
    def __init__(self, values: list[float]) -> None:
        self.x = values[0]
        self.y = values[1]
        self.z = values[2]


def define_ortho_to_screen_matrix(ortho_box: vf3d, canvas_dims: vf3d, camera_pos: np.array) -> np.array:
    return np.array([                               # Orthografic space to screen space
        [canvas_dims.x/(ortho_box.x), 0, 0, 0],
        [0, canvas_dims.y/(ortho_box.y), 0, 0],
        [0, 0, canvas_dims.z/(ortho_box.z), 0],
        [0, 0, 0, 1]   
    ]) @ np.array([                                 # Translate on opposite direction of camera
        [1, 0, 0, -camera_pos[0]],
        [0, 1, 0, -camera_pos[1]],
        [0, 0, 1, -camera_pos[2]],
        [0, 0, 0, 1]
    ])


def define_persp_to_screen_matrix(canvas_dims: vf3d, fov: float, z_far: float, camera_pos: np.array) -> np.array:
    a = canvas_dims.x / canvas_dims.y
    f = 1 / tan(fov / 2)
    l = z_far / (z_far - f)
    return np.array([                   # NDC space to screen space
        [canvas_dims.x/2, 0, 0, 0],
        [0, canvas_dims.y/2, 0, 0],
        [0, 0, canvas_dims.z/2, 0],
        [0, 0, 0, 1]   
    ]) @ \
    np.array([                          # Perspective to NDC space
        [f*a, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, l, -l*f],
        [0, 0, 1, 0]   
    ]) @ \
    np.array([                          # Translate on z for illusion of camera
        [1, 0, 0, -camera_pos[0]],
        [0, 1, 0, -camera_pos[1]],
        [0, 0, 1, -camera_pos[2]],
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

