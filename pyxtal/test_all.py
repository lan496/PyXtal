# python -m unittest pyxtal/test_all.py
import importlib.util
import os
import unittest
from random import choice, shuffle

import numpy as np
import pymatgen.analysis.structure_matcher as sm
from pymatgen.core import Lattice as pmg_Lattice
from pymatgen.core import Structure
from pymatgen.core.operations import SymmOp
from pymatgen.core.structure import Molecule
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from pyxtal import pyxtal
from pyxtal.lattice import Lattice
from pyxtal.molecule import pyxtal_molecule
from pyxtal.operations import get_inverse
from pyxtal.supergroup import supergroup, supergroups
from pyxtal.symmetry import Group, Hall, Wyckoff_position, get_wyckoffs
from pyxtal.util import generate_wp_lib
from pyxtal.wyckoff_site import atom_site
from pyxtal.XRD import Similarity


def resource_filename(package_name, resource_path):
    package_path = importlib.util.find_spec(package_name).submodule_search_locations[0]
    return os.path.join(package_path, resource_path)


cif_path = resource_filename("pyxtal", "database/cifs/")
l01 = Lattice.from_matrix([[4.08, 0, 0], [0, 9.13, 0], [0, 0, 5.50]])
l02 = Lattice.from_para(4.08, 9.13, 5.50, 90, 90, 90)
wp1 = Wyckoff_position.from_group_and_index(36, 0)
wp2 = Wyckoff_position.from_group_and_letter(36, "4a")


class TestGroup(unittest.TestCase):
    def test_generate_wp_lib(self):
        wps = generate_wp_lib([227, 228], composition=[1, 2])
        assert len(wps) == 18
        wps = generate_wp_lib([227, 228], composition=[1, 1, 3])
        assert len(wps) == 9

    def test_list_wyckoff_combinations(self):
        g = Group(64)
        a1, _, _ = g.list_wyckoff_combinations([4, 2])
        assert len(a1) == 0
        a2, _, _ = g.list_wyckoff_combinations([4, 8], quick=False)
        assert len(a2) == 8

    def test_print_group_and_dof(self):
        for d in [(1, 6), (15, 4), (60, 3), (143, 2), (208, 1)]:
            (sg, dof_ref) = d
            g = Group(sg)
            dof = g.get_lattice_dof()
            assert dof == dof_ref

    def test_get_spg_symmetry_object(self):
        spg_list = [14, 36, 62, 99, 143, 160, 182, 191, 225, 230]
        ans = [32, 18, 36, 21, 16, 19, 24, 48, 62, 62]
        for spg, num in zip(spg_list, ans):
            g = Group(spg)
            ss = g.get_spg_symmetry_object()
            matrix = ss.to_matrix_representation_spg()
            assert num == sum(sum(matrix))

    def test_short_path(self):
        g = Group(217)
        path = g.short_path_to_general_wp(7)
        assert path[-1][2] == 145

    def test_spg_symmetry(self):
        N_polar, N_centro, N_chiral = 0, 0, 0
        for sg in range(1, 231):
            g = Group(sg, quick=True)
            _pg, polar, centro, chiral = g.point_group, g.polar, g.inversion, g.chiral
            if polar:
                N_polar += 1
            if centro:
                N_centro += 1
            if chiral:
                N_chiral += 1
        assert N_polar == 68
        assert N_centro == 92
        assert N_chiral == 65

    def test_ferroelectric(self):
        pairs = [(4, 1), (187, 4), (222, 5)]
        for pair in pairs:
            (sg, N) = pair
            assert len(Group(sg, quick=True).get_ferroelectric_groups()) == N

    def test_check_compatible(self):
        assert Group(225).check_compatible([64, 28, 24]) == (True, True)
        assert Group(227).check_compatible([8]) == (True, False)
        assert Group(227).check_compatible([4]) == (False, False)
        assert Group(19).check_compatible([6]) == (False, False)

    def test_search_supergroup_paths(self):
        paths = Group(59, quick=True).search_supergroup_paths(139, 2)
        assert paths == [[71, 139], [129, 139], [137, 139]]

    def test_get_splitters(self):
        s = pyxtal()
        s.from_seed(cif_path + "3-G139.cif")
        g = Group(225)
        solutions = g.get_splitters_from_structure(s, "t")
        assert len(solutions) == 3

    def test_add_k_transitions(self):
        paras = [
            (189, 26, 6),
            (11, 6, 2),
            (62, 33, 3),
            (63, 33, 5),
        ]

        for p in paras:
            (g, h, n_path) = p
            gr = Group(g, quick=True)
            p = gr.search_subgroup_paths(h)[0]
            solutions = gr.add_k_transitions(p)
            assert len(solutions) == n_path

    def test_to_subgroup(self):
        s = pyxtal(molecular=True)
        s.from_seed(cif_path + "benzene.cif", ["benzene"])
        c = s.to_subgroup()
        assert c.valid

    def test_get_wyckoff_position_from_xyz(self):
        g = Group(5)
        pos = [
            ([0.0, 0.0, 0.0], "2a"),
            ([0.5, 0.5, 0.5], None),
            ([0.1, 0.0, 0.1], "4c"),
            ([0.5, 0.0, 0.0], None),
            ([0.0, 0.1, 0.0], "2a"),
            ([0.0, 0.5, 0.5], "2b"),
            ([0.1, 0.2, 0.3], "4c"),
        ]
        for d in pos:
            (p0, wp0) = d
            wp = g.get_wyckoff_position_from_xyz(p0)
            if wp is None:
                assert wp0 is None
            else:
                assert wp.get_label() == wp0


class TestSupergroup(unittest.TestCase):
    def test_supergroup(self):
        """
        call supergroup from pyxtal
        """
        data = [
            ("NbO2", 141, 5),
        ]
        for d in data:
            (cif, g, N) = d
            s = pyxtal()
            s.from_seed(cif_path + cif + ".cif")
            strucs, sols = s.supergroup(g, 0.5)
            assert len(strucs) > 0

    def test_make_pyxtal(self):
        data = {
            # "NbO2": 141,
            "GeF2": 62,
            "lt_quartz": 180,
            "NiS-Cm": 160,  # 9b->2a+4b
        }
        for cif in data:
            s = pyxtal()
            s.from_seed(cif_path + cif + ".cif")
            my = supergroup(s, G=data[cif])
            sols = my.search_supergroup(max_solutions=1)
            for sol in sols:
                struc_high = my.make_pyxtal_in_supergroup(sol)
                strucs = my.make_pyxtals_in_subgroup(sol, 3)
                pmg1 = struc_high.to_pymatgen()
                pmg2 = strucs[-1].to_pymatgen()
                rms = sm.StructureMatcher().get_rms_dist(pmg1, pmg2)[0]
                print(cif, rms)
                assert rms < 0.001

    def test_by_group(self):
        data = {
            "BTO-Amm2": 221,
            "BTO": 221,
            "lt_cristobalite": 227,
            "NaSb3F10": 194,
        }
        for cif in data:
            s = pyxtal()
            s.from_seed(cif_path + cif + ".cif")
            sup = supergroups(s, G=data[cif], show=False)
            assert sup.strucs is not None

    def test_by_path(self):
        data = {
            "MPWO": [59, 71, 139, 225],
        }
        for cif in data:
            s = pyxtal()
            s.from_seed(cif_path + cif + ".cif")
            sup = supergroups(s, path=data[cif], show=False)
            assert sup.strucs is not None

    def test_long(self):
        paras = (
            ["I4_132", 98],  # 1-3
            ["P3_112", 5],  # 1-3
            ["P6_422", 21],  # 1-3
        )
        for para in paras:
            name, H = para
            name = cif_path + name + ".cif"
            s = pyxtal()
            s.from_seed(name)
            pmg_s1 = s.to_pymatgen()
            G = s.group.number
            struc_h = s.subgroup_once(eps=0.05, H=H, mut_lat=False)
            sup = supergroups(struc_h, G=G, d_tol=0.2, show=False, max_per_G=500)

            if sup.strucs is None:
                print("Problem in ", name)
            assert sup.strucs is not None

            match = False
            for struc in sup.strucs:
                pmg_g = struc.to_pymatgen()
                if sm.StructureMatcher().fit(pmg_g, pmg_s1):
                    match = True
                    break
            if not match:
                print("Problem in ", name)
            assert match

    def test_long2(self):
        paras = (
            ["P4_332", 155],  # 1-4 splitting
            ["Fd3", 70],  # 1-3
            ["Pm3", 47],  # 1-3
            ["Fd3m", 166],
            ["R-3c", 15],
            ["R32", 5],
            ["R-3", 147],  # 1-3, k
            ["P4_332", 96],  # 1-3
        )
        for para in paras:
            name, H = para
            name = cif_path + name + ".cif"
            s = pyxtal()
            s.from_seed(name)
            pmg_s1 = s.to_pymatgen()
            G = s.group.number
            struc_h = s.subgroup_once(eps=0, H=H, mut_lat=False)
            my = supergroup(struc_h, G=G)
            sols = my.search_supergroup(max_solutions=1)

            if len(sols) == 0:
                print("problem", name)
            assert len(sols) > 0

            struc_high = my.make_pyxtal_in_supergroup(sols[0])
            struc_sub = my.make_pyxtals_in_subgroup(sols[0], 3)[-1]

            pmg_high = struc_high.to_pymatgen()
            pmg_sub = struc_sub.to_pymatgen()

            dist1 = sm.StructureMatcher().get_rms_dist(pmg_high, pmg_sub)[0]
            dist2 = sm.StructureMatcher().get_rms_dist(pmg_s1, pmg_high)[0]
            assert dist1 < 0.001
            assert dist2 < 0.001

    def test_multi(self):
        data = {
            "BTO": [123, 221],
            "lt_cristobalite": [98, 210, 227],
            "BTO-Amm2": [65, 123, 221],
            # "NaSb3F10": [186, 194],
            # "NaSb3F10": [176, 194],
            # "MPWO": [59, 71, 139, 225],
        }
        for cif in data:
            s = pyxtal()
            s.from_seed(cif_path + cif + ".cif")
            sup = supergroups(s, path=data[cif], show=False, max_per_G=2500)
            strucs = sup.get_transformation()
            pmg_0, pmg_1 = s.to_pymatgen(), sup.strucs[-1].to_pymatgen()
            pmg_2, pmg_3 = strucs[0].to_pymatgen(), strucs[1].to_pymatgen()
            dist1 = sm.StructureMatcher().get_rms_dist(pmg_0, pmg_2)[0]
            dist2 = sm.StructureMatcher().get_rms_dist(pmg_1, pmg_3)[0]
            print(cif, dist1, dist2)
            if dist2 > 1e-3:
                print(pmg_1)
                print(pmg_3)
            assert dist1 < 0.001
            assert dist2 < 0.001

    def test_similarity(self):
        paras = [
            ("0-G62", "2-G71"),
            ("0-G62", "3-G139"),
            # ('0-G62', '4-G225'),
        ]
        for para in paras:
            (cif1, cif2) = para
            s1 = pyxtal()
            s2 = pyxtal()
            s1.from_seed(cif_path + cif1 + ".cif")
            s2.from_seed(cif_path + cif2 + ".cif")
            pmg_s2 = s2.to_pymatgen()

            strucs, _, _, _, _ = s2.get_transition(s1)

            if strucs is None:
                print("Problem between ", cif1, cif2)
            else:
                struc_G_in_H = strucs[-1]
                s3 = pyxtal()
                s3.from_seed(struc_G_in_H.to_pymatgen(), tol=1e-3)
                pmg_s3 = s3.to_pymatgen()
                dist = sm.StructureMatcher().get_rms_dist(pmg_s2, pmg_s3)[0]
                assert dist < 0.001
                assert s3.group.number == s2.group.number

    def test_get_disp_sets(self):
        s1 = pyxtal()
        s1.from_seed(cif_path + "dist_6_0.cif")
        s2 = pyxtal()
        s2.from_seed(cif_path + "dist_6_1.cif")
        _, _, _, d = s1.get_disps_sets(s2, 1.0)
        assert d < 0.15

        s1 = pyxtal()
        s1.from_seed(cif_path + "sim-0.vasp")
        s2 = pyxtal()
        s2.from_seed(cif_path + "sim-1.vasp")
        _, _, _, d = s1.get_disps_sets(s2, 1.0, 0.3)
        assert d < 0.02


class TestOptLat(unittest.TestCase):
    def test_atomic(self):
        c1 = pyxtal()
        c1.from_seed(cif_path + "LiCs.cif", backend="pyxtal")
        pmg1 = c1.to_pymatgen()

        c2 = c1.copy()
        c2.optimize_lattice(1)
        pmg2 = c2.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg1, pmg2)

        c2.optimize_lattice(1)
        pmg2 = c2.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg1, pmg2)

        c3 = pyxtal()
        c3.from_seed(cif_path + "LiCs.cif")
        pmg3 = c3.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg1, pmg3)

    def test_molecular(self):
        c1 = pyxtal(molecular=True)
        c1.from_seed(seed=cif_path + "aspirin-c.cif", molecules=["aspirin"])
        c1.mol_sites[0].get_mol_object(0)
        c1.mol_sites[0].get_mol_object(1)
        pmg1 = c1.to_pymatgen()

        c2 = c1.copy()
        c2.optimize_lattice(1)
        pmg2 = c2.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg1, pmg2)

    def test_molecular_trans(self):
        c1 = pyxtal(molecular=True)
        c1.from_seed(seed=cif_path + "aspirin.cif", molecules=["aspirin"])
        pmg1 = c1.to_pymatgen()
        c1.transform(trans=[[1, 0, 0], [0, 1, 0], [-1, 0, 1]])
        pmg2 = c1.to_pymatgen()
        c1.optimize_lattice()
        pmg3 = c1.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg1, pmg2)
        assert sm.StructureMatcher().fit(pmg2, pmg3)

    def test_molecular_nonstd(self):
        sgs = [5, 7, 8, 9, 12, 13, 14, 15]
        c1 = pyxtal(molecular=True)
        for sg in sgs:
            hns = Hall(sg).hall_numbers
            for hn in hns[1:]:
                c1.from_random(3, hn, ["aspirin"], use_hall=True)
                pmg1 = c1.to_pymatgen()
                c2 = c1.copy()
                c2.optimize_lattice(1)
                pmg2 = c2.to_pymatgen()
                assert sm.StructureMatcher().fit(pmg1, pmg2)
                pmg3 = Structure.from_str(c1.to_file(), fmt="cif")
                assert sm.StructureMatcher().fit(pmg1, pmg3)

    def test_molecular(self):
        sgs = [5, 7, 8, 12, 13, 14]
        c1 = pyxtal(molecular=True)
        for _i in range(20):
            sg = choice(sgs)
            c1.from_random(3, sg, ["aspirin"])
            pmg1 = c1.to_pymatgen()
            c2 = c1.copy()
            c2.optimize_lattice(1)
            pmg2 = c2.to_pymatgen()
            assert sm.StructureMatcher().fit(pmg1, pmg2)

    def test_transform(self):
        l = Lattice.from_para(48.005, 7.320, 35.864, 90.000, 174.948, 90.000, ltype="monoclinic")
        sites = [
            [0.0000, 0.0000, 0.1250],
            [0.2296, 0.7704, 0.5370],
            [0.2296, 0.2296, 0.5370],
            [0.5408, 0.0000, 0.6186],
            [0.0000, 0.0000, 0.3074],
        ]
        c = pyxtal()
        c.build(9, ["S"], [8], lattice=l, sites=[sites])
        pmg0 = c.to_pymatgen()
        c.optimize_lattice()
        pmg1 = c.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg0, pmg1)

    def test_build(self):
        l = np.array([48.005, 7.320, 35.864, 90.000, 174.948, 90.000])
        sites = [
            [0.0000, 0.0000, 0.1250],
            [0.2296, 0.7704, 0.5370],
            [0.2296, 0.2296, 0.5370],
            [0.5408, 0.0000, 0.6186],
            [0.0000, 0.0000, 0.3074],
        ]
        c = pyxtal()
        c.build(9, ["S"], [8], lattice=l, sites=[sites])
        pmg0 = c.to_pymatgen()
        l1 = c.lattice.matrix

        c.optimize_lattice()
        pmg1 = c.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg0, pmg1)

        c1 = pyxtal()
        c1.build(9, ["S"], [8], lattice=l1, sites=[sites])
        c1.optimize_lattice()
        pmg2 = c1.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg0, pmg2)

    def test_build_1D(self):
        lat = Lattice.from_para(6.8472, 6.8472, 3.3198, 90, 90, 90, "tetragonal")
        c1 = pyxtal()
        sites = [
            [
                ("4g", 0.9236547993389047, 0.0, 0.5),
                ("4f", 0.39177300078207977, 0.0, 0.0),
            ]
        ]
        c1.build(30, ["C"], [8], lat, sites=sites, dim=1)
        assert c1.valid

    def test_build_2D(self):
        lat = Lattice.from_para(6.8472, 6.8472, 3.3198, 90, 90, 90, "tetragonal")
        c1 = pyxtal()
        sites = [[("4c", 0.15, 0.50, 0.28), ("4c", 0.59, 0.85, 0.87)]]
        c1.build(30, ["C"], [8], lat, sites=sites, dim=2)
        assert c1.valid

    # def test_build_0D(self):
    #    lat = Lattice.from_para(2.85, 2.85, 2.85, 90, 90, 90, 'spherical')
    #    c1 = pyxtal()
    #    sites = [[('8b', 0.70, 0.70, 0.70)]]
    #    c1.build(30, ['C'], [8], lat, sites=sites, dim=0)
    #    self.assertTrue(c1.valid)

    def test_transforms(self):
        paras = [
            (5.0317, 19.2982, 5.8004, 90.0000, 122.2672, 90.0000, "monoclinic", 6),
            (5.0317, 19.2982, 5.8004, 90.0000, 57.7328, 90.0000, "monoclinic", 6),
            (9.0640, 8.3522, 5.2856, 90.0000, 103.9699, 90.0000, "monoclinic", 3),
            (9.4913, 8.5844, 5.3358, 90.0000, 110.0035, 90.0000, "monoclinic", 3),
            (3.7727, 6.7490, 7.6446, 64.4392, 77.9087, 75.7214, "triclinic", 1),
            (3.7297, 6.5421, 7.9915, 73.9361, 71.5867, 103.2590, "triclinic", 1),
            (5.5740, 7.0902, 11.4529, 96.5703, 90.0224, 108.1857, "triclinic", 2),
            (5.5487, 7.1197, 11.4349, 83.0223, 89.8479, 72.0003, "triclinic", 2),
            (5.7985, 30.6352, 7.6374, 90.0000, 112.2615, 90.0000, "monoclinic", 3),
            (5.8280, 30.5992, 7.6373, 90.0000, 112.6020, 90.0000, "monoclinic", 3),
        ]

        for i in range(int(len(paras) / 2)):
            (a1, b1, c1, alpha1, beta1, gamma1, ltype1, N) = paras[i * 2]
            (a2, b2, c2, alpha2, beta2, gamma2, ltype2, N) = paras[i * 2 + 1]
            l1 = Lattice.from_para(a1, b1, c1, alpha1, beta1, gamma1, ltype=ltype1)
            l2 = Lattice.from_para(a2, b2, c2, alpha2, beta2, gamma2, ltype=ltype2)
            trans, diffs = l2.search_transformations(l1)
            print(i, len(trans), N)
            assert len(trans) == N

            # print("\nTarget:", l1)
            # print("Start :", l2)
            # if len(trans) == N:
            # for tran, diff in zip(trans, diffs):
            #    l = l2.transform_multi(tran)
            #    strs = "Success:" + str(l) + " {:6.3f} {:6.3f} {:6.3f}".format(*diff)
            #    print(strs)

    def test_optlat_setting(self):
        paras = [
            (18.950, 10.914, 31.672, 90, 168.63, 90, "monoclinic"),
            (48.005, 7.320, 35.864, 90, 174.948, 90, "monoclinic"),
        ]
        sites = [0.3600, 0.7500, 0.6743]
        for para in paras:
            (a, b, c, alpha, beta, gamma, ltype) = para
            l = Lattice.from_para(a, b, c, alpha, beta, gamma, ltype=ltype)
            for sg in range(3, 16):
                mult = Group(sg, quick=True)
                c = pyxtal()
                c.build(sg, ["S"], [mult], lattice=l, sites=[[sites]])
                pmg0 = c.to_pymatgen()
                c0 = c.copy()
                c0.optimize_lattice(standard=True)
                pmg1 = c0.to_pymatgen()
                c1 = c.copy()
                c1.optimize_lattice(standard=False)
                pmg2 = c1.to_pymatgen()
                d1 = sm.StructureMatcher().get_rms_dist(pmg0, pmg1)
                d2 = sm.StructureMatcher().get_rms_dist(pmg0, pmg2)
                assert sum(d1) + sum(d2) < 0.001


class TestWP(unittest.TestCase):
    def test_wp_check_translation(self):
        pass

    def test_wp_site_symm(self):
        data = [
            (143, 1, "3.."),
            (160, 1, ".m"),
            (160, 2, "3m"),
            (230, 6, ".32"),
        ]
        for d in data:
            (sg, i, symbol) = d
            wp = Group(sg)[i]
            wp.get_site_symmetry()
            # print("\n========", wp.site_symm, symbol, "==========\n")
            assert wp.site_symm == symbol

    def test_wp_dof(self):
        for sg in range(1, 231):
            g = Group(sg)
            for wp in g:
                axs = wp.get_frozen_axis()
                assert wp.get_dof() + len(axs) == 3

    def test_wp_label(self):
        symbol = wp1.get_label()
        assert symbol == "8b"
        symbol = wp2.get_label()
        assert symbol == "4a"

    def test_merge(self):
        pt, wp, _ = wp1.merge([0.05, 0.7, 0.24], l01.matrix, 0.5)
        symbol = wp.get_label()
        assert symbol == "4a"
        pt, wp, _ = wp1.merge([0.15, 0.7, 0.24], l01.matrix, 0.5)
        symbol = wp.get_label()
        assert symbol == "8b"

        wp = Group(167)[0]
        cell = np.diag([9, 9, 7])
        for pt in [[0.12, 0, 0.25], [0, 0.1316, 0.25]]:
            _, wpt, _ = wp.merge(pt, cell, 0.1)
            symbol = wpt.get_label()
            assert symbol == "18e"

        for pt in [[0, 0, 3 / 4], [2 / 3, 1 / 3, 7 / 12]]:
            _, wpt, _ = wp.merge(pt, cell, 0.1)
            symbol = wpt.get_label()
            assert symbol == "6a"

    def test_search_generator(self):
        wp = Group(167)[1]
        for pt in [[0, 0.13, 0.25], [0.13, 0, 0.25]]:
            wp0 = wp.search_generator(pt)
            assert wp0 is not None

    def test_get_wyckoff(self):
        for i in [1, 2, 229, 230]:
            get_wyckoffs(i)
            get_wyckoffs(i, organized=True)

    def test_setting(self):
        wp = Group(14)[0]
        wp.transform_from_matrix()
        assert not wp.is_standard_setting()

    def test_standarize(self):
        pass

    def test_is_equivalent(self):
        g = Group(15)
        wp = g[0]
        a = [0.10052793, 0.12726851, 0.27405404]
        b = [-0.10052642, -0.12726848, -0.27405526]
        c = [0.60052642, 0.62726848, 0.27405526]
        d = [-0.60052642, -0.62726848, -0.27405526]
        e = [0, 2.54537267e-01, 0]
        assert wp.are_equivalent_pts(a, b)
        assert wp.are_equivalent_pts(b, c)
        assert wp.are_equivalent_pts(d, a)
        assert not wp.are_equivalent_pts(a, e)

        wp = g[1]
        a = [0.00, 0.127, 0.254]
        b = [-0.01, -0.127, -0.250]
        assert wp.are_equivalent_pts(a, b)

    def test_project(self):
        pt = np.array([0.0629, 0.1258, 0.25])
        g = Group(178)
        wp = g[1]
        xyz0 = wp.project(pt, np.eye(3))
        diff = np.sum((pt - xyz0) ** 2)
        assert diff < 1e-08

    def test_euclidean(self):
        def check_error(spg, pt, cell):
            p0 = np.dot(pt, cell.matrix)
            for sg in spg:
                wp = Group(sg)[0]
                for i in range(len(wp)):
                    op0 = wp[i]
                    p1 = op0.operate(pt)

                    op1 = wp.get_euclidean_generator(cell.matrix, i)
                    if wp.euclidean:
                        p2 = np.dot(op1.operate(p0), cell.inv_matrix)
                    else:
                        p2 = np.dot(op1.apply_rotation_only(p0), cell.inv_matrix)
                        p2 += op1.translation_vector

                    diff = p1 - p2
                    diff -= np.rint(diff)
                    if np.linalg.norm(diff) > 0.02:
                        # res = '{:2d} {:28s}'.format(i, op0.as_xyz_str())
                        # res += ' {:28s}'.format(op1.as_xyz_str())
                        # res += '{:6.3f} {:6.3f} {:6.3f} -> '.format(*p1)
                        # res += '{:6.3f} {:6.3f} {:6.3f} -> '.format(*p2)
                        # res += '{:6.3f} {:6.3f} {:6.3f}'.format(*diff)
                        # print(res)
                        return False
            return True

        pt = [0.1333, 0.1496, 0.969]

        cell = Lattice.from_para(9.395, 7.395, 8.350, 91, 101, 92, ltype="triclinic")
        assert check_error(range(1, 3), pt, cell)

        cell = Lattice.from_para(9.395, 7.395, 8.350, 90, 101, 90, ltype="monoclinic")
        assert check_error(range(3, 16), pt, cell)

        cell = Lattice.from_para(9.395, 7.395, 8.350, 90, 90, 90, ltype="orthorhombic")
        assert check_error(range(16, 74), pt, cell)

        cell = Lattice.from_para(9.395, 9.395, 8.350, 90, 90, 90, ltype="tetragonal")
        assert check_error(range(74, 143), pt, cell)

        cell = Lattice.from_para(9.395, 9.395, 8.350, 90, 90, 120, ltype="hexagonal")
        assert check_error(range(143, 195), pt, cell)

        cell = Lattice.from_para(9.395, 9.395, 9.395, 90, 90, 90, ltype="cubic")
        assert check_error(range(195, 231), pt, cell)


class TestDof(unittest.TestCase):
    def test_atomic(self):
        s = pyxtal()
        s.from_random(3, 225, ["C"], [8])
        ans = s.get_dof()
        assert s.lattice.dof == 1
        assert ans == 1


class TestMolecule(unittest.TestCase):
    def test_get_orientations_in_wp(self):
        m = pyxtal_molecule("Benzene")
        g = Group(61)
        assert len(m.get_orientations_in_wp(g[0])) == 1
        assert len(m.get_orientations_in_wp(g[1])) == 1
        assert len(m.get_orientations_in_wp(g[2])) == 1


class TestMolecular(unittest.TestCase):
    def test_single_specie(self):
        struc = pyxtal(molecular=True)
        struc.from_random(3, 36, ["H2O"], sites=[["8b"]])
        struc.to_file()
        assert struc.valid

        # test space group
        pmg_struc = struc.to_pymatgen()
        sga = SpacegroupAnalyzer(pmg_struc)
        # print(sga.get_space_group_symbol())
        assert sga.get_space_group_number() >= 36

        # test rotation
        struc.mol_sites[0].orientation.axis
        struc.mol_sites[0].rotate(ax_vector=[1, 0, 0], angle=90)
        pmg_struc = struc.to_pymatgen()
        sga = SpacegroupAnalyzer(pmg_struc)
        # pmg_struc.to("cif", "1.cif")
        assert sga.get_space_group_symbol() == "Cmc2_1"
        # print(pmg_struc.frac_coords[:3])

    def test_sites(self):
        struc = pyxtal(molecular=True)
        struc.from_random(3, 19, ["H2O"])
        pmg_struc = struc.to_pymatgen()
        sga = SpacegroupAnalyzer(pmg_struc)
        assert sga.get_space_group_symbol() == "P2_12_12_1"

        struc = pyxtal(molecular=True)
        struc.from_random(3, 36, ["H2O"], [8], sites=[["4a", "4a"]])
        pmg_struc = struc.to_pymatgen()
        sga = SpacegroupAnalyzer(pmg_struc)
        assert sga.get_space_group_symbol() == "Cmc2_1"

    def test_sites_xyz(self):
        struc = pyxtal(molecular=True)
        sites = [{"4e": [0.77, 0.57, 0.53]}]
        lat = Lattice.from_para(11.43, 6.49, 11.19, 90, 83.31, 90, ltype="monoclinic")
        struc.from_random(3, 14, ["aspirin"], [4], lattice=lat, sites=sites)
        assert struc.valid

    def test_read(self):
        # test reading structure from external
        struc = pyxtal(molecular=True)
        struc.from_seed(seed=cif_path + "aspirin.cif", molecules=["aspirin"])
        assert struc.lattice.ltype == "monoclinic"
        pmg_struc = struc.to_pymatgen()
        sga = SpacegroupAnalyzer(pmg_struc)
        assert sga.get_space_group_symbol() == "P2_1/c"
        C = struc.subgroup_once(eps=0, H=4)
        pmg_s2 = C.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg_struc, pmg_s2)

    def test_big_molecule(self):
        # print("test_big_molecule")
        for mol in ["ROY", "aspirin"]:
            struc = pyxtal(molecular=True)
            struc.from_random(3, 19, [mol], factor=1.4)
            assert struc.valid
            pair = struc.check_short_distances()
            if len(pair) > 0:
                print("short distances were detected")
                print(mol)
                print(pair)
            assert len(pair) == 0

    def test_from_random_site(self):
        spg, wps, elements, numIons = 224, [["24j"]], ["C"], [24]
        for _i in range(10):
            c = pyxtal()
            c.from_random(3, spg, elements, numIons, sites=wps)
            pair = c.check_short_distances(0.5)
            assert len(pair) == 0

    def test_c60(self):
        struc = pyxtal(molecular=True)
        struc.from_random(3, 36, ["C60"], [4], 1.0)
        assert struc.valid

    def test_mutiple_species(self):
        Li = Molecule(["Li"], [[0.0, 0.0, 0.0]])
        coords = [
            [0.000000, 0.000000, 0.000000],
            [1.200000, 1.200000, -1.200000],
            [1.200000, -1.200000, 1.200000],
            [-1.200000, 1.200000, 1.200000],
            [-1.200000, -1.200000, -1.200000],
        ]
        ps4 = Molecule(["P", "S", "S", "S", "S"], coords)

        for _i in range(3):
            struc = pyxtal(molecular=True)
            struc.from_random(3, 10, [Li, ps4], [6, 2], 1.2, conventional=False)
            if struc.valid:
                assert len(struc.to_pymatgen()) == 16

    def test_distance(self):
        Ag_xyz = """1
        AgC2N2H
        Ag         4.30800        8.26300       -0.2200
        """

        C2N2H7_xyz = """12
        AgC2N2H
        H          5.95800        5.80600       -0.9530
        N          5.24100        6.16800       -1.1210
        N          2.23200        6.99000       -0.6820
        C          4.02900        5.47000       -1.5870
        C          2.78500        5.61100       -0.6610
        H          3.69300        5.63500       -2.5830
        H          4.17400        4.42800       -1.6990
        H          3.12700        5.50500        0.4260
        H          2.05000        5.01200       -0.9300
        H          1.96000        7.20500       -1.3860
        H          1.59400        6.99200       -0.0710
        """
        with open("Ag.xyz", "w") as f:
            f.write(Ag_xyz)
        with open("C2N2H7.xyz", "w") as f:
            f.write(C2N2H7_xyz)

        for _i in range(10):
            c = pyxtal(molecular=True)
            c.from_random(3, 9, ["Ag.xyz", "C2N2H7.xyz"], [12, 12])
            short_bonds = c.check_short_distances(r=1.1)
            assert len(short_bonds) == 0
        os.remove("Ag.xyz")
        os.remove("C2N2H7.xyz")

    def test_molecular_2d(self):
        # print("test_molecular_2d")
        struc = pyxtal(molecular=True)
        struc.from_random(2, 20, ["H2O"])
        assert struc.valid

    def test_molecular_1d(self):
        struc = pyxtal(molecular=True)
        struc.from_random(1, 20, ["H2O"])
        assert struc.valid

    def test_preassigned_sites(self):
        sites = [["4a", "4a"]]
        struc = pyxtal(molecular=True)
        struc.from_random(3, 36, ["H2O"], [8], sites=sites)
        assert struc.valid

    def test_special_sites(self):
        struc = pyxtal(molecular=True)
        struc.from_random(3, 61, ["Benzene"], [4])
        assert struc.valid


class TestAtomic3D(unittest.TestCase):
    def test_single_specie(self):
        struc = pyxtal()
        struc.from_random(3, 225, ["C"], [4], 1.2, conventional=False)
        struc.to_file()
        assert struc.valid

    def test_mutiple_species(self):
        struc = pyxtal()
        struc.from_random(3, 99, ["Ba", "Ti", "O"], [1, 1, 3], 1.2)
        assert struc.valid

    def test_preassigned_sites(self):
        sites = [["1b"], ["1b"], ["2c", "1b"]]
        struc = pyxtal()
        struc.from_random(3, 99, ["Ba", "Ti", "O"], [1, 1, 3], 1.0, sites=sites)
        assert struc.valid

        struc = pyxtal()
        struc.from_random(3, 225, ["C"], [12], 1.0, sites=[["4a", "8c"]])
        assert struc.valid

    def test_read(self):
        # test reading xtal from cif
        for name in ["FAU", "NaSb3F10", "PVO", "lt_quartz"]:
            cif_file = cif_path + name + ".cif"
            pmg1 = Structure.from_file(cif_file, primitive=True)
            struc = pyxtal()
            struc.from_seed(seed=cif_file)
            pmg_struc = struc.to_pymatgen()
            assert sm.StructureMatcher().fit(pmg_struc, pmg1)

    def test_read_spglib(self):
        # test reading xtal from cif
        for name in ["FAU"]:
            cif_file = cif_path + name + ".cif"
            pmg1 = Structure.from_file(cif_file, primitive=True)
            struc = pyxtal()
            struc.from_seed(seed=cif_file, style="spglib")
            pmg_struc = struc.to_pymatgen()
            assert sm.StructureMatcher().fit(pmg_struc, pmg1)
        # more space groups
        for name in ["I41amd", "P4nmm", "Pmmn", "Pn3m", "Fd3", "Pn3"]:
            cif_file = cif_path + name + ".vasp"
            pmg1 = Structure.from_file(cif_file, primitive=True)
            struc = pyxtal()
            struc.from_seed(seed=cif_file, style="spglib")
            pmg_struc = struc.to_pymatgen()
            assert sm.StructureMatcher().fit(pmg_struc, pmg1)

    def test_read_by_HN(self):
        for name in ["aspirin"]:
            cif_file = cif_path + name + ".cif"
            pmg1 = Structure.from_file(cif_file, primitive=True)
            struc = pyxtal()
            for hn in Hall(14).hall_numbers:
                struc._from_pymatgen(pmg1, hn=hn)
                pmg_struc = struc.to_pymatgen()
                assert sm.StructureMatcher().fit(pmg_struc, pmg1)


class TestAtomic2D(unittest.TestCase):
    def test_single_specie(self):
        struc = pyxtal()
        struc.from_random(2, 20, ["C"], [4], 1.0, thickness=2.0)
        struc.to_file()
        assert struc.valid

    def test_mutiple_species(self):
        struc = pyxtal()
        struc.from_random(2, 4, ["Mo", "S"], [2, 4], 1.0)
        assert struc.valid


class TestAtomic1D(unittest.TestCase):
    def test_single_specie(self):
        struc = pyxtal()
        struc.from_random(1, 20, ["C"], [4], 1.0)
        struc.to_file()
        assert struc.valid

    def test_mutiple_species(self):
        struc = pyxtal()
        struc.from_random(1, 4, ["Mo", "S"], [2, 4], 1.0)
        assert struc.valid


class TestCluster(unittest.TestCase):
    def test_multi_sites(self):
        struc = pyxtal()
        struc.from_random(0, 1, ["C"], [60], 1.0)
        assert struc.valid

        struc = pyxtal()
        struc.from_random(0, 3, ["C"], [60], 1.0)
        assert struc.valid

    def test_single_specie(self):
        struc = pyxtal()
        struc.from_random(0, "Ih", ["C"], [60], 1.0)
        assert struc.valid

    def test_mutiple_species(self):
        struc = pyxtal()
        struc.from_random(0, 4, ["Mo", "S"], [2, 4], 1.0)
        assert struc.valid


class TestLattice(unittest.TestCase):
    def test_para_matrix(self):
        assert np.allclose(l01.matrix, l02.matrix)

    def test_swap(self):
        l01.swap_axis(ids=[1, 0, 2])
        abc = l01.get_para()[:3]
        assert abc, np.array([9.13, 4.08, 5.5])

    def test_optimize_once(self):
        l3 = Lattice.from_para(4.08, 7.13, 5.50, 90, 38, 90, ltype="monoclinic")
        lat, tran, _ = l3.optimize_once()
        assert abs(lat.beta - 1.495907) < 0.0001

    def test_optimize_multi(self):
        l4 = Lattice.from_para(71.364, 9.127, 10.075, 90.00, 20.80, 90.00, ltype="monoclinic")
        lat, _ = l4.optimize_multi(7)
        assert abs(lat.beta - 1.7201) < 0.01

    def test_setpara(self):
        l0 = Lattice.from_matrix([[4.08, 0, 0], [0, 9.13, 0], [0, 0, 5.50]])
        l0.set_para([5, 5, 5, 90, 90, 90])
        assert l0.a == 5

    def test_search_transformation(self):
        l6 = Lattice.from_para(3.454, 3.401, 5.908, 90.00, 105.80, 90.00, ltype="monoclinic")
        l7 = Lattice.from_para(6.028, 3.419, 6.028, 90.00, 146.92, 90.00, ltype="monoclinic")
        l7, _ = l7.optimize_multi()
        trans, diff = l7.search_transformation(l6)
        l7 = l7.transform_multi(trans)
        assert np.abs(l7.matrix - l6.matrix).sum() < 0.25

    def test_is_valid_lattice(self):
        l8 = Lattice.from_para(3.454, 3.401, 5.908, 90.00, 105.80, 91.00, ltype="monoclinic")
        l9 = Lattice.from_para(3.454, 3.401, 5.908, 90.00, 105.80, 90.00, ltype="monoclinic")
        l10 = Lattice.from_para(3.454, 3.401, 5.908, 90.00, 90.00, 90.00, ltype="cubic")
        assert not l8.is_valid_lattice()
        assert l9.is_valid_lattice()
        assert not l10.is_valid_lattice()

    def test_from_1d_representation(self):
        lat = Lattice.from_1d_representation([5.09, 6.11], "trigonal")
        assert abs(lat.a - 5.09) < 0.001
        assert abs(lat.c - 6.11) < 0.001
        assert abs(lat.gamma - 2 / 3 * np.pi) < 0.001


class TestSymmetry(unittest.TestCase):
    def test_from_symops_wo_grou(self):
        data = [
            (["x, y, z", "-x, y+1/2, -z"], 4, 6),
            (["x, y, z", "-x+1/2, -y, z+1/2", "-x, y, z", "x+1/2, -y, z+1/2"], 31, 155),
            (
                ["x, y, z", "-x, -y, -z", "-x+1/2, y+1/2, -z", "x+1/2, -y+1/2, z"],
                14,
                83,
            ),
            (
                [
                    "x, y, z",
                    "-x, -y, -z",
                    "-x+1/2, y+1/2, -z+1/2",
                    "x+1/2, -y+1/2, z+1/2",
                ],
                14,
                82,
            ),
        ]
        for d in data:
            (strs, spg, hall) = d
            wp = Wyckoff_position.from_symops_wo_group(strs)
            assert wp.number == spg
            assert wp.hall_number == hall

    def test_from_symops(self):
        data = [
            (["x, y, z", "-x, y+1/2, -z"], 4, 6),
            (["x, y, z", "-x+1/2, -y, z+1/2", "-x, y, z", "x+1/2, -y, z+1/2"], 31, 155),
        ]
        for d in data:
            (strs, spg, hall) = d
            G = Group(spg)
            wp = Wyckoff_position.from_symops(strs, G)
            assert wp.number == spg
            assert wp.hall_number == hall


class TestNeighbour(unittest.TestCase):
    def test_packing(self):
        c = pyxtal(molecular=True)
        for data in [
            ("aspirin", 14),
            ("WEXBOS", 14),
            ("MERQIM", 12),
            ("LAGNAL", 16),
            ("YICMOP", 14),
            ("LUFHAW", 18),
            ("coumarin", 14),
            ("HAHCOI", 14),
            ("JAPWIH", 14),
            ("AXOSOW01", 14),
            ("PAHYON01", 13),
            ("xxvi", 15),
            ("resorcinol", 14),
        ]:
            (name, CN) = data
            c.from_seed(seed=cif_path + name + ".cif", molecules=[name])
            ds, _, _, _, engs = c.get_neighboring_molecules(0, 1.5)
            # print(engs)
            # print(name, CN, len(ds))
            assert len(ds) == CN


class TestSubgroup(unittest.TestCase):
    def test_cubic_cubic(self):
        sites = ["8a", "32e"]
        numIons = int(sum([int(i[:-1]) for i in sites]))
        C1 = pyxtal()
        C1.from_random(3, 227, ["C"], [numIons], sites=[sites])
        pmg_s1 = C1.to_pymatgen()
        # sga1 = SpacegroupAnalyzer(pmg_s1).get_space_group_symbol()

        C2s = C1.subgroup(eps=1e-5)
        for C2 in C2s:
            pmg_s2 = C2.to_pymatgen()
            # sga2 = SpacegroupAnalyzer(pmg_s2).get_space_group_symbol()
            # prevent some numerical error
            if not sm.StructureMatcher().fit(pmg_s1, pmg_s2):
                C12 = pyxtal()
                C12.from_seed(pmg_s2)
                pmg_12 = C12.to_pymatgen()
                assert sm.StructureMatcher().fit(pmg_s1, pmg_12)

            # self.assertTrue(sm.StructureMatcher().fit(pmg_s1, pmg_s2))

        C1.subgroup(perms={"C": "Si"}, H=216)

    def test_from_seed(self):
        coords = [[0, 0, 0], [0.75, 0.5, 0.75]]
        lattice = pmg_Lattice.from_parameters(a=3.84, b=3.84, c=3.84, alpha=120, beta=90, gamma=60)
        struct = Structure(lattice, ["Si", "C"], coords)
        s1 = pyxtal()
        s1.from_seed(struct)
        s2 = s1.subgroup_once(eps=0)
        pmg_s1 = s1.to_pymatgen()
        pmg_s2 = s2.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg_s1, pmg_s2)

    def test_molecules(self):
        for name in [
            "aspirin",
            "resorcinol",
            "coumarin",
            "HAHCOI",
            "xxvi",
            "WEXBOS",
            "MERQIM",
            "LAGNAL",
            "YICMOP",
            "LUFHAW",
            "JAPWIH",
            "AXOSOW01",
            "PAHYON01",
        ]:
            cif = cif_path + name + ".cif"
            struc = pyxtal(molecular=True)
            struc.from_seed(seed=cif, molecules=[name])
            pmg_struc = struc.to_pymatgen()
            pmg_s1 = Structure.from_file(cif, primitive=True)
            assert sm.StructureMatcher().fit(pmg_struc, pmg_s1)

            Cs = struc.subgroup(eps=0, max_cell=1)
            for C in Cs:
                pmg_s2 = C.to_pymatgen()
                assert sm.StructureMatcher().fit(pmg_struc, pmg_s2)

    def test_hydrate(self):
        # glycine dihydrate
        cif = cif_path + "gdh.cif"
        struc = pyxtal(molecular=True)
        struc.from_seed(seed=cif, molecules=["Glycine-z", "H2O"])
        pmg_struc = struc.to_pymatgen()
        pmg_s1 = Structure.from_file(cif, primitive=True)
        assert sm.StructureMatcher().fit(pmg_struc, pmg_s1)

    def test_special(self):
        cif = cif_path + "191.vasp"
        struc = pyxtal()
        struc.from_seed(seed=cif)
        for _i in range(100):
            struc.subgroup_once(0.2, None, None, "t+k", 2)


class TestPXRD(unittest.TestCase):
    def test_similarity(self):
        C1 = pyxtal()
        C1.from_random(3, 227, ["C"], [8], sites=[["8a"]])
        xrd1 = C1.get_XRD()
        C2 = C1.subgroup_once(eps=1e-3)
        xrd2 = C1.get_XRD()
        p1 = xrd1.get_profile()
        p2 = xrd2.get_profile()
        s = Similarity(p1, p2, x_range=[15, 90])
        assert 0.9 < s.value < 1.001

        C2.apply_perturbation(1e-3, 1e-3)
        xrd3 = C2.get_XRD()
        xrd3.get_profile()
        s = Similarity(p1, p2, x_range=[15, 90])
        assert 0.95 < s.value < 1.001


class TestLoad(unittest.TestCase):
    def test_atomic(self):
        s1 = pyxtal()
        s1.from_random(3, 36, ["C", "Si"], [4, 8])
        s2 = pyxtal()
        s2.load_dict(s1.save_dict())
        pmg_s1 = s1.to_pymatgen()
        pmg_s2 = s2.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg_s1, pmg_s2)

    def test_molecular(self):
        s1 = pyxtal(molecular=True)
        s1.from_random(3, 36, ["H2O"], [4])
        s2 = pyxtal()
        s2.load_dict(s1.save_dict())
        pmg_s1 = s1.to_pymatgen()
        pmg_s2 = s2.to_pymatgen()
        assert sm.StructureMatcher().fit(pmg_s1, pmg_s2)


class TestPartial(unittest.TestCase):
    def test_Al2SiO5(self):
        cell = Lattice.from_para(7.8758, 7.9794, 5.6139, 90, 90, 90)
        spg = 58
        elements = ["Al", "Si", "O"]
        composition = [8, 4, 20]
        sites = [
            {
                "4e": [0.0000, 0.0000, 0.2418],
                "4g": [0.1294, 0.6392, 0.0000],
            },
            {"4g": [0.2458, 0.2522, 0.0000]},
            [],  # empty for oxygen
        ]

        s = pyxtal()
        s.from_random(3, spg, elements, composition, lattice=cell, sites=sites)
        assert s.valid

        sites2 = [
            {
                "4e": [0.0000, 0.0000, 0.2418],
                "4g": [0.1294, 0.6392, 0.0000],
            },
            {"4g": [0.2458, 0.2522, 0.0000]},
            {"4g": [0.4241, 0.3636, 0.0000]},  # partial info on O
        ]

        s = pyxtal()
        s.from_random(3, spg, elements, composition, lattice=cell, sites=sites2)
        assert s.valid


class resort(unittest.TestCase):
    def test_molecule(self):
        # glycine dihydrate
        cif = cif_path + "gdh.cif"
        struc = pyxtal(molecular=True)
        struc.from_seed(seed=cif, molecules=["Glycine-z", "H2O"])
        N1 = len(struc.mol_sites)
        l = list(range(len(struc.mol_sites)))
        shuffle(l)
        struc.mol_sites = [struc.mol_sites[i] for i in l]
        struc.resort()
        N2 = len(struc.mol_sites)
        assert N1 == N2

    def test_atom(self):
        cif = cif_path + "aspirin.cif"
        struc = pyxtal()
        struc.from_seed(seed=cif)
        N1 = len(struc.atom_sites)
        l = list(range(len(struc.atom_sites)))
        shuffle(l)
        struc.atom_sites = [struc.atom_sites[i] for i in l]
        struc.resort()
        N2 = len(struc.atom_sites)
        assert N1 == N2


class Test_wyckoff_site(unittest.TestCase):
    def test_atom_site(self):
        """
        Test the search function
        """
        wp = Group(227)[-5]
        arr = np.array([0.1, 0.1, 0.1])
        for xyz in [
            [0.6501, 0.15001, 0.5999],
            [0.6501, 0.14999, 0.5999],
            [0.6499, 0.14999, 0.5999],
            [0.6499, 0.14999, 0.60001],
        ]:
            site = atom_site(wp, xyz, search=True)
            assert np.allclose(site.position, arr, rtol=0.001)


class Test_operations(unittest.TestCase):
    def test_inverse(self):
        coord0 = [0.35, 0.1, 0.4]
        coords = np.array(
            [
                [0.350, 0.100, 0.400],
                [0.350, 0.100, 0.000],
                [0.350, 0.100, 0.000],
                [0.350, 0.000, 0.667],
                [0.350, 0.000, 0.250],
                [0.350, 0.350, 0.400],
                [0.350, 0.350, 0.500],
                [0.350, 0.350, 0.000],
                [0.350, 0.350, 0.350],
                [0.100, 0.100, 0.100],
                [0.400, 0.400, 0.400],
                [0.350, 0.000, 0.000],
                [0.000, 0.100, 0.400],
                [0.350, 0.000, 0.400],
            ]
        )
        xyzs = [
            "x,y,z",
            "x,y,0",
            "y,x,0",
            "x,0,2/3",
            "0,x,1/4",
            "x,x,z",
            "x,-x,1/2",
            "2x,x,0",
            "-2x,-0.5x,-x+1/4",
            "-2y,-0.5y,-y+1/4",
            "-2z,-0.5z,-z+1/4",
            "0,0,x",
            "-y/2+1/2,-z,0",
            "-z,-x/2+1/2,0",
        ]

        for i, xyz in enumerate(xyzs):
            op = SymmOp.from_xyz_str(xyz)
            inv_op = get_inverse(op)
            coord1 = op.operate(coord0)
            coord2 = inv_op.operate(coord1)
            assert np.allclose(coord2, coords[i], rtol=0.01)
            # strs = "{:6.3f} {:6.3f} {:6.3f}".format(*coord0)
            # strs += "  {:12s}  ".format(op.as_xyz_str())
            # strs += "{:6.3f} {:6.3f} {:6.3f}".format(*coord1)
            # strs += "  {:12s}  ".format(inv_op.as_xyz_str())
            # strs += "{:6.3f} {:6.3f} {:6.3f}".format(*coord2)
            # print(strs)

    def test_swap_wp(self):
        g = Group(38)
        wp = g[4]
        wp1, trans = wp.swap_axis([1, 0, 2])

        g = Group(71)
        wp = g[5]
        wp1, trans = wp.swap_axis([0, 2, 1])
        wp1, trans = wp.swap_axis([1, 2, 0])
        wp1, trans = wp.swap_axis([2, 1, 0])

    def test_alternative(self):
        for name in ["BTO-Amm2", "lt_quartz", "GeF2", "lt_cristobalite", "PVO"]:
            s = pyxtal()
            s.from_seed(cif_path + name + ".cif")
            pmg_s1 = s.to_pymatgen()
            strucs = s.get_alternatives()
            for struc in strucs:
                pmg_s2 = struc.to_pymatgen()
                assert sm.StructureMatcher().fit(pmg_s1, pmg_s2)

    def test_wyc_sets(self):
        for i in range(1, 229):
            Group(i, quick=True).get_alternatives()["No."]

    def test_trans(self):
        mats = [
            np.array([[1, 0, 1], [0, 1, 0], [0, 0, 1]]),
            np.array([[1, 0, -1], [0, 1, 0], [0, 0, 1]]),
        ]

        for n in range(3, 16):
            hns = Hall(n).hall_numbers
            for hn in hns:
                g = Group(hn, use_hall=True)
                for i in range(1, len(g)):
                    wp = g[i].copy()
                    for mat in mats:
                        wp.transform_from_matrix(mat)
                        c1, c2 = wp.update()
                        # print(hn, i, (c1 or c2))
                        assert c1 or c2

    # def test_image(self):
    #    from pyxtal.descriptor import spherical_image
    #    c1 = pyxtal(molecular=True)
    #    for name in ['benzene', 'aspirin', 'naphthalene']:
    #        c1.from_seed(seed=cif_path+name+".cif", molecules=[name])
    #        for model in ['contact', 'molecule']:
    #            sph = spherical_image(c1, model=model)
    #            sph.align()
    #            print(name, model)

    class TestSubstitution(unittest.TestCase):
        def test_substitute_1_2(self):
            data = [
                (227, ["8a"], [3.6], ["C"], 1),
                (
                    92,
                    ["4a", "8b"],
                    [5.0847, 7.0986, 0.2944, 0.0941, 0.2410, 0.8256],
                    ["Si", "O"],
                    1,
                ),
            ]
            for d in data:
                (spg, wps, rep, elements, N) = d
                s = pyxtal()
                xtals = s.from_spg_wps_rep(spg, wps, rep, elements)
                assert len(xtals) == N

        def test_criteria(self):
            criteria = {"CN": {"B": 4, "N": 4}, "cutoff": 1.9, "exclude_ii": True}
            xtals = xtal.substitute_1_2({"C": ["B", "N"]}, ratio=[1, 1], criteria=criteria)
            assert xtals[0].check_validity(criteria)


if __name__ == "__main__":
    unittest.main()
