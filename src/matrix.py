import numpy as np


class vf3d:
    def __init__(self, values: list[np.float32]) -> None:
        self.x = values[0]
        self.y = values[1]
        self.z = values[2]


def define_ortho_to_screen_matrix(
        ortho_box:   np.array, 
        canvas_dims: np.array, 
        camera_pos:  np.array
        ) -> np.array:

    return np.array([                               # Orthografic space to screen space
        [canvas_dims[0]/(ortho_box[0]), 0, 0, canvas_dims[0]/2],
        [0, canvas_dims[1]/(ortho_box[1]), 0, canvas_dims[1]/2],
        [0, 0, canvas_dims[2]/(ortho_box[2]), canvas_dims[2]/2],
        [0, 0, 0, 1]   
    ], dtype=np.float32) @ \
    np.array([                                 # Translate on opposite direction of camera
        [1, 0, 0, -camera_pos[0]],
        [0, 1, 0, -camera_pos[1]],
        [0, 0, 1, -camera_pos[2]],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def define_persp_to_screen_matrix(
        canvas_dims: np.array, 
        fov:         np.float32, 
        z_far:       np.float32, 
        camera_pos:  np.array
        ) -> np.array:

    a = canvas_dims[0] / canvas_dims[1]
    f = 1 / np.tan(fov / 2)
    l = z_far / (z_far - f)
    return np.array([                   # NDC space to screen space
        [canvas_dims[0]/2, 0, 0, canvas_dims[0]/2],
        [0, canvas_dims[1]/2, 0, canvas_dims[1]/2],
        [0, 0, canvas_dims[2]/2, canvas_dims[2]/2],
        [0, 0, 0, 1]   
    ], dtype=np.float32) @ \
    np.array([                          # Perspective to NDC space
        [f*a, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, l, -l*f],
        [0, 0, 1, 0]   
    ], dtype=np.float32) @ \
    np.array([                          # Translate on z for illusion of camera
        [1, 0, 0, -camera_pos[0]],
        [0, 1, 0, -camera_pos[1]],
        [0, 0, 1, -camera_pos[2]],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def define_rotation_matrix(
        yaw_degrees:   float = 0, 
        pitch_degrees: float = 0, 
        roll_degrees:  float = 0
        ) -> np.array:

    alpha_rad = yaw_degrees   * np.pi / 180
    beta_rad  = pitch_degrees * np.pi / 180
    gamma_rad = roll_degrees  * np.pi / 180

    return np.array([                                   # Yaw
        [np.cos(alpha_rad), -np.sin(alpha_rad), 0, 0],
        [np.sin(alpha_rad),  np.cos(alpha_rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32) @ \
    np.array([                                          # Pitch
        [ np.cos(beta_rad), 0, np.sin(beta_rad), 0],
        [0, 1, 0, 0],
        [-np.sin(beta_rad), 0, np.cos(beta_rad), 0],
        [0, 0, 0, 1],
    ], dtype=np.float32) @ \
    np.array([                                          # Roll
        [1, 0, 0, 0],
        [0, np.cos(gamma_rad), -np.sin(gamma_rad), 0],
        [0, np.sin(gamma_rad),  np.cos(gamma_rad), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)