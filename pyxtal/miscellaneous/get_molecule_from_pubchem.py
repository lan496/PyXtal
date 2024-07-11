import pubchempy as pcp
import numpy as np
import json
from pyxtal.database.element import Element
from rdkit import Chem
from rdkit.Chem import AllChem
import pymatgen as mg


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def read_molecule(mol, name):
    x = np.transpose([mol.record["coords"][0]["conformers"][0]["x"]])
    y = np.transpose([mol.record["coords"][0]["conformers"][0]["y"]])
    z = np.transpose([mol.record["coords"][0]["conformers"][0]["z"]])

    xyz = np.concatenate((x, y, z), axis=1)
    numbers = mol.record["atoms"]["element"]
    elements = [Element(i).short_name for i in numbers]
    volume = mol.volume_3d
    pubchemid = mol.cid
    molecule = {
        "name": name,
        "elements": elements,
        "xyz": xyz,
        "volume": volume,
        "pubchem id": pubchemid,
    }
    return molecule


names = [
    "H2O",
    "CH4",
    "NH3",
    "benzene",
    "naphthalene",
    "anthracene",
    "tetracene",
    "Pentacene",
    "coumarin",
    "resorcinol",
    "benzamide",
    "aspirin",
    "ddt",
    "lindane",
    "Glycine",
    "Glucose",
    "ROY",
]

molecules = []
molecule = {
    "name": "C60",
    "elements": ["C"] * 60,
    "xyz": np.array(
        [
            [2.2101953, 0.5866631, 2.6669504],
            [3.1076393, 0.1577008, 1.6300286],
            [1.3284430, -0.3158939, 3.2363232],
            [3.0908709, -1.1585005, 1.2014240],
            [3.1879245, -1.4574599, -0.1997005],
            [3.2214623, 1.2230966, 0.6739440],
            [3.3161210, 0.9351586, -0.6765151],
            [3.2984981, -0.4301142, -1.1204138],
            [-0.4480842, 1.3591484, 3.2081020],
            [0.4672056, 2.2949830, 2.6175264],
            [-0.0256575, 0.0764219, 3.5086259],
            [1.7727917, 1.9176584, 2.3529691],
            [2.3954623, 2.3095689, 1.1189539],
            [-0.2610195, 3.0820935, 1.6623117],
            [0.3407726, 3.4592388, 0.4745968],
            [1.6951171, 3.0692446, 0.1976623],
            [-2.1258394, -0.8458853, 2.6700963],
            [-2.5620990, 0.4855202, 2.3531715],
            [-0.8781521, -1.0461985, 3.2367302],
            [-1.7415096, 1.5679963, 2.6197333],
            [-1.6262468, 2.6357030, 1.6641811],
            [-3.2984810, 0.4301871, 1.1204208],
            [-3.1879469, 1.4573895, 0.1996030],
            [-2.3360261, 2.5813627, 0.4760912],
            [-0.5005210, -2.9797771, 1.7940308],
            [-1.7944338, -2.7729087, 1.2047891],
            [-0.0514245, -2.1328841, 2.7938830],
            [-2.5891471, -1.7225828, 1.6329715],
            [-3.3160705, -0.9350636, 0.6765268],
            [-1.6951919, -3.0692581, -0.1976564],
            [-2.3954901, -2.3096853, -1.1189862],
            [-3.2214182, -1.2231835, -0.6739581],
            [2.1758234, -2.0946263, 1.7922529],
            [1.7118619, -2.9749681, 0.7557198],
            [1.3130656, -1.6829416, 2.7943892],
            [0.3959024, -3.4051395, 0.7557638],
            [-0.3408219, -3.4591883, -0.4745610],
            [2.3360057, -2.5814499, -0.4761050],
            [1.6263757, -2.6357349, -1.6642309],
            [0.2611352, -3.0821271, -1.6622618],
            [-2.2100844, -0.5868636, -2.6670300],
            [-1.7726970, -1.9178969, -2.3530466],
            [-0.4670723, -2.2950509, -2.6175105],
            [-1.3283500, 0.3157683, -3.2362375],
            [-2.1759882, 2.0945383, -1.7923294],
            [-3.0909663, 1.1583472, -1.2015749],
            [-3.1076090, -0.1578453, -1.6301627],
            [-1.3131365, 1.6828292, -2.7943639],
            [0.5003224, 2.9799637, -1.7940203],
            [-0.3961148, 3.4052817, -0.7557272],
            [-1.7120629, 2.9749122, -0.7557988],
            [0.0512824, 2.1329478, -2.7937450],
            [2.1258630, 0.8460809, -2.6700534],
            [2.5891853, 1.7227742, -1.6329562],
            [1.7943010, 2.7730684, -1.2048262],
            [0.8781323, 1.0463514, -3.2365313],
            [0.4482452, -1.3591061, -3.2080510],
            [1.7416948, -1.5679557, -2.6197714],
            [2.5621724, -0.4853529, -2.3532026],
            [0.0257904, -0.0763567, -3.5084446],
        ]
    ),
    "volume": None,
    "pubchem id": 123591,
}
molecules.append(molecule)

molecule = {
    "name": "Glycine-z",
    "elements": ["H", "N", "H", "C", "H", "H", "H", "C", "O", "O"],
    "xyz": np.array(
        [
            [3.090064, 3.564361, -0.325567],
            [2.538732, 3.591476, -1.036692],
            [2.097666, 2.810077, -1.104272],
            [1.560226, 4.699895, -0.864107],
            [3.019736, 3.730336, -1.784084],
            [0.843929, 4.596366, -1.524923],
            [1.157363, 4.630876, 0.026367],
            [2.190568, 6.104112, -1.022811],
            [1.309305, 6.980823, -0.972406],
            [3.437359, 6.189565, -1.153186],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "xxvi",
    "elements": [
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "N",
        "C",
        "O",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "Cl",
        "N",
        "C",
        "O",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "Cl",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
    ],
    "xyz": np.array(
        [
            [3.13073867, -3.36491150, -2.64721385],
            [1.82477880, -3.71896813, -2.32546087],
            [0.94261928, -2.80596909, -1.82568763],
            [1.33731746, -1.45528852, -1.62963296],
            [2.66874173, -1.09519586, -1.98228771],
            [3.53907849, -2.08759686, -2.49307291],
            [3.06616823, 0.24489274, -1.81773666],
            [2.21038255, 1.17722323, -1.34625977],
            [0.87895828, 0.83753665, -1.01123254],
            [0.44151629, -0.46570153, -1.12746036],
            [-0.94993120, -0.85053187, -0.72466066],
            [-1.16819747, -1.49926227, 0.47582205],
            [-2.47506679, -1.91279650, 0.84257981],
            [-3.52001657, -1.65697309, 0.0221523],
            [-3.35904520, -0.99094614, -1.2040898],
            [-4.44946712, -0.73078858, -2.06144647],
            [-4.26939744, -0.08842722, -3.23777638],
            [-2.99799640, 0.32962609, -3.6132389],
            [-1.90848392, 0.10128131, -2.81797595],
            [-2.05490421, -0.57541197, -1.58133938],
            [-0.05140171, -1.75619845, 1.29870195],
            [-0.02048065, -2.08495563, 2.61339307],
            [-1.02814328, -2.27640038, 3.26779866],
            [1.32913247, -2.27627206, 3.23718665],
            [1.39188403, -3.28135647, 4.20405182],
            [2.55142361, -3.57714301, 4.86588481],
            [3.69004600, -2.87488273, 4.6081055],
            [3.66640049, -1.85872590, 3.68219674],
            [2.50413258, -1.57167947, 2.99828407],
            [2.57998011, -0.25813695, 1.85536291],
            [0.01862539, 1.84408465, -0.51985822],
            [-0.06322446, 3.08119149, -1.05782811],
            [0.50335840, 3.39619442, -2.09912528],
            [-0.93447067, 4.06888913, -0.35196746],
            [-1.91485002, 4.70053843, -1.12064886],
            [-2.71788802, 5.64575569, -0.54703666],
            [-2.55145998, 5.99309950, 0.76811263],
            [-1.59017894, 5.42377994, 1.53293698],
            [-0.77349930, 4.45245293, 0.95626051],
            [0.52282048, 3.81797397, 1.91420694],
            [3.72278594, -4.00725445, -2.96593944],
            [1.54648930, -4.59649704, -2.45399439],
            [0.07682973, -3.06919038, -1.61225759],
            [4.40941526, -1.85455891, -2.72715538],
            [3.93468611, 0.49322605, -2.03843703],
            [2.50140425, 2.05508514, -1.24004422],
            [-2.61330209, -2.36028263, 1.64664034],
            [-4.37125504, -1.93086070, 0.27844672],
            [-5.30252447, -1.00549091, -1.81425621],
            [-4.99604225, 0.07369089, -3.79595391],
            [-2.88613494, 0.77496485, -4.4226979],
            [-1.06724932, 0.39216806, -3.0909586],
            [0.70434526, -1.62389193, 0.92485864],
            [0.62249541, -3.76345476, 4.40295656],
            [2.56324636, -4.26135813, 5.49534309],
            [4.47853291, -3.08125872, 5.05488365],
            [4.43578910, -1.36373956, 3.51750179],
            [-0.50521367, 1.64703600, 0.10159614],
            [-2.02034538, 4.47929608, -2.01835861],
            [-3.38269071, 6.05574511, -1.05183405],
            [-3.11167675, 6.63358995, 1.14172011],
            [-1.47740803, 5.67620528, 2.4211357],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "xxv",
    "elements": [
        "O",
        "H",
        "O",
        "O",
        "O",
        "O",
        "O",
        "N",
        "N",
        "C",
        "C",
        "C",
        "H",
        "C",
        "C",
        "H",
        "C",
        "C",
        "H",
        "N",
        "N",
        "C",
        "C",
        "H",
        "C",
        "H",
        "C",
        "C",
        "H",
        "C",
        "C",
        "H",
        "H",
        "C",
        "H",
        "H",
        "C",
        "C",
        "H",
        "C",
        "C",
        "H",
        "C",
        "H",
        "C",
        "C",
        "H",
        "H",
        "C",
        "H",
        "H",
        "H",
        "C",
        "H",
        "H",
        "H",
    ],
    "xyz": np.array(
        [
            [0.109856, 2.583241, 3.821450],
            [0.868664, 3.006013, 3.759431],
            [0.441683, 1.937362, 1.737301],
            [-4.137107, 1.865107, 5.939288],
            [-5.729484, 0.890497, 4.905636],
            [-4.813431, -1.371183, 0.773325],
            [-2.969797, -1.063412, -0.208262],
            [-4.585626, 1.285967, 4.986797],
            [-3.721930, -0.864022, 0.696758],
            [-0.236548, 2.001343, 2.718888],
            [-1.612853, 1.397382, 2.765593],
            [-2.031292, 0.603409, 1.712034],
            [-1.476709, 0.449523, 0.981587],
            [-3.291929, 0.044125, 1.771756],
            [-4.155857, 0.261440, 2.815362],
            [-5.009223, -0.107555, 2.826081],
            [-3.700827, 1.047140, 3.837529],
            [-2.445325, 1.616352, 3.842123],
            [-2.166030, 2.140061, 4.558023],
            [2.309524, 3.948632, 3.675973],
            [4.084307, 4.909178, 5.015892],
            [4.985582, 4.706479, 3.921752],
            [6.248705, 5.279551, 3.977646],
            [6.494420, 5.785885, 4.718813],
            [7.141056, 5.104706, 2.943228],
            [7.977095, 5.510104, 2.992997],
            [6.825061, 4.343827, 1.832244],
            [5.561876, 3.762756, 1.790898],
            [5.330553, 3.237669, 1.059685],
            [4.634979, 3.945599, 2.810768],
            [3.238411, 3.354600, 2.693621],
            [2.899014, 3.510692, 1.797789],
            [3.283203, 2.396537, 2.834504],
            [3.498132, 6.251128, 5.025080],
            [4.195172, 6.902798, 4.855867],
            [3.129199, 6.431213, 5.904833],
            [2.412692, 6.409702, 3.993725],
            [1.908136, 7.665609, 3.676739],
            [2.251805, 8.411321, 4.114701],
            [0.910951, 7.847900, 2.731138],
            [0.443740, 6.728229, 2.068835],
            [-0.208340, 6.828338, 1.413423],
            [0.919690, 5.471495, 2.357492],
            [0.588580, 4.732402, 1.898857],
            [1.894045, 5.302441, 3.334485],
            [2.995113, 3.950011, 4.994453],
            [2.356103, 4.172567, 5.689680],
            [3.342599, 3.063927, 5.178214],
            [7.798674, 4.183322, 0.696758],
            [7.734765, 4.941996, 0.111022],
            [7.592569, 3.383833, 0.209027],
            [8.690665, 4.122926, 1.046668],
            [0.345940, 9.213843, 2.455498],
            [-0.525730, 9.285546, 2.852114],
            [0.278621, 9.346218, 1.506835],
            [0.924298, 9.881233, 2.831441],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "BIPHEN",
    "elements": ["C"] * 12 + ["H"] * 10,
    "xyz": np.array(
        [
            [3.522287, 0.022171, 0.016457],
            [2.842472, 1.196407, 0.046472],
            [1.414764, 1.185531, 0.030851],
            [0.738955, -0.016045, -0.014385],
            [1.486857, -1.160752, -0.046285],
            [2.876353, -1.189890, -0.034198],
            [-0.730003, 0.001127, -0.011393],
            [-1.433617, -1.183684, 0.030781],
            [-2.825556, -1.174273, 0.047609],
            [-3.562975, -0.014379, 0.015227],
            [-2.873925, 1.173271, -0.035666],
            [-1.455614, 1.160516, -0.045470],
            [4.640687, 0.037313, 0.023516],
            [3.383973, 2.122626, 0.090707],
            [0.962204, 2.134564, 0.062104],
            [1.007704, -2.125016, -0.073566],
            [3.459566, -2.083218, -0.066584],
            [-0.890536, -2.122135, 0.054618],
            [-3.366681, -2.110257, 0.113713],
            [-4.660789, -0.042737, 0.026237],
            [-3.424430, 2.086622, -0.058475],
            [-0.951057, 2.106547, -0.094314],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)
molecule = {
    "name": "ANULEN",
    "elements": ["C"] * 18 + ["H"] * 18,
    "xyz": np.array(
        [
            [-1.869782, -2.195520, 0.409199],
            [-2.270978, -2.442720, 1.719589],
            [-1.782410, -1.740960, 2.843459],
            [-0.868955, -0.711840, 2.762571],
            [-0.260498, -0.039360, 3.801747],
            [0.704539, 0.996960, 3.598099],
            [1.176140, 1.380960, 2.354323],
            [1.995002, 2.440320, 2.049803],
            [-2.346725, -2.824320, -0.732752],
            [1.869782, 2.195520, -0.409199],
            [2.270978, 2.442720, -1.719589],
            [1.782410, 1.740960, -2.843459],
            [0.868955, 0.711840, -2.762571],
            [0.260498, 0.039360, -3.801747],
            [-0.704539, -0.996960, -3.598099],
            [-1.176140, -1.380960, -2.354323],
            [-1.995002, -2.440320, -2.049803],
            [2.346725, 2.824320, 0.732752],
            [-1.188808, -1.334400, 0.295004],
            [-2.871375, -3.206400, 1.874704],
            [-2.109651, -2.049600, 3.711342],
            [-0.645378, -0.374400, 1.855671],
            [-0.465655, -0.259200, 4.748615],
            [1.036005, 1.536000, 4.415546],
            [0.937534, 0.806400, 1.655830],
            [2.260780, 3.004800, 2.826330],
            [-2.915514, -3.595200, -0.570976],
            [1.188808, 1.334400, -0.295004],
            [2.871375, 3.206400, -1.874704],
            [2.109651, 2.049600, -3.711342],
            [0.645378, 0.374400, -1.855671],
            [0.465655, 0.259200, -4.748615],
            [-1.036005, -1.536000, -4.415546],
            [-0.937534, -0.806400, -1.655830],
            [-2.260780, -3.004800, -2.826330],
            [2.915514, 3.595200, 0.570976],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "QUPHEN",
    "elements": ["C"] * 24 + ["H"] * 18,
    "xyz": np.array(
        [
            [-0.237192, -0.001402, 0.712733],
            [-2.361455, -0.040280, 7.580801],
            [-2.807282, -1.022591, 6.689173],
            [-2.372134, -1.008061, 5.351374],
            [0.170869, 1.009744, 1.604895],
            [-0.253537, 1.016588, 2.942338],
            [-1.085084, 0.014137, 3.446418],
            [-1.478465, -1.012493, 2.572608],
            [-1.058264, -1.012549, 1.227860],
            [-1.532259, 0.001515, 4.863509],
            [-1.114307, 1.002507, 5.762086],
            [-1.535804, 0.980235, 7.103627],
            [0.237192, 0.001402, -0.712733],
            [2.361455, 0.040280, -7.580801],
            [2.807282, 1.022591, -6.689173],
            [2.372134, 1.008061, -5.351374],
            [-0.170869, -1.009744, -1.604895],
            [0.253537, -1.016588, -2.942338],
            [1.085084, -0.014137, -3.446418],
            [1.478465, 1.012493, -2.572608],
            [1.058264, 1.012549, -1.227860],
            [1.532259, -0.001515, -4.863509],
            [1.114307, -1.002507, -5.762086],
            [1.535804, -0.980235, -7.103627],
            [-2.742286, 0.016830, 8.609809],
            [-3.531354, -1.709367, 7.068525],
            [-2.716147, -1.783980, 4.839454],
            [0.751149, 1.706562, 1.291828],
            [-0.008889, 1.923669, 3.472789],
            [-2.055778, -1.804176, 2.881221],
            [-1.405779, -1.739100, 0.522077],
            [-0.575572, 1.925913, 5.498732],
            [-1.234116, 1.740222, 7.822240],
            [2.742286, -0.016830, -8.609809],
            [3.531354, 1.709367, -7.068525],
            [2.716147, 1.783980, -4.839454],
            [-0.751149, -1.706562, -1.291828],
            [0.008889, -1.923669, -3.472789],
            [2.055778, 1.804176, -2.881221],
            [1.405779, 1.739100, -0.522077],
            [0.575572, -1.925913, -5.498732],
            [1.234116, -1.740222, -7.822240],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "DBPERY",
    "elements": ["C"] * 28 + ["H"] * 16,
    "xyz": np.array(
        [
            [-2.63477, 2.22938, 5.17206],
            [-2.19688, 1.31535, 6.15920],
            [-2.00579, 2.22233, 3.89378],
            [-2.47768, 3.15252, 2.93683],
            [-3.50840, 4.04097, 3.20108],
            [-4.10838, 4.03584, 4.44721],
            [-3.70215, 3.15136, 5.46502],
            [-4.32955, 3.16659, 6.75645],
            [-5.37879, 4.04390, 7.15239],
            [-5.94660, 4.01197, 8.42979],
            [-5.48787, 3.09743, 9.36150],
            [-4.46449, 2.22335, 9.00935],
            [-3.88541, 2.25248, 7.72568],
            [-2.85263, 1.36213, 7.41318],
            [-0.50166, 0.38562, 4.59679],
            [-0.93955, 1.29965, 3.60965],
            [-1.13064, 0.39267, 5.87507],
            [-0.65875, -0.53752, 6.83202],
            [0.37197, -1.42597, 6.56777],
            [0.97195, -1.42084, 5.32164],
            [0.56572, -0.53636, 4.30382],
            [1.19311, -0.55159, 3.01239],
            [2.24236, -1.42889, 2.61646],
            [2.81017, -1.39697, 1.33906],
            [2.35143, -0.48243, 0.40735],
            [1.32806, 0.39165, 0.75950],
            [0.74898, 0.36252, 2.04317],
            [-0.28381, 1.25287, 2.35567],
            [-1.08469, -0.59865, 7.82813],
            [0.70545, -2.12121, 7.33346],
            [1.77455, -2.13524, 5.16895],
            [2.64219, -2.16872, 3.30346],
            [3.60729, -2.08896, 1.08081],
            [2.78363, -0.44760, -0.58861],
            [0.97836, 1.10381, 0.01433],
            [-0.58003, 1.93503, 1.56415],
            [-2.05174, 3.21365, 1.94072],
            [-3.84189, 4.73621, 2.43539],
            [-4.91098, 4.75024, 4.59990],
            [-5.77862, 4.78372, 6.46539],
            [-6.74372, 4.70396, 8.68804],
            [-5.92006, 3.06260, 10.35746],
            [-4.11479, 1.51119, 9.75452],
            [-2.55640, 0.67997, 8.20470],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "TBZPER",
    "elements": ["C"] * 34 + ["H"] * 18,
    "xyz": np.array(
        [
            [5.623156, 2.615557, 2.025778],
            [0.115983, 1.289134, 2.629836],
            [-0.709893, 2.176080, 3.254566],
            [-0.235965, 3.393299, 3.671818],
            [1.055842, 3.784834, 3.356390],
            [1.899715, 2.916533, 2.642851],
            [3.279508, 3.308067, 2.307518],
            [4.231365, 2.309255, 2.031137],
            [3.771434, 0.974841, 1.700398],
            [3.683447, 4.653135, 2.205694],
            [2.749588, 5.729189, 1.932374],
            [6.523021, 1.595437, 1.586323],
            [3.171524, 7.007669, 1.725662],
            [4.539319, 7.356587, 1.789207],
            [4.961256, 8.675019, 1.577136],
            [6.279058, 8.997303, 1.656758],
            [7.236914, 8.033116, 1.894094],
            [6.874969, 6.685385, 2.092385],
            [7.834825, 5.659937, 2.442264],
            [9.190621, 5.966240, 2.733958],
            [10.046493, 5.023361, 3.204036],
            [9.606559, 3.747545, 3.449794],
            [6.049092, 0.348919, 1.211179],
            [8.310753, 3.379982, 3.150444],
            [7.420887, 4.325524, 2.593853],
            [6.031095, 3.947307, 2.279191],
            [5.061241, 4.978082, 2.197272],
            [5.497175, 6.357775, 2.050277],
            [4.689296, 0.002664, 1.261709],
            [4.239364, -1.283807, 0.839863],
            [2.927561, -1.563475, 0.907236],
            [1.981703, -0.631249, 1.329847],
            [2.395641, 0.647231, 1.759349],
            [1.467780, 1.616745, 2.324362],
            [-0.159976, 0.585970, 2.312112],
            [-1.679748, 1.784545, 3.529416],
            [-0.899865, 4.155060, 4.004088],
            [1.479778, 4.794300, 3.529416],
            [1.639754, 5.433540, 1.768536],
            [7.498875, 1.864450, 1.554168],
            [2.419637, 7.777420, 1.133088],
            [4.299355, 9.348885, 1.401048],
            [6.579013, 9.854950, 1.347456],
            [8.238764, 8.256850, 1.936968],
            [9.498575, 6.898465, 2.710224],
            [10.958356, 5.433540, 3.537072],
            [10.158476, 3.036390, 3.881592],
            [6.718992, -0.346255, 0.826848],
            [7.958806, 2.343880, 3.246144],
            [5.079238, -1.837815, 0.436392],
            [2.479628, -2.477055, 0.474672],
            [0.839874, -0.905590, 1.454640],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)

molecule = {
    "name": "TBZPYR",
    "elements": ["C"] * 28 + ["H"] * 16,
    "xyz": np.array(
        [
            [0.648186, 1.775038, 9.169800],
            [0.680394, 2.972654, 8.479600],
            [0.728706, 4.223735, 9.150080],
            [0.607926, 5.485509, 8.400720],
            [0.088572, 6.565502, 9.130360],
            [-0.370392, 7.741732, 8.459880],
            [-0.954162, 8.811032, 9.189520],
            [-0.269742, 7.795197, 7.099200],
            [0.402600, 6.800748, 6.369560],
            [0.938058, 5.624518, 7.000600],
            [0.644160, 6.961143, 4.969440],
            [1.372866, 6.073624, 4.279240],
            [1.932480, 4.972245, 4.930000],
            [1.743258, 4.747692, 6.251240],
            [0.648186, 1.775038, 10.550200],
            [0.680394, 2.972654, 11.240400],
            [0.728706, 4.223735, 10.569920],
            [0.607926, 5.485509, 11.319280],
            [0.088572, 6.565502, 10.589640],
            [-0.370392, 7.741732, 11.260120],
            [-0.954162, 8.811032, 10.530480],
            [-0.269742, 7.795197, 12.620800],
            [0.402600, 6.800748, 13.350440],
            [0.938058, 5.624518, 12.719400],
            [0.644160, 6.961143, 14.750560],
            [1.372866, 6.073624, 15.440760],
            [1.932480, 4.972245, 14.790000],
            [1.743258, 4.747692, 13.468760],
            [0.628056, 0.908905, 8.676800],
            [0.668316, 2.961961, 7.493600],
            [-1.368840, 9.570235, 8.696520],
            [-0.688446, 8.554400, 6.606200],
            [0.261690, 7.763118, 4.496160],
            [1.513776, 6.191247, 3.293240],
            [2.492094, 4.330665, 4.397560],
            [2.174040, 3.956410, 6.685080],
            [0.628056, 0.908905, 11.043200],
            [0.668316, 2.961961, 12.226400],
            [-1.368840, 9.570235, 11.023480],
            [-0.688446, 8.554400, 13.113800],
            [0.261690, 7.763118, 15.223840],
            [1.513776, 6.191247, 16.426760],
            [2.492094, 4.330665, 15.322440],
            [2.174040, 3.956410, 13.034920],
        ]
    ),
    "volume": None,
    "pubchem id": None,
}
molecules.append(molecule)


data = {}
data["YICMOP"] = "s1cccc1c1c(F)c(OC)c(c2sccc2)c(F)c1OC"
data["MERQIM"] = "s1c2c(c3c1SCCC3)cc1sc3SCCCc3c1c2"
for name in data.keys():
    smi = data[name]
    m = Chem.MolFromSmiles(smi)
    m2 = Chem.AddHs(m)
    AllChem.EmbedMolecule(m2)
    cids = AllChem.EmbedMultipleConfs(m2, numConfs=1)
    xyz = Chem.rdmolfiles.MolToXYZBlock(m2, 0)
    mol = mg.core.Molecule.from_str(xyz, fmt="xyz")
    molecule = {
        "name": name,
        "elements": [site.specie.name for site in mol],
        "xyz": mol.cart_coords,
        "volume": None,
        "pubchem id": None,
    }
    molecules.append(molecule)

for name in names:
    print(name)
    mol = pcp.get_compounds(name, "name", record_type="3d")[0]
    molecule = read_molecule(mol, name)
    molecules.append(molecule)

dicts = {
    "LEFCIK": 812440,
    "OFIXUX": 102393188,
    "HAHCOI": 10910901,
    "JAPWIH": 11449344,
    "WEXBOS": 12232323,
    "LAGNAL": 139087974,
    "LUFHAW": 102382626,
    "PAHYON01": 10006,
    "AXOSOW01": 7847,
}
for key in dicts.keys():
    mol = pcp.get_compounds(dicts[key], "cid", record_type="3d")[0]
    molecule = read_molecule(mol, key)
    molecules.append(molecule)

# print(molecules)
dumped = json.dumps(molecules, cls=NumpyEncoder, indent=2)
with open("molecules.json", "w") as f:
    f.write(dumped)
