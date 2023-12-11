# COSMOS

To handle the form submission and make the prediction using Python, you need to create a server-side script using a web framework like Flask. 
## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project is a Flask web application that allows users to [provide a brief overview of what your application does].

## Installation

Follow these steps to set up and run the project:

1. Clone the repository:

    ```bash
    git clone https://github.com/Exo-planetary/flask-project.git
    ```

2. Navigate to the project directory:

    ```bash
    cd your-flask-project
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask application:

    ```bash
    python app.py
    ```

    The application will be accessible at [http://localhost:5000/](http://localhost:5000/).

## Usage

1. Open your web browser and go to [http://localhost:5000/](http://localhost:5000/).
2. [Provide instructions on how to use your application, if necessary].

## Folder Structure

Explain the purpose of each major folder in your project:

- `web_app`: Contains the Flask application code.
- `templates`: Contains HTML templates for rendering pages.
- `mongodb_code`: Contains utility code related to MongoDB operations.

## Dependencies

List the main dependencies used in your project:

- Flask
- pymongo

## Contributing

Feel free to contribute to this project by following these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request.


from django.test import TestCase
   from django.urls import reverse
   ```

3. Create a test class that inherits from `TestCase`:
   ```python
   class IndexPageTests(TestCase):
       def test_index_page_links(self):
           # Test the links in the index page
           response = self.client.get(reverse('index'))
           self.assertEqual(response.status_code, 200)
           self.assertContains(response, '<a href="/templates/explore.html#form-section1">Radial Velocity</a>')
           self.assertContains(response, '<a href="/templates/explore.html#form-section2">Transit Method</a>')
           self.assertContains(response, '<a href="/templates/explore.html#form-section3">Direct Imaging</a>')
           self.assertContains(response, '<a href="/templates/explore.html#form-section4">Biosignature</a>')
   ```

4. In the `test_index_page_links` method, we make a GET request to the index page using the `self.client.get` method. Then we assert that the response status code is 200 (indicating a successful request) and that the response contains the expected links.

5. Finally, run the tests by executing the following command in your terminal:
   ```bash
   python manage.py test
   ```

Here's the updated code with the tests included:



Enter the start time (days): 0
Enter the end time (days): 10
Enter transit light curve values (comma-separated, e.g., 1.0, 0.8, 0.6, 0.9, 1.0): 
1.0, 0.7, 0.4, 0.8, 1.0
Enter the transit duration (days): 2
Do you want to add realistic noise? (yes/no): no
Enter depth threshold for transit confirmation: 0.2
Enter duration threshold for transit confirmation: 1.0



# Test Case 1: Clear Transit Signal
Input:
Start time: 0
End time: 10
Transit light curve values: 1.0, 0.8, 0.6, 0.9, 1.0
Transit duration: 2
Add noise: No
Depth threshold: 0.2
Duration threshold: 1.0
Expected Output:
Exoplanet presence confirmed


# Test Case 2: No Transit Signal
Input:
Start time: 0
End time: 10
Transit light curve values: 1.0, 1.0, 1.0, 1.0, 1.0
Transit duration: 2
Add noise: No
Depth threshold: 0.2
Duration threshold: 1.0
Expected Output:
No exoplanet confirmed based on the provided transit data

# Test Case 3: Noisy Signal with Thresholds Met
Input:
Start time: 0
End time: 10
Transit light curve values: 1.0, 0.7, 0.4, 0.8, 1.0
Transit duration: 2
Add noise: Yes (Noise level: 0.1)
Depth threshold: 0.3
Duration threshold: 1.5
Expected Output:
Exoplanet presence confirmed

# Test Case 4: Noisy Signal with Thresholds Not Met
Input:
Start time: 0
End time: 10
Transit light curve values: 1.0, 0.7, 0.4, 0.8, 1.0
Transit duration: 2
Add noise: Yes (Noise level: 0.1)
Depth threshold: 0.4
Duration threshold: 2.0
Expected Output:
No exoplanet confirmed based on the provided transit data

# Test Case 5: Large Duration Transit Signal
Input:
Start time: 0
End time: 20
Transit light curve values: 1.0, 0.8, 0.6, 0.4, 0.3, 0.4, 0.6, 0.8, 1.0
Transit duration: 8
Add noise: Yes (Noise level: 0.05)
Depth threshold: 0.5
Duration threshold: 5.0
Expected Output:
Exoplanet presence confirmed


# Sample input data
sample_input = pd.DataFrame({
    'pl_orbper': [10.0],
    'pl_rade': [1.5],
    'pl_orbeccen': [0.1],
    'pl_orbincl': [89.0],
    'pl_tranmid': [2459000.0],
    'pl_imppar': [0.02],
    'pl_trandep': [0.01],
    'pl_trandur': [2.0],
    'pl_ratdor': [0.01],
    'pl_ratror': [0.1],
    'sy_vmag': [10.0],
    'sy_kmag': [8.0]
})

# Standardize the sample input
sample_input_scaled = scaler.transform(sample_input)

# Make predictions using the trained model
sample_output = model.predict(sample_input_scaled)

print("Sample Input:")
print(sample_input)
print("\nPredicted Output:")
print(sample_output)