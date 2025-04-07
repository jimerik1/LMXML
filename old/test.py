import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# Load data
with open('paste.txt', 'r') as f:
    data = json.load(f)

# Extract data into lists
years = [entry['year'] for entry in data['data']]
x_values = [entry['x'] for entry in data['data']]
y_values = [entry['y'] for entry in data['data']]
ut1_tai = [entry['UT1-TAI'] for entry in data['data']]
x_errors = [entry['x_er'] for entry in data['data']]
y_errors = [entry['y_er'] for entry in data['data']]

# Create a figure with a grid layout
plt.figure(figsize=(14, 10))
gs = GridSpec(3, 2, height_ratios=[2, 1, 1])

# Plot 1: X and Y values over time
ax1 = plt.subplot(gs[0, 0])
ax1.errorbar(years, x_values, yerr=x_errors, fmt='o-', label='x', color='blue', alpha=0.7, capsize=3)
ax1.errorbar(years, y_values, yerr=y_errors, fmt='o-', label='y', color='red', alpha=0.7, capsize=3)
ax1.set_title('Earth Orientation Parameters: X and Y Over Time')
ax1.set_xlabel('Year')
ax1.set_ylabel('Value (arcseconds)')
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()

# Plot 2: UT1-TAI over time
ax2 = plt.subplot(gs[0, 1])
ax2.plot(years, ut1_tai, 'o-', color='green', alpha=0.7)
ax2.set_title('UT1-TAI Over Time')
ax2.set_xlabel('Year')
ax2.set_ylabel('UT1-TAI (seconds)')
ax2.grid(True, linestyle='--', alpha=0.7)

# Plot 3: X vs Y polar motion
ax3 = plt.subplot(gs[1, :])
sc = ax3.scatter(x_values, y_values, c=years, cmap='viridis', s=50, alpha=0.8)
ax3.set_title('Polar Motion (X vs Y)')
ax3.set_xlabel('X (arcseconds)')
ax3.set_ylabel('Y (arcseconds)')
ax3.grid(True, linestyle='--', alpha=0.7)
ax3.set_aspect('equal')
plt.colorbar(sc, ax=ax3, label='Year')

# Plot 4: Error magnitudes
ax4 = plt.subplot(gs[2, :])
ax4.plot(years, x_errors, 'o-', label='x error', color='blue', alpha=0.7)
ax4.plot(years, y_errors, 'o-', label='y error', color='red', alpha=0.7)
ax4.set_title('Measurement Errors Over Time')
ax4.set_xlabel('Year')
ax4.set_ylabel('Error (arcseconds)')
ax4.grid(True, linestyle='--', alpha=0.7)
ax4.legend()

# Add overall title
plt.suptitle(f'Earth Orientation Parameters (Data from {data["date"]})', fontsize=16)

plt.tight_layout()
plt.subplots_adjust(top=0.92)
plt.savefig('earth_orientation_parameters.png', dpi=300, bbox_inches='tight')
plt.show()

# Create additional visualization for seasonal patterns
plt.figure(figsize=(14, 7))

# Compute the decimal part of the year to represent month
months = [12 * (year - int(year)) for year in years]

# Plot 5: Seasonal X and Y variations
plt.subplot(1, 2, 1)
sc_x = plt.scatter(months, x_values, c=years, cmap='viridis', s=50, alpha=0.8)
plt.title('X Value by Month')
plt.xlabel('Month (0-12)')
plt.ylabel('X (arcseconds)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.colorbar(sc_x, label='Year')

plt.subplot(1, 2, 2)
sc_y = plt.scatter(months, y_values, c=years, cmap='viridis', s=50, alpha=0.8)
plt.title('Y Value by Month')
plt.xlabel('Month (0-12)')
plt.ylabel('Y (arcseconds)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.colorbar(sc_y, label='Year')

plt.suptitle('Seasonal Patterns in Earth Orientation Parameters', fontsize=16)
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.savefig('seasonal_patterns.png', dpi=300, bbox_inches='tight')
plt.show()

# Create a 3D plot showing the evolution of polar motion over time
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D path
scatter = ax.scatter(x_values, y_values, years, c=years, cmap='viridis', s=30, alpha=0.8)
ax.plot(x_values, y_values, years, color='gray', alpha=0.5)

# Add points for each year start
year_starts = [2020, 2021, 2022, 2023, 2024, 2025]
for year in year_starts:
    # Find the closest point to January of each year
    idx = np.argmin([abs(y - year) for y in years])
    ax.scatter([x_values[idx]], [y_values[idx]], [years[idx]], 
               color='red', s=100, alpha=1, edgecolors='black')
    ax.text(x_values[idx], y_values[idx], years[idx], f' {int(years[idx])}', fontsize=10)

ax.set_title('3D Visualization of Polar Motion Over Time')
ax.set_xlabel('X (arcseconds)')
ax.set_ylabel('Y (arcseconds)')
ax.set_zlabel('Year')

# Add a colorbar
cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
cbar.set_label('Year')

plt.tight_layout()
plt.savefig('polar_motion_3d.png', dpi=300, bbox_inches='tight')
plt.show()