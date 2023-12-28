"""
Functions for working with layers.

Examples:
    .. code-block:: python

        path = path(layer) # Returns "path/to/layer".
        workspace = workspace(layer) # Returns "path/to/workspace.
                                     # This is the same as the value in ``path``,
                                     # but without the layer name.
                                     
        kind = kind(layer)
        if kind == LayerKind.Casing:
            do_something()

    Note: 
        Layer names include the groups of which they are a part.
        Nested groups appear in parent-child order.
        E.g., layer "foo" in subgroup "bar" in group "baz" has a 
        layer name of "baz\\bar\\foo"
"""
import re
from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional

import arcpy


def path(
    layer: arcpy._mp.Layer,  # pyright: ignore [reportGeneralTypeIssues]
) -> str:
    """
    Returns the absolute path to a layer.

    Arguments:
        layer (arcpy._mp.Layer): A layer object.

    Returns:
        str: The absolute path to the layer.
    """
    desc = arcpy.Describe(layer)
    path_parent = desc.path  # pyright: ignore [reportGeneralTypeIssues]
    name_long = desc.name  # pyright: ignore [reportGeneralTypeIssues]

    path = f"{path_parent}\\{name_long}"

    return path


def name(
    layer: arcpy._mp.Layer,  # pyright: ignore [reportGeneralTypeIssues]
) -> str:
    """
    Returns the layer's base name.

    Arguments:
        layer (arcpy._mp.Layer): A layer object.

    Returns:
        str: The layer's name.
    """
    desc = arcpy.Describe(layer)
    name_long = desc.name  # pyright: ignore [reportGeneralTypeIssues]
    index_slash = name_long.rfind("\\")

    name: str = name_long[index_slash + 1 :]

    return name


def workspace(
    layer: arcpy._mp.Layer,  # pyright: ignore [reportGeneralTypeIssues]
) -> str:
    """
    Returns the absolute path to a layer's workspace.

    Arguments:
        layer (arcpy._mp.Layer): A layer object.

    Returns:
        str: The absolute path to the layer's workspace.
    """
    desc = arcpy.Describe(layer)
    path_parent = desc.path  # pyright: ignore [reportGeneralTypeIssues]
    index_slash = path_parent.rfind("\\")

    workspace: str = path_parent[:index_slash]

    return workspace


@dataclass
class _TemplateIndex:
    affix_template: str
    index: int


@unique
class LayerKind(Enum):
    """
    Enumerates layer variants with a payload containing their affix template and parameter index.

    Use the parameter index with a contiguous slice into the relevant part of your parameter
    list that contains the layer kinds in alphabetical order.
    """

    Casing = _TemplateIndex("{}CA", 0)
    ControlValve = _TemplateIndex("{}CV", 1)
    Fitting = _TemplateIndex("{}FT", 2)
    Hydrant = _TemplateIndex("{}HYD", 3)
    ServiceLine = _TemplateIndex("{}SERV", 4)
    Structure = _TemplateIndex("{}STR", 5)
    SystemValve = _TemplateIndex("{}SV", 6)
    WaterMain = _TemplateIndex("000015-WATER-000{}", 7)


def kind(
    layer: arcpy._mp.Layer,  # pyright: ignore [reportGeneralTypeIssues]
) -> Optional[LayerKind]:
    """
    Returns the type of a layer

    Arguments:
        layer (arcpy._mp.Layer): A layer object.

    Returns:
        Optional[LayerKind]: The kind of layer.
    """
    name_layer = name(layer)

    pattern = (
        r"(?P<ca>waCasing)"
        r"|(?P<cv>waControlValve)"
        r"|(?P<ft>waFitting)"
        r"|(?P<hy>waHydrant)"
        r"|(?P<sl>waServiceLine)"
        r"|(?P<st>waStructure)"
        r"|(?P<sv>waSystemValve)"
        r"|(?P<wm>waWaterMain)"
    )
    regex = re.compile(pattern)
    match = regex.search(name_layer)

    if match is None:
        return None

    match_groups = match.groupdict()
    kind_map = {
        "ca": LayerKind.Casing,
        "cv": LayerKind.ControlValve,
        "ft": LayerKind.Fitting,
        "hy": LayerKind.Hydrant,
        "sl": LayerKind.ServiceLine,
        "st": LayerKind.Structure,
        "sv": LayerKind.SystemValve,
        "wm": LayerKind.WaterMain,
    }

    intersection = set(match_groups.keys()) & set(kind_map.keys())
    layer_kind = kind_map[next(iter(intersection))]

    return layer_kind
