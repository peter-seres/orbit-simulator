import numpy as np
from typing import Tuple

# Type alias for typing clarity:
Vector = np.ndarray | list[int] | list[float] | tuple[int] | tuple[float]
Color = (
    tuple[float, float, float] | tuple[int, int, int] | list[int, int, int],
    list[float, float, float],
)


def normalize(v: Vector, eps: float = 1e-6) -> Tuple[Vector, float]:
    """ Normalize vector v, with threshold eps. Raises ZeroDivisionError for zero-vector. """
    
    norm = np.linalg.norm(v)
    if norm < eps:
        raise ZeroDivisionError(
            f"Cannot normalize zero length vector: {v} with norm: {norm}."
        )
    return v / norm, norm


def rotate_vector_2D(v: Vector, angle: float) -> np.ndarray:
    """ Rotate 2D vector v with angle using rotation matrix."""
    
    ca, sa = np.cos(angle), np.sin(angle)
    return np.array([[ca, -sa], [sa, ca]]) @ v
