# Predictive Risk Score Model Deployment

## 1. Introduction

This document outlines the architecture, implementation, and deployment of a predictive risk score model using Flask, Scikit-learn, and Render's free-tier hosting. The system provides risk predictions based on user health data.

## 2. System Overview

The system processes user health data, applies a trained machine learning model, and generates risk scores. The deployment ensures accessibility via a REST API hosted on Render.

### Key Components:

- **Data Processing**: Handling missing values, feature engineering, and scaling.
- **Machine Learning Model**: MultiOutputRegressor with LinearRegression.
- **Web API (Flask)**: A RESTful API for model inference.
- **Deployment**: Hosted on Render free tier.

## 3. System Architecture

### 3.1 High-Level Architecture

The architecture consists of four main layers:

1. **Data Preprocessing Layer**: Cleans and transforms raw input data.
2. **Machine Learning Layer**: Loads the trained model and generates predictions.
3. **API Layer**: Serves predictions via a Flask API.

### 3.2 Architecture Diagram

```
User Input --> Flask API --> Data Preprocessing --> Model Prediction --> API Response --> Display Results
```

## 4. Technology Stack

- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn (Linear Regression)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Deployment**: Render (Free Tier)
- **Storage**: Pickle (Model & Scaler Persistence)

## 5. Data Processing Pipeline

1. **Data Cleaning**: Handle missing values using median imputation.
2. **Feature Engineering**: Convert categorical and numerical values.
3. **Feature Scaling**: Standardization using `StandardScaler`.
4. **Encoding**: Label encoding categorical variables.

## 6. Machine Learning Model

- **Algorithm**: MultiOutputRegressor (LinearRegression)
- **Training Data**: Historical health data.
- **Target Variables**:
  - Risk Score (risk\_score\_t)
  - Cost (cost\_t)
  - Blood Pressure (bps\_mean\_t)
  - Gagne Comorbidity Score (gagne\_sum\_t)
  - LDL Mean (ldl\_mean\_t)
- **Performance Metrics**:
  - Mean Squared Error (MSE)
  - R-squared (R2 Score)

## 7. API Endpoints

### 7.1 `/predict` (POST)

**Request:**

```json
{
  "features": {"age": 30, "race": 1, "biomarkers": 1, "comorbidity": 1},
  "desired_targets": ["risk_score_t", "cost_t"]
}
```

**Response:**

```json
{
  "predicted_scores": {
    "risk_score_t": 0.85,
    "cost_t": 300.5
  }
}
```

## 8. Deployment Process

1. **Train the Model**: Train locally and save as a compressed `.pkl.gz` file.
2. **Create a Flask App**: Develop API endpoints for serving predictions.
3. **Deploy on Render**:
   - Upload model files.
   - Set up environment variables.
   - Deploy the Flask app.
4. **Monitor Logs**: Use Render's logging tools to track errors.

## 9. Security & Performance Optimization

- **Model Compression**: Using gzip to minimize storage size.
- **Rate Limiting**: Implement Flask-Limiter for API rate limiting.
- **Input Validation**: Ensure input data follows the expected format.
- **Error Handling**: Custom error messages for missing/incorrect inputs.

## 10. Conclusion

This system provides an interactive web-based solution for predicting health risks using machine learning, ensuring scalability and efficient deployment on a free-tier Render server.
