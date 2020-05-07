import matplotlib.pyplot as plt
import pyasdf

ds1 = pyasdf.ASDFDataSet('observed.h5')
ds2 = pyasdf.ASDFDataSet('synthetic_more_perturbed.h5')

st1 = ds1.waveforms.II_AAK.synthetic
st2 = ds2.waveforms.II_AAK.synthetic

for st in [st1, st2]:
    st.filter(type='bandpass', freqmin=1 / 80, freqmax=1 / 40, zerophase=True)
    st.rotate('NE->RT', back_azimuth=351)

plt.figure(figsize=(5, 6))
plt.subplot(3, 1, 1)
plt.plot(st1[0].times(), st1[0].data, label='Observed')
plt.plot(st2[0].times(), st2[0].data, color='k', label='Synthetic')
plt.xlabel('Time (s)')
plt.ylabel('Displacement (m)')
plt.title(st1[0].id)
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(st1[1].times(), st1[1].data, label='Observed')
plt.plot(st2[1].times(), st2[1].data, color='k', label='Synthetic')
plt.title(st1[1].id)

plt.subplot(3, 1, 3)
plt.plot(st1[2].times(), st1[2].data, label='Observed')
plt.plot(st2[2].times(), st2[2].data, color='k', label='Synthetic')
plt.title(st1[2].id)

plt.tight_layout()
plt.savefig('processing.png', dpi=300, bbox_inches='tight')
