# import numpy as np
# import matplotlib.pyplot as plt

# # Simulated radio signal data (for demonstration purposes)
# frequency = np.linspace(1e6, 2e6, 1000)
# signal_intensity = np.random.rand(1000)

# # Plot the radio signal spectrum
# plt.figure(figsize=(8, 4))
# plt.plot(frequency, signal_intensity)
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Signal Intensity')
# plt.title('Radio Signal Spectrum')
# plt.grid(True)
# plt.show()

# # Perform simple analysis (e.g., finding peak frequency)
# peak_frequency = frequency[np.argmax(signal_intensity)]
# print(f"Peak frequency: {peak_frequency} Hz")


import numpy as np
import matplotlib.pyplot as plt

# Simulated radio signal data (for demonstration purposes)
frequency = np.linspace(1e6, 2e6, 1000)
signal_intensity = np.random.rand(1000)
peak_frequency = frequency[np.argmax(signal_intensity)]
# Define some example spectral lines for elements (not accurate)
element_lines = {
    'Hydrogen': 1.42e6,
    'Helium': 1.86e6,
    'Oxygen': 2.06e6,
    # Add more element lines as needed
}

detected_elements = []
element_percentages = []

# Threshold for considering a spectral line as detected
threshold = 0.8

# Identify elements based on their spectral lines
for element, line_frequency in element_lines.items():
    if max(signal_intensity) >= threshold * max(signal_intensity) and abs(line_frequency - peak_frequency) < 1e4:
        detected_elements.append(element)
        element_percentages.append(signal_intensity[np.argmax(signal_intensity)] * 100)

# Print detected elements and their percentages
for element, percentage in zip(detected_elements, element_percentages):
    print(f"{element}: {percentage:.2f}%")

# Plot the radio signal spectrum
plt.figure(figsize=(8, 4))
plt.plot(frequency, signal_intensity)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Signal Intensity')
plt.title('Radio Signal Spectrum')
plt.grid(True)
plt.show()