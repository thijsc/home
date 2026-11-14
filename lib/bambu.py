"""A plate written as a Bambu Studio project: the parts' meshes, and the settings a single part changes, such as
supports. It carries no process, printer or filament settings: Bambu Studio takes those from the presets selected
when it is opened.

Bambu Studio reads a part's own settings only from a 3MF laid out the way Bambu Studio writes one: each part's mesh
in a file of its own under 3D/Objects, the settings in Metadata. The layout here is copied from a project Bambu
Studio 2.09.01 saved; it is not documented, so a newer Bambu Studio may read it differently, and an export is
checked by opening it (README.md, Slicer settings).
"""

import zipfile
from xml.sax.saxutils import quoteattr
from dataclasses import dataclass, field

# Each part's mesh, as finely as the plate's other files are written.
LINEAR_TOLERANCE = 0.01
ANGULAR_TOLERANCE = 0.2

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PRODUCTION = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
BAMBU = "http://schemas.bambulab.com/package/2021"
MODEL_TYPE = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
VERSION = "02.09.01.70"  # the Bambu Studio whose layout this is


@dataclass
class Part:
    """A part on the plate, turned the way it prints: its name, and the settings it changes from the presets, as Bambu
    Studio names them."""

    name: str
    shape: object
    settings: dict = field(default_factory=dict)


def _uuid(n, tail):
    return f"{n:08x}-{tail}"


def _mesh(shape):
    """The shape's triangles, about the middle of its bounding box, and that middle. tessellate() gives each face its
    own vertices, so where two faces meet the mesh would be open; a slicer repairing an open mesh fills holes in it.
    The vertices at the same place are made one, which closes it."""
    c = shape.bounding_box().center()
    points, faces = shape.tessellate(LINEAR_TOLERANCE, ANGULAR_TOLERANCE)
    index, vertices, remap = {}, [], []
    for v in points:
        key = (round(v.X - c.X, 6), round(v.Y - c.Y, 6), round(v.Z - c.Z, 6))
        if key not in index:
            index[key] = len(vertices)
            vertices.append(key)
        remap.append(index[key])
    triangles = [(remap[a], remap[b], remap[t]) for a, b, t in faces]
    triangles = [t for t in triangles if len(set(t)) == 3]
    return vertices, triangles, c


def _object_model(object_id, uuid, vertices, triangles):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{CORE}" xmlns:BambuStudio="{BAMBU}" xmlns:p="{PRODUCTION}" requiredextensions="p">',
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        " <resources>",
        f'  <object id="{object_id}" p:UUID="{uuid}" type="model">',
        "   <mesh>",
        "    <vertices>",
    ]
    lines += [f'     <vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in vertices]
    lines += ["    </vertices>", "    <triangles>"]
    lines += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in triangles]
    lines += ["    </triangles>", "   </mesh>", "  </object>", " </resources>", " <build/>", "</model>", ""]
    return "\n".join(lines)


def write_project(path, parts):
    """Write the parts, already set out on the plate, to path as a Bambu Studio project."""
    version = VERSION

    model = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{CORE}" xmlns:BambuStudio="{BAMBU}" xmlns:p="{PRODUCTION}" requiredextensions="p">',
        f' <metadata name="Application">BambuStudio-{version}</metadata>',
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        " <resources>",
    ]
    build, rels, config, plate, assemble, cuts, files = [], [], [], [], [], [], {}
    for i, part in enumerate(parts, start=1):
        mesh_id, object_id = 2 * i - 1, 2 * i  # the mesh in its own file, and the object on the plate holding it
        vertices, triangles, c = _mesh(part.shape)
        files[f"3D/Objects/object_{i}.model"] = _object_model(mesh_id, _uuid(i << 16, "81cb-4c03-9d28-80fed5dfa1dc"), vertices, triangles)
        model += [
            f'  <object id="{object_id}" p:UUID="{_uuid(i, "61cb-4c03-9d28-80fed5dfa1dc")}" type="model">',
            "   <components>",
            f'    <component p:path="/3D/Objects/object_{i}.model" objectid="{mesh_id}" p:UUID="{_uuid(i << 16, "b206-40ff-9872-83e8017abed1")}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>',
            "   </components>",
            "  </object>",
        ]
        move = f"1 0 0 0 1 0 0 0 1 {c.X:.6f} {c.Y:.6f} {c.Z:.6f}"
        build.append(f'  <item objectid="{object_id}" p:UUID="{_uuid(object_id, "b1ec-4553-aec9-835e5b724bb4")}" transform="{move}" printable="1"/>')
        rels.append(f' <Relationship Target="/3D/Objects/object_{i}.model" Id="rel-{i}" Type="{MODEL_TYPE}"/>')
        name = quoteattr(part.name.replace("_", " "))
        config.append(f'  <object id="{object_id}">')
        config.append(f'    <metadata key="name" value={name}/>')
        config += [f'    <metadata key={quoteattr(k)} value={quoteattr(str(v))}/>' for k, v in part.settings.items()]
        config += [
            '    <metadata key="extruder" value="1"/>',
            f'    <metadata face_count="{len(triangles)}"/>',
            f'    <part id="{mesh_id}" subtype="normal_part" uuid="{_uuid(i, "4f45-4d0b-a3fb-7295689fcc42")}">',
            f'      <metadata key="name" value={name}/>',
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
            '      <metadata key="extruder" value="1"/>',
            f'      <mesh_stat face_count="{len(triangles)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
            "    </part>",
            "  </object>",
        ]
        plate += [
            "    <model_instance>",
            f'      <metadata key="object_id" value="{object_id}"/>',
            '      <metadata key="instance_id" value="0"/>',
            f'      <metadata key="identify_id" value="{100 + i}"/>',
            "    </model_instance>",
        ]
        assemble += [
            f'   <assemble_item object_id="{object_id}" instance_id="0" transform="{move}" offset="0 0 0" />',
            f'   <assemble_item object_id="{object_id}" volume_id="0" transform="1 0 0 0 1 0 0 0 1 0 0 0" />',
        ]
        cuts += [f' <object id="{i}">', '  <cut_id id="0" check_sum="1" connectors_cnt="0"/>', " </object>"]

    model += [" </resources>", ' <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">'] + build + [" </build>", "</model>", ""]
    files["3D/3dmodel.model"] = "\n".join(model)
    files["3D/_rels/3dmodel.model.rels"] = "\n".join(
        ['<?xml version="1.0" encoding="UTF-8"?>',
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'] + rels + ["</Relationships>", ""])
    files["Metadata/model_settings.config"] = "\n".join(
        ['<?xml version="1.0" encoding="UTF-8"?>', "<config>"] + config
        + ["  <plate>", '    <metadata key="plater_id" value="1"/>', '    <metadata key="plater_name" value=""/>',
           '    <metadata key="locked" value="false"/>', '    <metadata key="filament_map_mode" value="Auto For Flush"/>']
        + plate + ["  </plate>", "  <assemble>"] + assemble + ["  </assemble>", "</config>", ""])
    files["Metadata/cut_information.xml"] = "\n".join(['<?xml version="1.0" encoding="utf-8"?>', "<objects>"] + cuts + ["</objects>"])
    files["Metadata/slice_info.config"] = "\n".join(
        ['<?xml version="1.0" encoding="UTF-8"?>', "<config>", "  <header>",
         '    <header_item key="X-BBL-Client-Type" value="slicer"/>',
         f'    <header_item key="X-BBL-Client-Version" value="{version}"/>', "  </header>", "</config>", ""])
    files["Metadata/filament_sequence.json"] = '{"plate_1":{"nozzle_sequence":[],"optimal_assignment":[],"sequence":[]}}'
    files["[Content_Types].xml"] = "\n".join(
        ['<?xml version="1.0" encoding="UTF-8"?>',
         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
         ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
         ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>',
         ' <Default Extension="png" ContentType="image/png"/>',
         ' <Default Extension="gcode" ContentType="text/x.gcode"/>',
         "</Types>", ""])
    files["_rels/.rels"] = "\n".join(
        ['<?xml version="1.0" encoding="UTF-8"?>',
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
         f' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="{MODEL_TYPE}"/>',
         "</Relationships>", ""])

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))  # the same parts write the same file
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text)
