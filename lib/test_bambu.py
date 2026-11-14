"""bambu.py: a plate written as a Bambu Studio project.

Run with `bin/part --test`.
"""

import tempfile
import unittest
import xml.dom.minidom
import zipfile
from pathlib import Path

from build123d import Box, Cylinder, Pos

from bambu import Part, write_project


def parts():
    return [Part("front_shell", Pos(20, 20, 5) * Box(10, 10, 10), {"enable_support": "1"}),
            Part("wheel", Pos(60, 20, 4) * Cylinder(5, 8))]


class WriteProject(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "plate.3mf"
        write_project(self.path, parts())
        self.zip = zipfile.ZipFile(self.path)

    def tearDown(self):
        self.zip.close()
        self.dir.cleanup()

    def read(self, name):
        return self.zip.read(name).decode()

    def test_it_holds_what_bambu_studio_reads_a_project_from(self):
        for name in ("[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "3D/_rels/3dmodel.model.rels",
                     "3D/Objects/object_1.model", "3D/Objects/object_2.model", "Metadata/model_settings.config"):
            self.assertIn(name, self.zip.namelist())
        for name in self.zip.namelist():
            if name.endswith((".model", ".config", ".rels", ".xml")):
                xml.dom.minidom.parseString(self.zip.read(name))

    def test_it_carries_no_process_printer_or_filament_settings(self):
        self.assertNotIn("Metadata/project_settings.config", self.zip.namelist())

    def test_it_says_which_bambu_studio_layout_it_is(self):
        self.assertIn('<metadata name="Application">BambuStudio-02.09.01.70</metadata>', self.read("3D/3dmodel.model"))

    def test_each_part_carries_its_name_and_its_own_settings(self):
        config = self.read("Metadata/model_settings.config")
        self.assertIn('<metadata key="name" value="front shell"/>', config)
        self.assertIn('<metadata key="enable_support" value="1"/>', config)
        self.assertEqual(config.count("<model_instance>"), 2)

    def test_a_mesh_sits_about_its_middle_and_the_plate_puts_it_back(self):
        model = self.read("3D/3dmodel.model")
        self.assertIn('transform="1 0 0 0 1 0 0 0 1 20.000000 20.000000 5.000000"', model)
        mesh = xml.dom.minidom.parseString(self.zip.read("3D/Objects/object_1.model"))
        xs = [float(v.getAttribute("x")) for v in mesh.getElementsByTagName("vertex")]
        self.assertAlmostEqual(min(xs), -5)
        self.assertAlmostEqual(max(xs), 5)

    def test_a_mesh_is_closed_and_turned_one_way_so_the_slicer_does_not_repair_it(self):
        d = Path(self.dir.name)
        write_project(d / "holed.3mf", [Part("plate", Box(20, 20, 4) - Cylinder(3, 4))])
        with zipfile.ZipFile(d / "holed.3mf") as z:
            mesh = xml.dom.minidom.parseString(z.read("3D/Objects/object_1.model"))
        edges = {}
        for t in mesh.getElementsByTagName("triangle"):
            a, b, c = (int(t.getAttribute(k)) for k in ("v1", "v2", "v3"))
            for edge in ((a, b), (b, c), (c, a)):
                edges[edge] = edges.get(edge, 0) + 1
        self.assertTrue(edges)
        for (a, b), n in edges.items():
            self.assertEqual((n, edges.get((b, a))), (1, 1), f"edge {a}-{b}")

    def test_names_and_settings_are_escaped(self):
        d = Path(self.dir.name)
        write_project(d / "quoted.3mf", [Part("a_&_b", Box(5, 5, 5), {"filament_settings_id": 'PLA "Matte" <1>'})])
        with zipfile.ZipFile(d / "quoted.3mf") as z:
            config = xml.dom.minidom.parseString(z.read("Metadata/model_settings.config"))
        values = {m.getAttribute("key"): m.getAttribute("value") for m in config.getElementsByTagName("metadata")}
        self.assertEqual((values["name"], values["filament_settings_id"]), ("a & b", 'PLA "Matte" <1>'))

    def test_the_same_parts_write_the_same_file(self):
        again = Path(self.dir.name) / "again.3mf"
        write_project(again, parts())
        self.assertEqual(again.read_bytes(), self.path.read_bytes())


if __name__ == "__main__":
    unittest.main()
