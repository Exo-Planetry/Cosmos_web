import numpy as np
import matplotlib.pyplot as plt

# Generate synthetic direct imaging data
def generate_synthetic_direct_imaging_data(time, exoplanet_present=False):
    # Generate a synthetic direct imaging signal
    if exoplanet_present:
        # Simulate the presence of an exoplanet (e.g., a point source)
        imaging_data = np.random.normal(1.0, 0.1, len(time))
        imaging_data[time < 100] = np.random.normal(1.0, 0.1, np.sum(time < 100))
        imaging_data[time > 200] = np.random.normal(1.0, 0.1, np.sum(time > 200))
    else:
        # No exoplanet present (background noise)
        imaging_data = np.random.normal(1.0, 0.1, len(time))
    return imaging_data

# Confirm the presence of an exoplanet based on direct imaging data
def confirm_exoplanet_imaging(imaging_data):
    # Define criteria for confirmation (you can adjust these criteria as needed)
    signal_threshold = 1.2  # Threshold for signal presence

    max_signal = max(imaging_data)

    if max_signal > signal_threshold:
        return True
    else:
        return False

# Main module for user input and confirmation
if __name__ == "__main__":
    # User input for the time period
    start_time = float(input("Enter the start time (days): "))
    end_time = float(input("Enter the end time (days): "))

    # Calculate duration based on user input
    duration = end_time - start_time

    # Generate time range based on user input
    time_range = np.linspace(start_time, end_time, int(duration) + 1)

    # User input to simulate the presence of an exoplanet
    exoplanet_present = input("Is an exoplanet present in this source (yes/no)? ").strip().lower() == "yes"

    # Generate synthetic direct imaging data based on user input
    synthetic_imaging_data = generate_synthetic_direct_imaging_data(time_range, exoplanet_present)

    # Confirm the presence of an exoplanet based on the imaging data
    confirmation_result = confirm_exoplanet_imaging(synthetic_imaging_data)

    if confirmation_result:
        print("\nExoplanet presence confirmed!")
    else:
        print("\nNo exoplanet confirmed based on the provided imaging data.")
