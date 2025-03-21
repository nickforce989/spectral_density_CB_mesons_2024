import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.legend_handler import HandlerTuple
import matplotlib.patches as mpatches

# Define constants and configuration
w0_values = {'M1': 2.5210, 'M2': 2.5290, 'M3': 2.5237, 'M4': 2.3664, 'M5': 2.6927}
files = [
    ('M1', ['M1_ground.txt', 'M1_first.txt']),
    ('M2', ['M2_ground.txt', 'M2_first.txt', 'M2_second.txt']),
    ('M3', ['M3_ground.txt', 'M3_first.txt', 'M3_second.txt']),
    ('M4', ['M4_ground.txt', 'M4_first.txt', 'M4_second.txt']),
    ('M5', ['M5_ground.txt', 'M5_first.txt', 'M5_second.txt']),
    # CB channels
    ('M1', ['CB_M1_ground.txt', 'CB_M1_first.txt', 'CB_M1_second.txt']),
    ('M2', ['CB_M2_ground.txt', 'CB_M2_first.txt', 'CB_M2_second.txt']),
    ('M3', ['CB_M3_ground.txt', 'CB_M3_first.txt', 'CB_M3_second.txt']),
    ('M4', ['CB_M4_ground.txt', 'CB_M4_first.txt', 'CB_M4_second.txt']),
    ('M5', ['CB_M5_ground.txt', 'CB_M5_first.txt', 'CB_M5_second.txt'])
]

plt.style.use("paperdraft.mplstyle")
output_file = '../../../plots/final_spectrum_detail.pdf'
spacing = 0.
colors = [cm.tab10(i) for i in np.linspace(0, 0.5, 6)]

def process_file(file_name, w0):
    values, errors = [], []
    
    with open(file_name, 'r') as file:
        lines = file.readlines()

        # Check if there are enough lines in the file
        if len(lines) < 3:  # Make sure there are at least 3 lines in the file
            print(f"Warning: {file_name} does not have enough lines. Skipping this file.")
            return values, errors
        
        # Determine the line to process
        line_idx = 1 if file_name.startswith('CB_') else 2  # Second line for 'CB_' files, third line otherwise

        # Make sure the chosen line exists
        if line_idx >= len(lines):
            print(f"Warning: {file_name} does not have enough lines for line index {line_idx}. Skipping this file.")
            return values, errors

        # Process the selected line
        data = list(map(float, lines[line_idx].strip().split()))
        measurements, errors_data = data[::2], data[1::2]

        # Calculate the error values
        min_err_idx = errors_data.index(min(errors_data))
        stat = errors_data[min_err_idx]
        sys = max(abs(measurements[i] - measurements[j]) for i in range(len(measurements)) for j in range(i+1, len(measurements)))
        
        # Apply w0 scaling
        value = measurements[min_err_idx] * w0
        total_err = math.sqrt(stat**2 + sys**2) * w0
        
        values.append(value)
        errors.append(total_err)
    
    return values, errors



# Plotting setup
fig, ax = plt.subplots(figsize=(16, 9))

# Define x_labels: Place 'η'' first, followed by the rest of the labels
x_labels = ['T', '$\Sigma^{+}_{\\rm CB}$']

hatches = [r'//////', '++++']  # Define different hatch patterns for M4 and M5

# Offsets and alpha values for ensembles
offsets = {'M1': -0.05, 'M2': 0.0, 'M3': 0.05, 'M4': -0.25, 'M5': 0.50}
alpha_values = {'M1': 0.4, 'M2': 0.6, 'M3': 0.85, 'M4': 0.7, 'M5': 0.7}

# Define the new color scheme for CB channels
cb_colors = [cm.RdBu(i) for i in np.linspace(0, 0.3, 6)]  # Use a range from the RdBu colormap

# Define hatch colors based on the same colormap as the bars
hatch_colors = [cm.tab10(i) for i in np.linspace(0, 0.5, 6)]

# Additional eta files for each ensemble
eta_files = {
    'M1': ['eta_M1_ground.txt', 'eta_M1_first.txt'],
    'M2': ['eta_M2_ground.txt', 'eta_M2_first.txt'],
    'M3': ['eta_M3_ground.txt', 'eta_M3_first.txt'],
    'M4': ['eta_M4_ground.txt', 'eta_M4_first.txt'],
    'M5': ['eta_M5_ground.txt', 'eta_M5_first.txt'],
}

# Plot eta channels first
for ensemble, file_list in eta_files.items():
    w0 = w0_values[ensemble]
    ensemble_offset = offsets[ensemble]

    for idx, file_name in enumerate(file_list):
        values, errors = process_file(file_name, w0)

        color = 'burlywood'  # Set color for eta
        alpha = alpha_values.get(ensemble, 0.6)
        hatch = None
        hatch_color = None

        if ensemble == 'M4':
            hatch = hatches[0]
            hatch_color = 'burlywood'
            color = 'none'
        elif ensemble == 'M5':
            hatch = hatches[1]
            hatch_color = 'burlywood'
            color = 'none'

        # Plot the eta channel at the first position
        for i, (val, err) in enumerate(zip(values, errors)):
            x_pos = 0.3 - 0.2 + spacing * 0.1 + ensemble_offset
            factor = 0.15 if ensemble in ['M4', 'M5'] else 0.4
            rect = plt.Rectangle((x_pos, val - err), factor, 2 * err, color=color, alpha=alpha, hatch=hatch)
            if hatch_color:
                rect.set_edgecolor(hatch_color)
            ax.add_patch(rect)
            ax.plot([x_pos + 0.2, x_pos + 0.2], [val - err, val + err], color='red', alpha=0.0)

# Plot the rest of the channels
for ensemble, file_list in files:
    w0 = w0_values[ensemble]
    ensemble_offset = offsets[ensemble]

    for idx, file_name in enumerate(file_list):
        values, errors = process_file(file_name, w0)
        for i, (val, err) in enumerate(zip(values, errors)):
            if 'CB' in file_name:
                x_pos = 2.3 + i + ensemble_offset
                color = cb_colors[1]
            else:
                x_pos = 0.3 + i + ensemble_offset
                color = colors[2]
                if i >= 6:
                    x_pos += 0.4

            hatch = None
            hatch_color = None
            alpha = alpha_values.get(ensemble, 0.6)

            if ensemble == 'M4':
                hatch = hatches[0]
                hatch_color = colors[2]
                color = 'none'
                if 'CB' in file_name:
                    hatch_color = cb_colors[1]
            elif ensemble == 'M5':
                hatch = hatches[1]
                hatch_color = colors[2]
                color = 'none'
                if 'CB' in file_name:
                    hatch_color = cb_colors[1]

            rect = plt.Rectangle((x_pos - 0.2, val - err), 0.15 if ensemble in ['M4', 'M5'] else 0.4, 2 * err, color=color, alpha=alpha, hatch=hatch)
            if hatch_color:
                rect.set_edgecolor(hatch_color)
            ax.add_patch(rect)

# Define sector boundaries and labels
sector_boundaries = [7.0, 13.4, 19.8]
sector_labels = ['Fundamental', 'Antisymmetric', 'Chimera baryons']

# Add vertical lines for sector separation
for boundary in sector_boundaries:
    ax.axvline(boundary, color='black', linestyle='-', alpha=0.7)

# Optionally shade sectors to distinguish regions
ax.axvspan(-0.5, 7.5, color='none')  # First sector
ax.axvspan(0.5, 7.5, color='none')  # Second sector
ax.axvspan(7.5, 13.5, color='none')  # Third sector



# Create custom legend handles with color patches for each group
legend_handles = [
    mpatches.Patch(color='black', alpha=0.4),
    mpatches.Patch(color='black', alpha=0.6),
    mpatches.Patch(color='black', alpha=0.85),
    mpatches.Patch(color='black', alpha=0.7,fill=False),
    mpatches.Patch(color='black', alpha=0.7,fill=False),
]

for i, hatch in enumerate(hatches):
    legend_handles[-(i+1)].set_hatch(hatch)

# Plot the legend with custom handles and labels
#plt.legend(handles=legend_handles, labels=legend_labels, handlelength=1.5, handletextpad=3.4)
plt.legend([(legend_handles[0]), (legend_handles[1]), (legend_handles[2]), (legend_handles[3]), (legend_handles[4])], ['M1', 'M2', 'M3', 'M4', 'M5'],
               handler_map={tuple: HandlerTuple(ndivide=None)}, handlelength=3.0)

ciao = [0.3, 2.3]
# Adjust x-ticks and labels
ax.set_xticks(ciao)
ax.set_xticklabels(x_labels, ha='right', fontsize=14, rotation=45)

# Set y-label and axis limits
ax.set_ylabel('$\hat{m}$', fontsize=16)
ax.set_ylim(0.5, 3.7)
ax.set_xlim(-0.5, 3.2)
# Save and show the plot
plt.tight_layout()
plt.savefig(output_file)
#plt.show()

