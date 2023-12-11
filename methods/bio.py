import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Synthetic data for exoplanet biosignature
exoplanet_data = np.random.rand(100) * 10

# Earth's biosignature data (hypothetical values for demonstration)
earth_data = np.array([2.5, 3.0, 4.2, 5.1, 6.0, 5.7, 4.9, 3.5, 2.7, 2.1])

# Streamlit interface
st.title("Exoplanet Biosignature Analysis")

# Display synthetic data and Earth's biosignature data
st.subheader("Synthetic Exoplanet Data")
st.line_chart(exoplanet_data)

st.subheader("Earth's Biosignature Data")
st.line_chart(earth_data)

# Data analysis
st.header("Data Analysis")

# Calculate mean and standard deviation for exoplanet data
exoplanet_mean = np.mean(exoplanet_data)
exoplanet_std = np.std(exoplanet_data)

# Calculate mean and standard deviation for Earth's data
earth_mean = np.mean(earth_data)
earth_std = np.std(earth_data)

# Compare exoplanet data with Earth's data
st.write(f"Exoplanet Mean: {exoplanet_mean}")
st.write(f"Exoplanet Standard Deviation: {exoplanet_std}")

st.write(f"Earth's Mean: {earth_mean}")
st.write(f"Earth's Standard Deviation: {earth_std}")

# Conclusion
st.header("Conclusion")

if exoplanet_mean > earth_mean:
    st.write("The synthetic exoplanet data shows a higher biosignature level than Earth's data.")
elif exoplanet_mean < earth_mean:
    st.write("The synthetic exoplanet data shows a lower biosignature level than Earth's data.")
else:
    st.write("The synthetic exoplanet data is similar to Earth's data in terms of biosignature.")

# Plot histograms for comparison
fig, ax = plt.subplots()
ax.hist(exoplanet_data, bins=20, alpha=0.5, label="Exoplanet Data")
ax.hist(earth_data, bins=20, alpha=0.5, label="Earth's Data")
ax.set_xlabel("Biosignature Level")
ax.set_ylabel("Frequency")
ax.legend()
st.pyplot(fig)


# Synthetic data for exoplanet chemical composition
exoplanet_composition = {
    'Oxygen': np.random.uniform(0.1, 0.5, 100),
    'Carbon': np.random.uniform(0.05, 0.3, 100),
    'Nitrogen': np.random.uniform(0.01, 0.1, 100),
    'Water': np.random.uniform(0.2, 0.9, 100),
}

# Earth's chemical composition (hypothetical values for demonstration)
earth_composition = {
    'Oxygen': 0.21,
    'Carbon': 0.04,
    'Nitrogen': 0.78,
    'Water': 0.7,
}

# Streamlit interface
st.title("Exoplanet Chemical Composition and Habitability Analysis")

# Display exoplanet and Earth's chemical composition
st.subheader("Synthetic Exoplanet Chemical Composition")
st.line_chart(pd.DataFrame(exoplanet_composition))

st.subheader("Earth's Chemical Composition")
st.bar_chart(pd.Series(earth_composition))

# Data analysis
st.header("Chemical Composition Analysis")

# Compare exoplanet composition with Earth's composition
habitability_conditions = []

for element in exoplanet_composition:
    exoplanet_mean = np.mean(exoplanet_composition[element])
    earth_value = earth_composition.get(element, None)

    if earth_value is None:
        st.write(f"Earth's composition data for {element} is not available.")
    else:
        st.write(f"{element} in Exoplanet Mean: {exoplanet_mean}")
        st.write(f"{element} in Earth: {earth_value}")

        if exoplanet_mean > earth_value:
            habitability_conditions.append(f"{element} level is higher than Earth.")
        elif exoplanet_mean < earth_value:
            habitability_conditions.append(f"{element} level is lower than Earth.")
        else:
            habitability_conditions.append(f"{element} level is similar to Earth.")

# Check habitability conditions
st.header("Habitability Conditions")

if all(condition.startswith(element) for element in exoplanet_composition for condition in habitability_conditions):
    st.write("The exoplanet appears to have similar chemical composition to Earth.")
    st.write("Habitability conditions are favorable.")

else:
    st.write("The exoplanet's chemical composition differs from Earth.")
    st.write("Habitability conditions need further analysis.")

# Plot histograms for comparison
fig, ax = plt.subplots()
for element in exoplanet_composition:
    ax.hist(exoplanet_composition[element], bins=20, alpha=0.5, label=f"Exoplanet {element}")
ax.set_xlabel("Chemical Composition")
ax.set_ylabel("Frequency")
ax.legend()
st.pyplot(fig)




# # Compare exoplanet composition with Earth's composition
# habitability_conditions = []

# for element in exoplanet_composition:
#     exoplanet_mean = np.mean(exoplanet_composition[element])
#     earth_value = earth_composition.get(element, None)

#     if earth_value is None:
#         st.write(f"Earth's composition data for {element} is not available.")
#     else:
#         st.write(f"{element} in Exoplanet Mean: {exoplanet_mean}")
#         st.write(f"{element} in Earth: {earth_value}")

#         if exoplanet_mean > earth_value:
#             habitability_conditions.append(f"{element} level is higher than Earth.")
#         elif exoplanet_mean < earth_value:
#             habitability_conditions.append(f"{element} level is lower than Earth.")
#         else:
#             habitability_conditions.append(f"{element} level is similar to Earth.")

# Check habitability conditions
st.header("Habitability Conditions")

if all(condition.startswith(element) for element in exoplanet_composition for condition in habitability_conditions):
    st.write("The exoplanet appears to have similar chemical composition to Earth.")
    st.write("Habitability conditions are favorable.")

else:
    st.write("The exoplanet's chemical composition differs from Earth.")
    st.write("Habitability conditions need further analysis.")
