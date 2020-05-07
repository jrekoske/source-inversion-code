import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs

data = np.genfromtxt('stations.txt', dtype=float)
lat, lon = data.T[2], data.T[3]

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
ax.set_global()
ax.stock_img()
ax.coastlines()
ax.scatter(lon, lat, color='r', marker='v', transform=ccrs.PlateCarree(),
           edgecolors='k')
plt.show()
