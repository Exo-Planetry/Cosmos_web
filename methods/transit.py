import numpy as np
import matplotlib.pyplot as plt

# Generate synthetic transit light curve data
def generate_synthetic_transit_data(time, depth, duration):
    # Generate a synthetic transit light curve
    transit_data = np.ones_like(time)
    mask = (time >= duration / 2) & (time <= (1 - duration / 2))
    
    # Check if the mask has at least one True value
    if np.any(mask):
        transit_data[mask] -= depth
    
    return transit_data


# Confirm the presence of an exoplanet based on the transit light curve
def confirm_exoplanet_transit(transit_curve, depth_threshold, duration_threshold):
    # Define criteria for confirmation (you can adjust these criteria as needed)
    transit_depth = 1.0 - min(transit_curve)
    transit_duration = np.sum(transit_curve < 1.0)

    if transit_depth < depth_threshold or transit_duration < duration_threshold:
        return True
    else:
        return False

# Add realistic noise to the synthetic transit data
def add_realistic_noise(transit_data, noise_level):
    noise = noise_level * np.random.randn(len(transit_data))
    noisy_transit_data = transit_data + noise
    return noisy_transit_data

# Main module for user input and confirmation
if __name__ == "__main__":
    # User input for the time period
    start_time = float(input("Enter the start time (days): "))
    end_time = float(input("Enter the end time (days): "))

    # Generate time range based on user input
    time_range = np.linspace(start_time, end_time, int(end_time - start_time) + 1)

    # User input for transit light curve (radio signal values)
    print("Enter transit light curve values (comma-separated, e.g., 1.0, 0.8, 0.6, 0.9, 1.0): ")
    transit_light_curve = [float(value.strip()) for value in input().split(',')]
    print(transit_light_curve)

    # User input for transit duration
    duration = float(input("Enter the transit duration (days): "))

    # Generate synthetic transit data based on user input
    synthetic_transit_data = generate_synthetic_transit_data(time_range, transit_light_curve, duration)

    # Ask if the user wants to add realistic noise
    add_noise = input("Do you want to add realistic noise? (yes/no): ").lower()
    if add_noise == 'yes':
        noise_level = float(input("Enter the noise level: "))
        synthetic_transit_data = add_realistic_noise(synthetic_transit_data, noise_level)

    # User input for threshold optimization
    depth_threshold = float(input("Enter depth threshold for transit confirmation: "))
    duration_threshold = float(input("Enter duration threshold for transit confirmation: "))

    # Confirm the presence of an exoplanet based on the transit data and user-defined thresholds
    confirmation_result = confirm_exoplanet_transit(synthetic_transit_data, depth_threshold, duration_threshold)

    # Visualize the synthetic transit data
    plt.plot(time_range, synthetic_transit_data, label='Synthetic Transit Data')
    plt.xlabel('Time (days)')
    plt.ylabel('Normalized Flux')
    plt.title('Synthetic Transit Light Curve')

    if confirmation_result:
        plt.axvline(time_range[np.argmin(synthetic_transit_data)], color='red', linestyle='--', label='Transit Confirmation')

    plt.legend()
    plt.show()

    if confirmation_result:
        print("\nExoplanet presence confirmed!")
    else:
        print("\nNo exoplanet confirmed based on the provided transit data.")
