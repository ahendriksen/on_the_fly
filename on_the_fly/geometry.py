import numpy as np


def get_extents_shape(vg):
    WindowMinX = vg["option"]["WindowMinX"]
    WindowMaxX = vg["option"]["WindowMaxX"]
    WindowMinY = vg["option"]["WindowMinY"]
    WindowMaxY = vg["option"]["WindowMaxY"]
    WindowMinZ = vg["option"]["WindowMinZ"]
    WindowMaxZ = vg["option"]["WindowMaxZ"]

    voxZ = vg["GridSliceCount"]
    voxY = vg["GridRowCount"]
    voxX = vg["GridColCount"]

    extents = np.array(
        [
            (WindowMinZ, WindowMaxZ),
            (WindowMinY, WindowMaxY),
            (WindowMinX, WindowMaxX),
        ]
    )

    shape = np.array([voxZ, voxY, voxX])
    return extents, shape


def calculate_mask_index(vg, mask_vg):
    extents, shape = get_extents_shape(vg)
    size = extents[:, 1] - extents[:, 0]
    voxel_size = size / shape

    mask_extents, mask_shape = get_extents_shape(mask_vg)

    left = (mask_extents[:, 0] - extents[:, 0]) / voxel_size
    right = (mask_extents[:, 1] - extents[:, 0]) / voxel_size

    mask_idx = tuple(slice(int(l), int(r)) for l, r in zip(left, right))

    return mask_idx
