from flask import Flask, request, jsonify, render_template
import pickle
import gzip
import pandas as pd
import numpy as np

app = Flask(__name__)

# Define the features used for prediction
features = ['cost_t', 'age', 'dem_female', 'race', 'biomarkers', 'comorbidity',
            'lasix_dose_count_tm1', 'cre_tests_tm1', 'crp_tests_tm1', 'esr_tests_tm1',
            'ghba1c_tests_tm1', 'hct_tests_tm1', 'ldl_tests_tm1', 'nt_bnp_tests_tm1',
            'sodium_tests_tm1', 'trig_tests_tm1']

def load_scaler_and_model():
    # Decompress and load the saved scaler and model only when needed
    with gzip.open('standard_scaler.pkl.gz', 'rb') as scaler_file_in:
        scaler = pickle.load(scaler_file_in)

    with gzip.open('random_forest_risk_score_model_compressed.pkl.gz', 'rb') as model_file_in:
        model = pickle.load(model_file_in)

    return scaler, model

@app.route('/')
def home():
    return render_template('index.html')

# API route to predict risk score
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Load the scaler and model only when needed
        scaler, model = load_scaler_and_model()
        
        # Parse input data from the request
        data = request.get_json()

        # Convert data to DataFrame
        df = pd.DataFrame([data])

        # Check if all required features are present
        if all(feature in df.columns for feature in features):
            X = df[features]
            X_scaled = scaler.transform(X)
            predicted_risk_score = model.predict(X_scaled)[0]

            # Clear variables to free memory
            del scaler, model, df, X, X_scaled
            
            # Return the predicted score
            return jsonify({'predicted_risk_score': predicted_risk_score}), 200
        else:
            return jsonify({'error': 'Missing required features'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
