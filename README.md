# 3D renderer based on python

![3d-renderer](https://github.com/user-attachments/assets/74042263-4244-4edd-aa0d-2fca79e27254)

## Description
This is an exercise on the inner workings of 3d engines.

All the transformations (3D to NDC to screen space) are built from scratch.
Also, triangles rasterization with z depth buffer and shading were built from the ground up.

### Dependencies
Pygame is only used to create a window and render the individual pixels.

Numpy is used for matrix transformations.

Numba provides a great boost on performance by compiling the most inefficient functions, due to python loops.
It requires scipy for functions which rely heavily on linear algebra.

Numpy-stl is used to importthe stl files to a Mesh object.

## Setup
Clone the repo and cd into it.

### Optional
Create a venv: ```python -m venv venv```

Tap into it: ```source venv/bin/activate```

### Required
Install dependencies via pip:

```pip install -r requirements.txt```

## Usage
Just run ```python3 src/main.py```

If you are NOT using a venv, you may also call the script directly, with ```./src/main.py```.

Beware it may take a few seconds to start, as some functions are being compiled with numba.
