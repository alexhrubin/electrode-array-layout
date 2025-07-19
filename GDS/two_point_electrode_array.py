import gdsfactory as gf


def make_electrode_points(spacing_um):
    x = 200 - spacing_um / 2
    arm_points = [
        (-100, 0),
        (0, 0),
        (x - 25, 300),
        (x - 25, 400),
        (x, 400),
        (x, 300),
        (25, 0),
        (100, 0),
        (100, -200),
        (-100, -200),
        (-100, 0)
    ]

    right_arm_points = [(400-x, y) for x, y in arm_points]
    return arm_points, right_arm_points


def ITO_points(spacing_um, edge_overlap_um):
    points = [
        (200 - spacing_um/2 - edge_overlap_um, 325),
        (200 - spacing_um/2 - edge_overlap_um, 375),
        (200 + spacing_um/2 + edge_overlap_um, 375),
        (200 + spacing_um/2 + edge_overlap_um, 325),
        (200 - spacing_um/2 - edge_overlap_um, 325),
    ]
    return points


def make_electrode(spacing_um, edge_overlap_um, gap_um):
    electrode = gf.Component()

    left_points, right_points = make_electrode_points(spacing_um)
    electrode.add_polygon(left_points, layer=(1,0))
    electrode.add_polygon(right_points, layer=(1,0))

    points = ITO_points(spacing_um, edge_overlap_um)
    electrode.add_polygon(points, layer=(2,0))

    # Add label (the ITO/metal overlap size) and center it below the pattern
    label_text = gf.components.text(text=f"{gap_um} um", size=75, layer=(1, 0))
    text_ref = electrode.add_ref(label_text)

    (text_xmin, _), (text_xmax, _) = label_text.bbox_np()
    text_width = text_xmax - text_xmin

    (xmin, ymin), (xmax, _) = electrode.bbox_np()
    x_pos = (xmin + xmax - text_width) / 2
    y_pos = ymin - 150
    text_ref.move((x_pos, y_pos))

    return electrode
