
from flask import Flask, request, jsonify, render_template
import pickle
import gzip
import pandas as pd
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# Define the feature columns expected in input data
FEATURES = [
    'age', 'dem_female', 'race', 'biomarkers', 'comorbidity',
    'lasix_dose_count_tm1', 'cre_tests_tm1', 'crp_tests_tm1', 'esr_tests_tm1',
    'ghba1c_tests_tm1', 'hct_tests_tm1', 'ldl_tests_tm1', 'nt_bnp_tests_tm1',
    'sodium_tests_tm1', 'trig_tests_tm1'
]

# Define the target columns for prediction
TARGET_COLUMNS = ['risk_score_t', 'cost_t', 'bps_mean_t', 'gagne_sum_t', 'ldl_mean_t']


# Define feature importance for each target, where weights represent the impact of each feature

FEATURES_IMPORTANCE = {
        "risk_score_t": {
        "cre_tests_tm1": 0.331480,
        "age":  0.116470,
        "hct_tests_tm1": 0.110542,
        "sodium_tests_tm1": 0.082573,
        "ghba1c_tests_tm1": 0.053679,
        "lasix_dose_count_tm1": 0.021110,
        "esr_tests_tm1": 0.041045,
        "trig_tests_tm1": 0.037929,
        "ldl_tests_tm1": 0.030893,
        "dem_female": 0.029604,
        "nt_bnp_tests_tm1": 0.031657,
        "race": 0.023662,
        "comorbidity": 0.088552,
        "crp_tests_tm1": 0.000805,
        "biomarkers": 0.000000
    },
        "cost_t": {
        "cre_tests_tm1": 0.174385,
        "age": 0.153828,
        "hct_tests_tm1": 0.129224,
        "sodium_tests_tm1": 0.091458,
        "ghba1c_tests_tm1": 0.097446,
        "lasix_dose_count_tm1": 0.046513,
        "esr_tests_tm1": 0.055875,
        "trig_tests_tm1": 0.057166,
        "ldl_tests_tm1": 0.057799,
        "dem_female": 0.043361,
        "nt_bnp_tests_tm1": 0.028622,
        "race": 0.037774,
        "comorbidity": 0.025631,
        "crp_tests_tm1": 0.002510,
        "biomarkers": 0.000000
    },
"bps_mean_t": {
        "age": 0.200674,
        "hct_tests_tm1": 0.139932,
        "cre_tests_tm1": 0.099523,
        "sodium_tests_tm1": 0.096317,
        "ghba1c_tests_tm1": 0.085675,
        "dem_female": 0.072795,
        "esr_tests_tm1": 0.064653,
        "trig_tests_tm1": 0.063822,
        "ldl_tests_tm1": 0.063506,
        "comorbidity": 0.045139,
        "race": 0.028183,
        "nt_bnp_tests_tm1": 0.022838,
        "lasix_dose_count_tm1": 0.015517,
        "crp_tests_tm1": 0.001427,
        "biomarkers": 0.000000
    },
    "gagne_sum_t": {
        "comorbidity": 0.348375,
        "cre_tests_tm1": 0.148429,
        "age": 0.098254,
        "sodium_tests_tm1": 0.088527,
        "hct_tests_tm1": 0.071717,
        "ghba1c_tests_tm1": 0.068573,
        "esr_tests_tm1": 0.030941,
        "ldl_tests_tm1": 0.030435,
        "trig_tests_tm1": 0.030433,
        "dem_female": 0.027625,
        "nt_bnp_tests_tm1": 0.022836,
        "race": 0.018367,
        "lasix_dose_count_tm1": 0.014738,
        "crp_tests_tm1": 0.000751,
        "biomarkers": 0.000000
    },
    "ldl_mean_t": {
        "hct_tests_tm1": 0.157374,
        "age": 0.130014,
        "cre_tests_tm1": 0.117300,
        "sodium_tests_tm1": 0.115766,
        "ghba1c_tests_tm1": 0.100805,
        "esr_tests_tm1": 0.072078,
        "ldl_tests_tm1": 0.056939,
        "comorbidity": 0.056806,
        "trig_tests_tm1": 0.055816,
        "race": 0.045980,
        "dem_female": 0.039691,
        "nt_bnp_tests_tm1": 0.029840,
        "lasix_dose_count_tm1": 0.018002,
        "crp_tests_tm1": 0.003589,
        "biomarkers": 0.000000
    }

}



# Load the scaler and model once during application startup to avoid reloading on each request
def load_scaler_and_model():
    with gzip.open('standard_scaler.pkl.gz', 'rb') as scaler_file_in:
        scaler = pickle.load(scaler_file_in)
    with gzip.open('multi_output_random_forest_model_compressed.pkl.gz', 'rb') as model_file_in:
        model = pickle.load(model_file_in)
    return scaler, model

# Load the scaler and model at startup
scaler, model = load_scaler_and_model()

# Define the home route to render the main HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Define route for displaying feature importance information
@app.route('/features_importance')
def feature_importance():
    return render_template('features_importance.html')

# Route for rendering a result page (if required in the front end)
@app.route('/result')
def result():
    return render_template('result.html')

# Prediction route to handle POST requests with feature data for prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Check if the model and scaler are loaded properly
    if scaler is None or model is None:
        return jsonify({"error": "Model or scaler not loaded properly."}), 500

    # Retrieve JSON data from the request
    data = request.get_json()

    # If data is missing, return an error
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Extract input features, desired targets, and weight values from request data
    input_features = data.get('features')
    desired_targets = data.get('desired_targets')
    weights = data.get('weight')

    # Validate presence of required fields
    if input_features is None:
        return jsonify({"error": "Missing 'features' in input data"}), 400
    if desired_targets is None:
        return jsonify({"error": "Missing 'desired_targets' in input data"}), 400
    if weights is None:
        return jsonify({"error": "Missing 'weight' in input data"}), 400

    # Ensure desired targets are valid
    valid_targets = [target for target in desired_targets if target in TARGET_COLUMNS]
    invalid_targets = [target for target in desired_targets if target not in TARGET_COLUMNS]

    # Return error if any invalid target is provided
    if invalid_targets:
        return jsonify({
            "error": f"Invalid target(s) specified: {invalid_targets}",
            "valid_targets": TARGET_COLUMNS
        }), 400

    # Check if any required feature is missing in the input data
    missing_features = [feature for feature in FEATURES if feature not in input_features]
    if missing_features:
        return jsonify({
            "error": "Missing required features",
            "missing_features": missing_features
        }), 400

    # Check if any weight is missing in the input data
    missing_weights = [feature for feature in FEATURES if feature not in weights]
    if missing_weights:
        return jsonify({
            "error": "Missing required weights",
            "missing_weights": missing_weights
        }), 400

    try:
        # Create a DataFrame from the input features
        input_df = pd.DataFrame([input_features], columns=FEATURES)

        # Scale the input features using the preloaded scaler
        input_scaled = scaler.transform(input_df)

        # Predict the target values based on scaled input features
        predictions = model.predict(input_scaled)[0]

        # Map predictions to target columns
        prediction_series = pd.Series(predictions, index=TARGET_COLUMNS)

        # Select predictions for only the desired targets
        selected_predictions = prediction_series[valid_targets]
       
        
        # Calculate weighted scores for each desired target using feature importance and weights
        weighted_scores = {}


        # for target in valid_targets:
        #     if target in FEATURES_IMPORTANCE:
        # # Calculate weighted score based solely on feature importance and weights
        #         weighted_score = sum(
        #         FEATURES_IMPORTANCE[target][feature] * weights[feature]
        #         for feature in FEATURES if feature in FEATURES_IMPORTANCE[target]
        #         )
        #         weighted_scores[target] = weighted_score


        for target in valid_targets:
            if target in FEATURES_IMPORTANCE:
                # Calculate weighted score using predicted score, feature importance, and request weight
                weighted_score = selected_predictions[target] * sum(
                    FEATURES_IMPORTANCE[target][feature] * weights[feature]
                    for feature in FEATURES if feature in FEATURES_IMPORTANCE[target]
                )
                weighted_scores[target] = weighted_score

        # Return predicted and weighted scores as a response
        response = {
            "predicted_scores": selected_predictions.to_dict(),
            "weighted_scores": weighted_scores
        }

        return jsonify(response), 200

    except Exception as e:
        # Handle any errors during prediction process
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500

# Run the app in production mode
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)  # Debug and auto-reloader turned off for production

