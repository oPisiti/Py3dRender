from math import sin, cos, pi
import numpy as np


class vf3d:
    def __init__(self, values: list[float]) -> None:
        self.x = values[0]
        self.y = values[1]
        self.z = values[2]


def define_ortho_to_screen_matrix(ortho_box: vf3d, canvas_dims: vf3d) -> np.array:
    return np.array([
        [canvas_dims.x/(ortho_box.x), 0, 0, 0],
        [0, canvas_dims.y/(ortho_box.y), 0, 0],
        [0, 0, canvas_dims.z/(ortho_box.z), 0],
        [0, 0, 0, 1]   
    ])

# def define_ortho_to_screen_matrix() -> np.array:
#     w = py.display.Info().current_w
#     h = py.display.Info().current_h
#     return np.array([
#         [w, 0, 0, 0],
#         [0, h, 0, 0],
#         [0, 0, w, 0],
#         [0, 0, 0, 1]   
#     ])

def define_persp_to_ortho_matrix(near: float) -> np.array:
    # f = near + ortho_box.z
    return np.array([
        [near, 0, 0, 0],
        [0, near, 0, 0],
        [0, 0, near, near],
        [0, 0, 1, 0]   
    ])

# def define_persp_to_ortho_matrix(aspect: float = 1, near = 1, far = 10) -> np.array:
#     tan_falf_FOV = tan(Globals.FOV / 2)
#     return np.array([
#         [1/(aspect*tan_falf_FOV), 0, 0, 0],
#         [0, 1/tan_falf_FOV, 0, 0],
#         [0, 0, far/(far-near), -(far*near)/(far-near)],
#         [0, 0, 1, 0]   
#     ])


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

