import sys
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from scipy import interpolate
from fuzzywuzzy import process  # for simple material fuzzy search
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import subprocess
from subprocess import Popen, PIPE, STDOUT
import random

param_name_rgx = re.compile(r"\[([A-Za-z0-9_]+)\]")  # get string between square brackets
sub_param_name_rgx = re.compile(r"<(.*?)>")  # get string between < and >

# material dictionary
materials = {
    'Pure Iron': """<BeginBlock>\n<BlockName> = "Pure Iron"\n<Mu_x> = 14872\n<Mu_y> = 14872\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 10.44\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 21\n0	0\n0.22706499999999999	13.898400000000001\n0.45412999999999998	27.796700000000001\n0.68119499999999999	42.397399999999998\n0.90825999999999996	61.415700000000001\n1.13533	82.382400000000004\n1.36239	144.66900000000001\n1.58935	897.75999999999999\n1.81236	4581.7399999999998\n2.01004	17736.200000000001\n2.1331600000000002	41339.300000000003\n2.1999900000000001	68321.800000000003\n2.2547899999999998	95685.5\n2.2999299999999998	123355\n2.3425099999999999	151083\n2.3787600000000002	178954\n2.4150100000000001	206825\n2.45126	234696\n2.4874999999999998	262568\n2.5237500000000002	290439\n2.5600000000000001	318310\n<EndBlock>\n""",  # noqa
    'Mu Metal': """<BeginBlock>\n<BlockName> = "Mu Metal"\n<Mu_x> = 82910\n<Mu_y> = 82910\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 1.8\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 31\n0	0\n0.080001000000000003	0.79577500000000001\n0.099140000000000006	1.0342340000000001\n0.12679699999999999	1.344149\n0.16478400000000001	1.7469330000000001\n0.21423800000000001	2.270413\n0.27441399999999999	2.9507569999999999\n0.34069300000000002	3.8349700000000002\n0.39480599999999999	4.9841449999999998\n0.43570300000000001	6.4776769999999999\n0.46653800000000001	8.4187550000000009\n0.49254100000000001	10.941490999999999\n0.51263599999999998	14.220181\n0.53089299999999995	18.481352000000001\n0.54834099999999997	24.019411000000002\n0.56394500000000003	31.216987\n0.57866499999999998	40.571362999999998\n0.59203600000000001	52.728839999999998\n0.60396099999999997	68.529386000000002\n0.61424699999999999	89.064670000000007\n0.62285900000000005	115.75348700000001\n0.63014599999999998	150.439784\n0.63628200000000001	195.52006\n0.64158999999999999	254.10893899999999\n0.64653300000000002	330.25436300000001\n0.65073700000000001	429.217266\n0.65423600000000004	557.835058\n0.65707000000000004	724.99402199999997\n0.65927800000000003	942.24327400000004\n0.66090599999999999	1224.592701\n0.66200000000000003	1591.55\n<EndBlock>\n""",  # noqa
    'Vanadium Permedur': """<BeginBlock>\n<BlockName> = "Vanadium Permedur"\n<Mu_x> = 6856\n<Mu_y> = 6856\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 2.5\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 12\n0	0\n0.59999999999999998	71.400000000000006\n1	119\n1.6000000000000001	175\n1.8	268\n2	493\n2.1000000000000001	804\n2.2000000000000002	1910\n2.2599999999999998	4775\n2.2999999999999998	15120\n2.3399999999999999	42971\n2.3900000000000001	79577\n<EndBlock>\n""",  # noqa
    'Air': """<BeginBlock>\n<BlockName> = "Air"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'Titanium': """<BeginBlock>\n<BlockName> = "Titanium"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 1.798\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'Copper': """<BeginBlock>\n<BlockName> = "Copper"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'Aluminum, 6061-T6': """<BeginBlock>\n<BlockName> = "Aluminum, 6061-T6"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 24.59\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N30': """<BeginBlock>\n<BlockName> = "N30"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 836420\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N33': """<BeginBlock>\n<BlockName> = "N33"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 878619\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N35': """<BeginBlock>\n<BlockName> = "N35"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 905659\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '12 AWG': """<BeginBlock>\n<BlockName> = "12 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 2.0530176819291301\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '14 AWG': """<BeginBlock>\n<BlockName> = "14 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 1.62813422596841\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '18 AWG': """<BeginBlock>\n<BlockName> = "18 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 1.0239652968433499\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '22 AWG': """<BeginBlock>\n<BlockName> = "22 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.64399170069399603\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '20 AWG': """<BeginBlock>\n<BlockName> = "20 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.812049969500513\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '36 AWG': """<BeginBlock>\n<BlockName> = "36 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.12704655216407401\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '34 AWG': """<BeginBlock>\n<BlockName> = "34 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.16020105336575399\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '32 AWG': """<BeginBlock>\n<BlockName> = "32 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.20200766618485599\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '30 AWG': """<BeginBlock>\n<BlockName> = "30 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.25472427515370799\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '28 AWG': """<BeginBlock>\n<BlockName> = "28 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.32119799004660898\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '26 AWG': """<BeginBlock>\n<BlockName> = "26 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.40501891210693097\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '24 AWG': """<BeginBlock>\n<BlockName> = "24 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 0.510714027632857\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '16 AWG': """<BeginBlock>\n<BlockName> = "16 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 1.2911827701741401\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    '10 AWG': """<BeginBlock>\n<BlockName> = "10 AWG"\n<Mu_x> = 1\n<Mu_y> = 1\n<H_c> = 0\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 58\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 3\n<LamFill> = 1\n<NStrands> = 1\n<WireD> = 2.5887801724742099\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N38': """<BeginBlock>\n<BlockName> = "N38"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 944771\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N40': """<BeginBlock>\n<BlockName> = "N40"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 969969\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N42': """<BeginBlock>\n<BlockName> = "N42"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 994529\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N55': """<BeginBlock>\n<BlockName> = "N55"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 922850\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 10\n0	0\n0.075300000000000006	5371\n0.15060000000000001	12456\n0.22589999999999999	22657\n0.30120000000000002	39606\n0.3765	72533\n0.45179999999999998	124321\n0.52710000000000001	180991\n0.60240000000000005	238036\n1.506	922850\n<EndBlock>\n""",  # noqa
    'N45': """<BeginBlock>\n<BlockName> = "N45"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 1030272\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 0\n<EndBlock>\n""",  # noqa
    'N52': """<BeginBlock>\n<BlockName> = "N52"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 956180\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 8\n0	0\n0.073200000000000001	7484\n0.1464	18446\n0.2195	37084\n0.29270000000000002	72766\n0.3659	124571\n0.43909999999999999	179757\n1.4636	956180\n<EndBlock>\n""",  # noqa
    'N48': """<BeginBlock>\n<BlockName> = "N48"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 1014538\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 6\n0	0\n0.070199999999999999	20713\n0.14050000000000001	58818\n0.2107	109648\n0.28100000000000003	162700\n1.405	1014538\n<EndBlock>\n""",  # noqa
    'N50': """<BeginBlock>\n<BlockName> = "N50"\n<Mu_x> = 1.05\n<Mu_y> = 1.05\n<H_c> = 987837\n<H_cAngle> = 0\n<J_re> = 0\n<J_im> = 0\n<Sigma> = 0.66700000000000004\n<d_lam> = 0\n<Phi_h> = 0\n<Phi_hx> = 0\n<Phi_hy> = 0\n<LamType> = 0\n<LamFill> = 1\n<NStrands> = 0\n<WireD> = 0\n<BHPoints> = 8\n0	0\n0.0717	11297\n0.14349999999999999	30636\n0.2152	67096\n0.28689999999999999	118309\n0.35859999999999997	172428\n0.4304	226773\n1.4346000000000001	987837\n<EndBlock>\n"""  # noqa
}


def find_num(line):
    return float(line.partition('=')[2])


def find_string(line):
    return line.partition('=')[2].lstrip()[:-1]


def parse_array(i, lines):
    line = lines[i]
    num = int(find_num(line))
    data = lines[i + 1:i + 1 + num]
    parsed_data = []
    for d in data:
        nums = d.split('\t')
        parsed_data.append([float(n) for n in nums])
    return parsed_data


class femm_file:
    def __init__(self):
        self.polys = []
        self.circuits = []
        self.path = None

    def polygon(self, verts, mat, circuit=None, turns=None, deg=0):  # [[x, y], [x1, y1]]
        ratios = process.extract(mat, list(materials))
        nmat = ratios[0][0]
        self.polys.append([verts, nmat, circuit, turns, deg])

    def circuit(self, name, re, im, t):
        self.circuits.append({
            "name": name,
            "re": re,
            "im": im,
            "type": t
        })

    def generate(self, path):
        try:
            with open(path, 'w+') as f:
                self.path = path
                # write header
                f.write("""[Format]      =  4.0\n[Frequency]   =  0\n[Precision]   =  1e-008\n[MinAngle]    =  30\n[DoSmartMesh] =  1\n[Depth]       =  1\n[LengthUnits] =  millimeters\n[ProblemType] =  planar\n[Coordinates] =  cartesian\n[ACSolver]    =  0\n[PrevType]    =  0\n[PrevSoln]    =  ""\n[Comment]     =  "Add comments here."\n[PointProps]   = 0\n[BdryProps]   = 0\n""")  # noqa
                # write materials
                f.write("[BlockProps]  = 32\n")
                for m in materials:
                    f.write(materials[m])
                # write circuits
                f.write(f"[CircuitProps]  = {len(self.circuits)}\n")
                for c in self.circuits:
                    f.write(f"""<BeginCircuit>\n<CircuitName> = "{c["name"]}"\n<TotalAmps_re> = {c["re"]}\n<TotalAmps_im> = {c["im"]}\n<CircuitType> = {c["type"]}\n<EndCircuit>\n""")  # noqa
                # write nodes and segments
                segments = []
                nodes = []
                for poly in self.polys:
                    p = poly[0]
                    segs = []
                    for i in range(len(p) - 1):
                        segs.append([p[i], p[i + 1]])
                    segs.append([p[0], p[-1]])
                    for seg in segs:
                        segments.append([0, 0])
                        if seg[0] in nodes:
                            segments[-1][0] = nodes.index(seg[0])
                        else:
                            nodes.append(seg[0])
                            segments[-1][0] = nodes.index(seg[0])
                        if seg[1] in nodes:
                            segments[-1][1] = nodes.index(seg[1])
                        else:
                            nodes.append(seg[1])
                            segments[-1][1] = nodes.index(seg[1])

                # generate boundary
                Xmax = max((np.array(nodes).T)[0])
                Xmin = min((np.array(nodes).T)[0])
                Ymax = max((np.array(nodes).T)[1])
                Ymin = min((np.array(nodes).T)[1])

                Xp = abs(Xmax - Xmin) * 1

                nodes.append([Xmax + Xp, Ymax + Xp])
                nodes.append([Xmax + Xp, Ymin - Xp])
                nodes.append([Xmin - Xp, Ymin - Xp])
                nodes.append([Xmin - Xp, Ymax + Xp])

                segments.append([len(nodes) - 1, len(nodes) - 2])
                segments.append([len(nodes) - 2, len(nodes) - 3])
                segments.append([len(nodes) - 3, len(nodes) - 4])
                segments.append([len(nodes) - 4, len(nodes) - 1])

                f.write(f"[NumPoints]  = {len(nodes)}\n")
                for n in nodes:
                    f.write(f"{n[0]:.20f}\t{n[1]:.20f}\t0\t0\n")
                f.write(f"[NumSegments]  = {len(segments)}\n")
                for s in segments:
                    f.write(f"{int(s[0])}\t{int(s[1])}\t-1\t0\t0\t0\n")
                # write useless tags
                f.write(f"[NumArcSegments] = 0\n[NumHoles] = 0\n")
                # find a point inside each polygon and stick the material marker to it
                marks = []
                for i, poly in enumerate(self.polys):
                    mymat = poly[1]
                    segms = poly[0]
                    mycirc = poly[2] if poly[2] is not None else 0
                    myturns = poly[3] if poly[3] is not None else 0
                    mydeg = poly[4]
                    mypoly = 0
                    try:
                        mypoly = Polygon(segms)
                    except ValueError:
                        raise RuntimeError(f"polygon {i + 1} with material {mymat} is invalid!")
                    if not mypoly.is_valid:
                        raise RuntimeError(f"polygon {i + 1} with material {mymat} is self intersecting or invalid!")

                    pXmax = max((np.array(nodes).T)[0])
                    pXmin = min((np.array(nodes).T)[0])
                    pYmax = max((np.array(nodes).T)[1])
                    pYmin = min((np.array(nodes).T)[1])

                    # find a random point inside the polygon so that we can append a marker to it
                    p = 0
                    px = 0
                    py = 0

                    while True:
                        px = random.uniform(pXmin, pXmax)
                        py = random.uniform(pYmin, pYmax)
                        p = Point(px, py)
                        if mypoly.contains(p):
                            break

                    marks.append([px, py, list(materials).index(mymat), mycirc, myturns, mydeg])

                # add Air marker for boundary
                marks.append([Xmin - Xp + 0.1,
                              Ymin - Xp + 0.1,
                              3, 0, 0, 0])

                f.write(f"[NumBlockLabels]  = {len(marks)}\n")
                for m in marks:
                    f.write(f"{m[0]:.20f}\t{m[1]:.20f}\t{int(m[2]) + 1}\t-1\t{int(m[3])}\t{m[5]}\t0\t{m[4]:.20f}\t0\n")

        except OSError:
            print("cannot create file")
        return

    def solve(self):
        # TODO add more checks
        if self.path is None:
            raise RuntimeError("fem file not found")
        p = Popen(["timeout", "2", "fmesher", self.path], stdout=subprocess.PIPE)
        mesherstdout = p.communicate()[0]
        if("No errors" not in mesherstdout.decode()):
            raise RuntimeError("mesher returned error")
        # GENERATE ANSWER
        p = Popen(["timeout", "2", 'fsolver'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        solverstdout = p.communicate(input=self.path[:-4].encode())[0]
        if("results written to disk" not in solverstdout.decode()):
            raise RuntimeError("solver returned error")

    def save_plot(self, output_path):
        f = 0
        if self.path is None:
            raise RuntimeError("fem file not found")

        with open(self.path[:-4] + ".ans", "r") as f:
            lines = f.readlines()

            blocks = {}

            for i, line in enumerate(lines):
                params = param_name_rgx.findall(line)
                if len(params):
                    param = params[0]
                    if param == "Format":
                        blocks["Format"] = find_num(line)
                    elif param == "Frequency":
                        blocks["Frequency"] = find_num(line)
                    elif param == "Precision":
                        blocks["Precision"] = find_num(line)
                    elif param == "MinAngle":
                        blocks["MinAngle"] = find_num(line)
                    elif param == "Depth":
                        blocks["Depth"] = find_num(line)
                    elif param == "LengthUnits":
                        blocks["LengthUnits"] = find_string(line)
                    elif param == "ProblemType":
                        blocks["ProblemType"] = find_string(line)
                    elif param == "Coordinates":
                        blocks["Coordinates"] = find_string(line)
                    elif param == "Comment":
                        blocks["Comment"] = find_string(line)
                    elif param == "PointProps":
                        blocks["PointProps"] = find_num(line)
                    elif param == "BdryProps":
                        blocks["BdryProps"] = find_num(line)
                    elif param == "BlockProps":
                        num = find_num(line)
                        idx = i
                        block_idx = 0
                        sub = {}
                        temp_dict = {}
                        while(block_idx < num):
                            line = lines[idx]
                            sub_params = sub_param_name_rgx.findall(line)
                            if len(sub_params):
                                sub_param = sub_params[0]
                                if sub_param == "EndBlock":
                                    block_idx += 1
                                    sub[[*sub.keys()][-1]] = temp_dict
                                elif sub_param == "BlockName":
                                    sub[find_string(line)[1:-1]] = {}
                            idx += 1
                        blocks["BlockProps"] = sub
                    elif param == "CircuitProps":
                        blocks["CircuitProps"] = find_num(line)
                    elif param == "NumPoints":
                        blocks["NumPoints"] = parse_array(i, lines)
                    elif param == "NumSegments":
                        blocks["NumSegments"] = parse_array(i, lines)
                    elif param == "NumArcSegments":
                        blocks["NumArcSegments"] = parse_array(i, lines)
                    elif param == "NumHoles":
                        blocks["NumHoles"] = parse_array(i, lines)
                    elif param == "NumBlockLabels":
                        blocks["NumBlockLabels"] = parse_array(i, lines)
                    elif param == "Solution":
                        # nodes
                        node_num = int(lines[i + 1])
                        node_data = lines[i + 2:i + 2 + node_num]
                        parsed_node_data = []
                        for d in node_data:
                            nums = d.split('\t')
                            parsed_node_data.append([float(n) for n in nums])
                        # elems
                        elem_ind = i + 2 + node_num
                        elem_num = int(lines[elem_ind])
                        elem_data = lines[elem_ind + 1:elem_ind + 1 + elem_num]
                        parsed_elem_data = []
                        for d in elem_data:
                            nums = d.split('\t')
                            parsed_elem_data.append([float(n) for n in nums])
                        # circuits
                        circuit_ind = elem_ind + 1 + elem_num
                        circuit_num = int(lines[circuit_ind])
                        circuit_data = lines[circuit_ind + 1:circuit_ind + 1 + circuit_num]
                        parsed_circuit_data = []
                        for d in circuit_data:
                            nums = d.split('\t')
                            parsed_circuit_data.append([float(n) for n in nums])
                        blocks["Solution"] = [parsed_node_data, parsed_elem_data, parsed_circuit_data]

            # ##### plot B
            nodes = np.array(blocks["Solution"][0])
            X, Y, U, V = nodes[:, 0], nodes[:, 1], nodes[:, 2], nodes[:, 3]

            N = 100  # grid dimension

            Xmax, Xmin, Ymax, Ymin = max(X), min(X), max(Y), min(Y)

            Xi = np.linspace(Xmin, Xmax, N)  # grid of coordinates
            Yi = np.linspace(Ymin, Ymax, N)
            dXi, dYi = [c[1] - c[0] for c in (Xi, Yi)]  # get spacing between uniform coordinates (it's a number not an array)
            xx, yy = np.meshgrid(Xi, Yi)     # grids of meshed coordinates
            points = np.transpose(np.vstack((X, Y)))  # array of non uniform point coordinates

            Ui = interpolate.griddata(points, U, (xx, yy), method='linear')  # grid of vectors

            Ux = interpolate.RegularGridInterpolator([Xi, Yi], Ui)  # function for vector U tip coordinate

            A = Ux((xx, yy))
            Ax_grad, Ay_grad = np.gradient(A)

            Bv = np.transpose(np.array([Ay_grad, - Ax_grad]), axes=(0, 2, 1))
            Bx, By = Bv
            B = np.linalg.norm(Bv, axis=0)
            Bmax = np.amax(B)
            Bmin = np.amin(B)
            nBmax = Bmax + ((Bmax - Bmin) * 0)
            nBmin = Bmin - ((Bmax - Bmin) * 0.23)
            Bxs, Bys = (B > Bmax * 0.1) * Bv

            fig, ax = plt.subplots()
            # plt.imshow(B, cmap='jet': """""", interpolation='none')
            ax.contourf(Xi, Yi, B, 20, vmin=nBmin, vmax=nBmax, cmap='gist_ncar')
            ax.streamplot(Xi, Yi, Bxs, Bys, density=1.5, arrowstyle='->', maxlength=1000, linewidth=0.5, color='black', arrowsize=1)  # noqa
            # plt.quiver(xx, yy, Bx, By)

            # ##### plot geometry
            segs = []

            for seg in blocks['NumSegments']:
                sp = blocks['NumPoints'][int(seg[0])]
                ep = blocks['NumPoints'][int(seg[1])]
                segs.append([(sp[0], sp[1]), (ep[0], ep[1])])

            lc = mc.LineCollection(segs, linewidths=0.5, color='black')
            ax.add_collection(lc)

            plt.gca().set_aspect('equal')
            plt.savefig(output_path)
            return output_path
