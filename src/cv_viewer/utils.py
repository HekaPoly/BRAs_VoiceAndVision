import cv2
import numpy as np
import pyzed.sl as sl

id_colors = [(232, 176, 59),
             (175, 208, 25),
             (102, 205, 105),
             (185, 0, 255),
             (99, 107, 252)]

def render_object(object_data, is_tracking_on):
    """
    #TODO: add type of object_data
    Determines whether a detected object should 
    be rendered based on the tracking state

    Parameters:
        object_data () : The detected object data.
        is_tracking_on (bool) : Whether tracking is currently unabled.

    Returns:
        bool : True if the object should be drawn, false otherwise.
    """
    if is_tracking_on:
        return object_data.tracking_state == sl.OBJECT_TRACKING_STATE.OK
    else:
        return (object_data.tracking_state == sl.OBJECT_TRACKING_STATE.OK) or (
                    object_data.tracking_state == sl.OBJECT_TRACKING_STATE.OFF)


def generate_color_id_u(idx):
    """
    Generates an RGB color for a given object ID.
    The function cycles through a fixed list of colors using modulo operation.

    Parameters:
        idx (int) : The ID of the object

    Returns:
        list[int] : A list of four integers representing the RGB colors.
    """
    arr = []
    if idx < 0:
        arr = [236, 184, 36, 255]
    else:
        color_idx = idx % 5
        arr = [id_colors[color_idx][0], id_colors[color_idx][1], id_colors[color_idx][2], 255]
    return arr


def draw_vertical_line(left_display, start_pt, end_pt, clr, thickness):
    """
    #TODO: add type left_display
    Draws a vertical line between two points

    Parameters:
        left_display () : The image/frame on which to draw the line.
        start_pt (tuple) : The starting point (x , y) of the line
        end_pt (tuple) : The ending point (x , y) of the line.
        clr (tuple) : The RGB color of the line 
        thickness (int) : Thickness of the line in pixels.
        
    Returns:
        None

    """
    n_steps = 7
    pt1 = [((n_steps - 1) * start_pt[0] + end_pt[0]) / n_steps
        , ((n_steps - 1) * start_pt[1] + end_pt[1]) / n_steps]
    pt4 = [(start_pt[0] + (n_steps - 1) * end_pt[0]) / n_steps
        , (start_pt[1] + (n_steps - 1) * end_pt[1]) / n_steps]

    cv2.line(left_display, (int(start_pt[0]), int(start_pt[1])), (int(pt1[0]), int(pt1[1])), clr, thickness)
    cv2.line(left_display, (int(pt4[0]), int(pt4[1])), (int(end_pt[0]), int(end_pt[1])), clr, thickness)
