import copy
import numpy as np

import pyflex
import pyasdf
from obspy.geodetics import calc_vincenty_inverse

import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 200


def get_time_array(synt, origin):
    """Returns time array in relation to origin time"""
    dt = synt.stats.delta
    npts = synt.stats.npts
    start = synt.stats.starttime - origin.time
    return np.arange(start, start+npts*dt, dt)


def user_func(config, sta_info, origin, obsd_tr, synt_tr):

    npts = synt_tr.stats.npts

    base_water_level = config.stalta_waterlevel
    base_cc = config.cc_acceptance_level
    base_tshift = config.tshift_acceptance_level
    base_dlna = config.dlna_acceptance_level
    base_s2n = config.s2n_limit

    # turn parameters into arrays
    stalta_waterlevel = np.ones(npts) * base_water_level
    cc = np.ones(npts) * base_cc
    tshift = np.ones(npts) * base_tshift
    dlna = np.ones(npts) * base_dlna
    s2n = np.ones(npts) * base_s2n

    trace_info = sta_info.get_coordinates(synt_tr.id[:-1]+"Z")

    times = get_time_array(synt_tr, origin)
    dist_km = calc_vincenty_inverse(
        origin.latitude, origin.longitude,
        trace_info["latitude"], trace_info["longitude"])[0] / 1000

    # rayleigh
    r_vel = 3.2
    r_time = dist_km/r_vel
    r_index = None

    # Find index in time array of Rayleigh wave arrival
    r_index = (np.abs(times - r_time)).argmin() + 1
    s2n[r_index:] = 10 * base_s2n
    cc[r_index:] = 0.95
    tshift[r_index:] = base_tshift/3.0
    dlna[r_index:] = base_dlna/3.0
    stalta_waterlevel[r_index:] = base_water_level * 2.0

    # Check event depth
    # origin.depth is in meters
    if origin.depth > 70000 and origin.depth < 300000:  # intermediate
        tshift[:] = base_tshift * 1.4
    elif origin.depth > 300000:  # deep
        tshift[:] = base_tshift * 1.7

    # replace config vars
    new_config = copy.deepcopy(config)
    new_config.stalta_waterlevel = stalta_waterlevel
    new_config.tshift_acceptance_level = tshift
    new_config.dlna_acceptance_level = dlna
    new_config.cc_acceptance_level = cc
    new_config.s2n_limit = s2n
    new_config.signal_end_index = r_index

    return new_config


conf = pyflex.Config(
    40, 80,
    stalta_waterlevel=0.08,
    tshift_acceptance_level=10.0,
    tshift_reference=0.0,
    dlna_acceptance_level=0.8,
    cc_acceptance_level=0.85,
    check_global_data_quality=True,
    snr_integrate_base=3.5,
    snr_max_base=12.0,
    c_0=0.7,
    c_1=3.0,
    c_2=0.0,
    c_3a=1.0,
    c_3b=2.0,
    c_4a=3.0,
    c_4b=10.0
)

ds_obsd = pyasdf.ASDFDataSet("observed.h5")
ds_synt = pyasdf.ASDFDataSet("synthetic_more_perturbed.h5")
event = ds_synt.events[0]
origin = event.preferred_origin()
synt_tag = "synthetic"
obsd_tag = "synthetic"

# Set up the textfile
num_channels = 0
text = []

for idx, sta in enumerate(ds_synt.waveforms.list()):
    print('%s/%s' % (idx + 1, len(ds_synt.waveforms.list())))
    for channel in "ENZ":
        sta_info = ds_synt.waveforms[sta].StationXML
        synt_tr = ds_synt.waveforms[sta][synt_tag].select(
            channel="*"+channel)[0]
        obsd_tr = ds_obsd.waveforms[sta][obsd_tag].select(
            channel="*" + channel)[0]

        # Filter both traces
        synt_tr.detrend('demean').detrend('linear').taper(0.05).filter(
            type='bandpass', freqmin=1/80, freqmax=1/40, zerophase=True)
        obsd_tr.detrend('demean').detrend('linear').taper(0.05).filter(
            type='bandpass', freqmin=1/80, freqmax=1/40, zerophase=True)

        new_conf = user_func(conf, sta_info, origin, obsd_tr, synt_tr)
        try:
            wins = pyflex.select_windows(obsd_tr, synt_tr, new_conf,
                                         event=event, station=sta_info,
                                         plot=False)

            if wins:
                num_channels += 1
                text.append(obsd_tr.id)
                text.append(synt_tr.id)
                text.append(len(wins))
                for win in wins:
                    text.append('%.2f %.2f' % (win.left * obsd_tr.stats.delta,
                                               win.right*obsd_tr.stats.delta))
        except Exception:
            continue

text.insert(0, num_channels)
with open('windows.txt', 'w') as f:
    for item in text:
        f.write("%s\n" % item)
