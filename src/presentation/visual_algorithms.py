"""Visual algorithms for treemap layout and color palette generation."""

import colorsys
from typing import List, Tuple


def generate_palette_colors(
    count: int,
    hue: int,
    saturation_range: List[int],
    lightness_range: List[int],
    hue_spread: int
) -> List[str]:
    """
    Generates a list of visually distinct colors within a harmonious palette.

    :param count: Number of colors to generate.
    :param hue: Base hue value (0-360).
    :param saturation_range: [min, max] saturation percentage (0-100).
    :param lightness_range: [min, max] lightness percentage (0-100).
    :param hue_spread: Total spread of hues around the base (0-180).
    :return: List of hex color strings.
    """
    colors = []
    sat_min, sat_max = saturation_range[0] / 100, saturation_range[1] / 100
    light_min, light_max = lightness_range[0] / 100, lightness_range[1] / 100

    for i in range(count):
        t = i / max(count - 1, 1)

        hue_offset = (i * 137.508) % 360
        current_hue = (hue + (hue_offset / 360) * hue_spread - hue_spread / 2) % 360

        if i % 2 == 0:
            saturation = sat_max - (sat_max - sat_min) * (t * 0.5)
            lightness = light_min + (light_max - light_min) * (t * 0.7)
        else:
            saturation = sat_min + (sat_max - sat_min) * (1 - t * 0.5)
            lightness = light_max - (light_max - light_min) * (t * 0.5)

        r, g, b = colorsys.hls_to_rgb(current_hue / 360, lightness, saturation)
        hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        colors.append(hex_color)

    return colors


def treemap_slice_dice(
    values: List[float],
    x: float,
    y: float,
    width: float,
    height: float,
    vertical: bool = True
) -> List[Tuple[float, float, float, float]]:
    """
    Slice-and-dice treemap algorithm.

    :param values: List of values (proportions).
    :param x: Starting x position.
    :param y: Starting y position.
    :param width: Total width available.
    :param height: Total height available.
    :param vertical: Start with vertical slicing.
    :return: List of tuples (x, y, width, height) for each rectangle.
    """
    if not values or width <= 0 or height <= 0:
        return []

    total = sum(values)
    if total == 0:
        return []

    rects = []
    n = len(values)

    if n == 1:
        return [(x, y, width, height)]

    if n == 2:
        ratio = values[0] / total
        if vertical:
            w1 = width * ratio
            rects.append((x, y, w1, height))
            rects.append((x + w1, y, width - w1, height))
        else:
            h1 = height * ratio
            rects.append((x, y, width, h1))
            rects.append((x, y + h1, width, height - h1))
        return rects

    mid = n // 2
    left_values = values[:mid]
    right_values = values[mid:]
    left_sum = sum(left_values)
    ratio = left_sum / total if total > 0 else 0.5

    if vertical:
        left_width = width * ratio
        rects.extend(treemap_slice_dice(
            left_values, x, y, left_width, height, not vertical
        ))
        rects.extend(treemap_slice_dice(
            right_values, x + left_width, y, width - left_width, height, not vertical
        ))
    else:
        left_height = height * ratio
        rects.extend(treemap_slice_dice(
            left_values, x, y, width, left_height, not vertical
        ))
        rects.extend(treemap_slice_dice(
            right_values, x, y + left_height, width, height - left_height, not vertical
        ))

    return rects
