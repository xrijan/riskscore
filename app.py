from flask import Flask, request, jsonify, render_template
import pickle
import gzip
import pandas as pd
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Define the features used for prediction
# features = ['cost_t', 'age', 'dem_female', 'race', 'biomarkers', 'comorbidity',
#             'lasix_dose_count_tm1', 'cre_tests_tm1', 'crp_tests_tm1', 'esr_tests_tm1',
#             'ghba1c_tests_tm1', 'hct_tests_tm1', 'ldl_tests_tm1', 'nt_bnp_tests_tm1',
#             'sodium_tests_tm1', 'trig_tests_tm1']

FEATURES = [
    'age', 'dem_female', 'race', 'biomarkers', 'comorbidity',
    'lasix_dose_count_tm1', 'cre_tests_tm1', 'crp_tests_tm1', 'esr_tests_tm1',
    'ghba1c_tests_tm1', 'hct_tests_tm1', 'ldl_tests_tm1', 'nt_bnp_tests_tm1',
    'sodium_tests_tm1', 'trig_tests_tm1'
]


TARGET_COLUMNS = ['risk_score_t', 'cost_t', 'cost_avoidable_t']
# # Load the scaler and model once on startup
# def load_scaler_and_model():
#     with gzip.open('standard_scaler.pkl.gz', 'rb') as scaler_file_in:
#         scaler = pickle.load(scaler_file_in)
#     with gzip.open('random_forest_risk_score_model_compressed.pkl.gz', 'rb') as model_file_in:
#         model = pickle.load(model_file_in)
#     return scaler, model

# Load the scaler and model once on startup
def load_scaler_and_model():
    with gzip.open('standard_scaler.pkl.gz', 'rb') as scaler_file_in:
        scaler = pickle.load(scaler_file_in)
    with gzip.open('multi_output_random_forest_model_compressed.pkl.gz', 'rb') as model_file_in:
        model = pickle.load(model_file_in)
    return scaler, model

scaler, model = load_scaler_and_model()

@app.route('/')
def home():
    return render_template('index.html')

# Route for the result page
@app.route('/result')
def result():
    return render_template('result.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         # Parse input data from the request
#         data = request.get_json()
        
#         # Convert data to DataFrame
#         df = pd.DataFrame([data])
        
#         # Ensure correct dtypes to minimize memory usage
#         df = df.astype({
#             # 'cost_t': 'float32',
#             'age': 'float32',
#             'dem_female': 'int8',
#             'race': 'int8',
#             'biomarkers': 'float32',
#             'comorbidity': 'int8',
#             'lasix_dose_count_tm1': 'float32',
#             'cre_tests_tm1': 'float32',
#             'crp_tests_tm1': 'float32',
#             'esr_tests_tm1': 'float32',
#             'ghba1c_tests_tm1': 'float32',
#             'hct_tests_tm1': 'float32',
#             'ldl_tests_tm1': 'float32',
#             'nt_bnp_tests_tm1': 'float32',
#             'sodium_tests_tm1': 'float32',
#             'trig_tests_tm1': 'float32'
#         })

#         # Check if all required features are present
#         if all(feature in df.columns for feature in features):
#             X = df[features]
#             X_scaled = scaler.transform(X)
#             predicted_risk_score = model.predict(X_scaled)[0]
#             return jsonify({'predicted_risk_score': predicted_risk_score}), 200
#         else:
#             return jsonify({'error': 'Missing required features'}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
@app.route('/predict', methods=['POST'])
def predict():
    if scaler is None or model is None:
        return jsonify({"error": "Model or scaler not loaded properly."}), 500

    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Extract features and desired targets from the request
    input_features = data.get('features')
    desired_targets = data.get('desired_targets')

    if input_features is None:
        return jsonify({"error": "Missing 'features' in input data"}), 400

    if desired_targets is None:
        return jsonify({"error": "Missing 'desired_targets' in input data"}), 400

    # Validate desired targets
    valid_targets = [target for target in desired_targets if target in TARGET_COLUMNS]
    invalid_targets = [target for target in desired_targets if target not in TARGET_COLUMNS]

    if invalid_targets:
        return jsonify({
            "error": f"Invalid target(s) specified: {invalid_targets}",
            "valid_targets": TARGET_COLUMNS
        }), 400

    # Check for missing features
    missing_features = [feature for feature in FEATURES if feature not in input_features]
    if missing_features:
        return jsonify({
            "error": "Missing required features",
            "missing_features": missing_features
        }), 400

    try:
        # Create DataFrame from input features
        input_df = pd.DataFrame([input_features], columns=FEATURES)

        # Ensure correct data types (optional, based on your data)
        # For example, converting to numeric, handling categorical if needed

        # Scale the features
        input_scaled = scaler.transform(input_df)

        # Make predictions
        predictions = model.predict(input_scaled)[0]

        # Create a Series with target names
        prediction_series = pd.Series(predictions, index=TARGET_COLUMNS)

        # Select desired targets
        selected_predictions = prediction_series[valid_targets]

        # Convert to dictionary for JSON response
        response = selected_predictions.to_dict()

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)  # Turn off debug mode and auto-reloader for production
