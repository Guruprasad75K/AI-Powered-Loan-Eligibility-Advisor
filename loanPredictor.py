"""
LOAN APPROVAL PREDICTION MODULE
Provides prediction functionality for Flask application
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import joblib
import os

class LoanPredictor:
    def __init__(self):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Build absolute paths to model files
        self.MODEL_PATH = os.path.join(script_dir, 'models', 'loan_model.ubj')
        self.ENCODER_PATH = os.path.join(script_dir, 'models', 'loan_encoder.joblib')
        self.THRESHOLD = 0.5
        self.model = None
        self.encoder = None
        self.expected_column_order = None

    def load_model(self):
        """Load XGBoost model and encoder"""
        try:
            # Load XGBoost model
            self.model = XGBClassifier()
            self.model.load_model(self.MODEL_PATH)

            # Load encoder
            self.encoder = joblib.load(self.ENCODER_PATH)

            # Get expected column order from model
            self.expected_column_order = self.model.get_booster().feature_names

            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    def preprocess_input(self, data):
        """Apply same preprocessing as training"""
        # Separate categorical and numerical features
        cat_columns = data.select_dtypes(include=['object']).columns

        # One-hot encode categorical features
        encoded = self.encoder.transform(data[cat_columns])
        encoded_df = pd.DataFrame(
            encoded,
            columns=self.encoder.get_feature_names_out(cat_columns)
        )

        # Combine with numerical features
        numerical_df = data.drop(columns=cat_columns)
        final_data = pd.concat([encoded_df, numerical_df], axis=1)

        # Ensure correct column order if available
        if self.expected_column_order is not None:
            final_data = final_data[self.expected_column_order]

        return final_data

    def make_prediction(self, application_data):
        """Make prediction using loaded model"""
        try:
            # Create DataFrame
            data = pd.DataFrame({
                'person_age': [application_data['person_age']],
                'person_gender': [application_data['person_gender']],
                'person_education': [application_data['person_education']],
                'person_income': [application_data['person_income']],
                'person_emp_exp': [application_data['person_emp_exp']],
                'person_home_ownership': [application_data['person_home_ownership']],
                'loan_amnt': [application_data['loan_amnt']],
                'loan_intent': [application_data['loan_intent']],
                'loan_percent_income': [application_data['loan_amnt'] / application_data['person_income']],
                'cb_person_cred_hist_length': [application_data['cb_person_cred_hist_length']],
                'credit_score': [application_data['credit_score']],
                'previous_loan_defaults_on_file': [application_data['previous_loan_defaults_on_file']]
            })

            # Preprocess
            processed_data = self.preprocess_input(data)

            # Get probability
            probability = self.model.predict_proba(processed_data)[:, 1][0]

            # Apply threshold
            prediction = int(probability >= self.THRESHOLD)

            # Identify risk factors
            risk_factors = []
            if application_data['credit_score'] < 600:
                risk_factors.append("Low credit score (< 600)")
            if application_data['previous_loan_defaults_on_file'] == 'Yes':
                risk_factors.append("Previous loan defaults on file")
            if (application_data['loan_amnt'] / application_data['person_income']) > 0.4:
                risk_factors.append("High debt-to-income ratio (> 40%)")
            if application_data['person_emp_exp'] == 0:
                risk_factors.append("No employment experience")
            if application_data['cb_person_cred_hist_length'] < 2:
                risk_factors.append("Short credit history (< 2 years)")

            return {
                'prediction': prediction,
                'probability': float(probability),
                'risk_factors': risk_factors,
                'application_data': application_data
            }
        except Exception as e:
            raise Exception(f"Prediction error: {str(e)}")

# Create global instance
predictor = LoanPredictor()