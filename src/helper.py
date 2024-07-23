from enum import Enum
from numba import njit
import numpy as np


class FullMesh:
    def __init__(self, mesh) -> None:
        self.mesh = mesh

        self.points_4d  = None
        self.normals_4d = None

        self.remove_centroid = None
        self.add_centroid    = None


class Projection(Enum):
    ORTHO = 1
    PERSP = 2


class RenderType(Enum):
    FILL = 1
    WIRE = 2

@njit()
def normalize_1d(arr: np.array) -> np.array:
    norm = np.linalg.norm(arr)    
    if norm == 0: return arr    
    normalized = arr/norm
    return normalized


def get_face_color(a: np.array, b: np.array, light_direction: np.array) -> np.uint8: 
    normal = normalize_1d(np.cross(a, b)) 
    intensity = np.uint8(-110 * np.dot(normal, light_direction)) + 30
    return intensity    


def get_z_cross(
            a: np.array,
            b: np.array
        ) -> np.float32:

    return a[0]*b[1] - a[1]*b[0]