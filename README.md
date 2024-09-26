# Flask Prediction App

This repository contains a Python Flask web application that predicts a risk score based on several features. The app takes in input data, processes it using a pre-trained machine learning model, and returns a prediction.

## Features
- Predicts a risk score using a Random Forest model.
- Inputs are processed using a Standard Scaler.
- The application uses Flask as the web framework.
- Includes CORS handling for cross-origin requests.
  
### Prerequisites
- Python 3.12
- `pip` (Python package manager)
  
### Clone the Repository
```bash
git clone https://github.com/xrijan/riskscore.git
cd riskscore
```

### Setting Up the Environment

It is recommended to use a virtual environment to avoid version conflicts.

Create a virtual environment:

```bash
python3 -m venv venv
```
Activate the virtual environment:
On macOS/Linux:
```bash
source venv/bin/activate
```
On Windows:
```bash
Copy code
venv\Scripts\activate
```
### Install required packages:
Install the dependencies from the requirements.txt file.

```bash
pip install -r requirements.txt
```


### Running the Flask App
```bash
python app.py
```



