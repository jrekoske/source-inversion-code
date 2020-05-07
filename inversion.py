import os
import conda

os.environ["PROJ_LIB"] = os.path.join(
    conda.__file__.split('lib')[0], 'Library', 'share')

from pycmt3d.data_container import DataContainer        # NOQA
from pycmt3d.constant import PARLIST                    # NOQA
from pycmt3d.cmt3d import Cmt3D                         # NOQA
from pycmt3d.config import Config, DefaultWeightConfig  # NOQA
from pycmt3d.source import CMTSource                    # NOQA

# load cmtsource
cmtfile = os.path.join('..', 'cmt_solutions', 'CMTSOLUTION-syn.txt')
cmtsource = CMTSource.from_CMTSOLUTION_file(cmtfile)

# load data and window from flexwin output file
npar = 9  # read 9 deriv synthetic
data_con = DataContainer(PARLIST[:npar])
flexwin_output = 'windows.txt'
asdf_file_dict = {
    'obsd': 'observed.h5',
    'synt': 'synthetic_perturbed.h5',
    'Mrr': os.path.join('kernels', 'Mrr.h5'),
    'Mtt': os.path.join('kernels', 'Mtt.h5'),
    'Mpp': os.path.join('kernels', 'Mpp.h5'),
    'Mrt': os.path.join('kernels', 'Mrt.h5'),
    'Mrp': os.path.join('kernels', 'Mrp.h5'),
    'Mtp': os.path.join('kernels', 'Mtp.h5'),
    'dep': os.path.join('kernels', 'depth.h5'),
    'lat': os.path.join('kernels', 'lat.h5'),
    'lon': os.path.join('kernels', 'lon.h5')}
data_con.add_measurements_from_asdf(flexwin_output, asdf_file_dict,
                                    file_format='txt')

# inversion shema
weight_config = DefaultWeightConfig(
    normalize_by_energy=False, normalize_by_category=False,
    comp_weight={"E": 1.0, "N": 1.0, "Z": 1.0},
    love_dist_weight=1.0, pnl_dist_weight=1.0,
    rayleigh_dist_weight=1.0, azi_exp_idx=0.5)

config = Config(
    npar=9,
    dlocation=0.05,
    ddepth=5000,
    dmoment=0.10e23,
    weight_data=True,
    weight_config=weight_config)

# source inversion
srcinv = Cmt3D(cmtsource, data_con, config)
srcinv.source_inversion()

# plot result
srcinv.plot_summary()
