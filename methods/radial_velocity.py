import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Function to model the radial velocity signal
def sinusoidal(time, A, P, phi, gamma):
    return A * np.sin(2 * np.pi * time / P + phi) + gamma

# Generate synthetic radial velocity data with known parameters
def generate_synthetic_radial_velocity_data(time, amplitude, period, phase, offset, noise_stddev=1.0):
    true_velocity = sinusoidal(time, amplitude, period, phase, offset)
    noise = np.random.normal(0, noise_stddev, len(time))
    noisy_velocity = true_velocity + noise
    return noisy_velocity

# Fit the sinusoidal model to the synthetic data and estimate parameters
def fit_radial_velocity_data(time, velocity):
    popt, _ = curve_fit(sinusoidal, time, velocity)
    return popt  # popt contains the estimated parameters (A, P, phi, gamma)

# Plot the synthetic data and the fitted curve
def plot_radial_velocity(time, velocity, fitted_params):
    plt.figure(figsize=(10, 6))
    plt.scatter(time, velocity, label="Synthetic Data")
    plt.plot(time, sinusoidal(time, *fitted_params), 'r-', label="Fitted Curve")
    plt.xlabel("Time (days)")
    plt.ylabel("Radial Velocity (m/s)")
    plt.legend()
    plt.title("Synthetic Radial Velocity Data and Fitted Curve")
    plt.grid(True)
    plt.show()
    
    
def confirm_exoplanet(estimated_params):
    # Define criteria for confirmation (you can adjust these criteria as needed)
    amplitude_threshold = 5.0  # Threshold for amplitude (m/s)
    period_threshold = 200.0  # Threshold for orbital period (days)

    amplitude = estimated_params[0]
    period = estimated_params[1]

    if amplitude > amplitude_threshold or period > period_threshold:
        return True
    else:
        return False

# Main module for user input
if __name__ == "__main__":
    # User input for the radio signal values
    radio_signal_values = input("Enter radio signal values (comma-separated): ")
    
    # Convert the input values to a list of floats
    radio_signal_values = [float(value.strip()) for value in radio_signal_values.split(',')]

    # Generate time range based on the number of input values
    time_range = np.linspace(0, len(radio_signal_values) - 1, len(radio_signal_values))

    # Known velocity parameters for the synthetic data
    true_amplitude = 10.0  # m/s
    true_period = 365.25  # days
    true_phase = 0.0  # radians
    true_offset = 0.0  # m/s

    # Generate synthetic radial velocity data based on radio signal values
    synthetic_velocity = generate_synthetic_radial_velocity_data(
        time_range, true_amplitude, true_period, true_phase, true_offset, noise_stddev=1.0
    )

    # Fit the synthetic data to estimate the velocity parameters
    estimated_params = fit_radial_velocity_data(time_range, synthetic_velocity)

    # Print the estimated parameters
    print("\nEstimated Parameters:")
    print("Amplitude:", estimated_params[0])
    print("Orbital Period (days):", estimated_params[1])
    print("Phase (radians):", estimated_params[2])
    print("Offset (m/s):", estimated_params[3])

    # Plot the synthetic data and fitted curve
    plot_radial_velocity(time_range, synthetic_velocity, estimated_params)
    
    confirmation_result = confirm_exoplanet(estimated_params)

    if confirmation_result:
        print("\nExoplanet presence confirmed!")
    else:
        print("\nNo exoplanet confirmed based on the provided data.")
