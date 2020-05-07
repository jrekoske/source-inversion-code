import os
import pyasdf
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 18

for file in os.listdir('kernels'):
    ds = pyasdf.ASDFDataSet(os.path.join('kernels', file))
    st = ds.waveforms.II_AAK.synthetic
    st.plot(outfile='%s.png' % file)