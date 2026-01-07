"""
LOAN APPROVAL SYSTEM - FLASK APPLICATION
Main web application with loan prediction and chatbot
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from loanPredictor import predictor
from chatbot import chatbot
from datetime import datetime
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize predictor at startup
print("🔄 Loading model and encoder...")
success = predictor.load_model()
if success:
    print("✓ Model and encoder loaded successfully")
else:
    print("❌ Failed to load model and encoder")
    print("⚠️  Predictions will not work until model files are added to ./models/")

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    """Handle loan prediction request"""
    try:
        data = request.json

        # Validate required fields
        required_fields = [
            'person_age', 'person_income', 'person_emp_exp', 'loan_amnt',
            'cb_person_cred_hist_length', 'credit_score', 'person_gender',
            'person_education', 'person_home_ownership', 'loan_intent',
            'previous_loan_defaults_on_file'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing field: {field}'}), 400

        # Make prediction
        result = predictor.make_prediction(data)

        # Store result in session for report generation
        session['last_prediction'] = result

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot request"""
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'success': False, 'message': 'No message provided'}), 400

        # Get session ID for conversation history
        if 'chat_session_id' not in session:
            session['chat_session_id'] = secrets.token_hex(8)

        session_id = session['chat_session_id']

        # Get response from chatbot
        response = chatbot.get_response(user_message, session_id)

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download-report', methods=['GET'])
def download_report():
    """Generate and download visual report"""
    try:
        # Get last prediction from session
        if 'last_prediction' not in session:
            return jsonify({'success': False, 'message': 'No prediction available. Please submit an application first.'}), 400

        result = session['last_prediction']

        # Check if model is loaded
        if predictor.model is None or predictor.encoder is None:
            return jsonify({'success': False, 'message': 'Model not loaded. Please restart the application.'}), 500

        print("Generating visual report...")

        # Generate visual report (PNG image)
        from reportGenerator import generate_loan_report

        try:
            report_buffer = generate_loan_report(
                result,
                predictor.model,
                predictor.encoder,
                predictor.expected_column_order
            )

            print("Report generated successfully")

            # Make sure buffer is at the start
            report_buffer.seek(0)

            # Generate filename with timestamp
            filename = f'loan_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

            # Send file as PNG
            return send_file(
                report_buffer,
                mimetype='image/png',
                as_attachment=True,
                download_name=filename
            )

        except Exception as report_error:
            print(f"Report generation error: {str(report_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error generating report: {str(report_error)}'}), 500

    except Exception as e:
        print(f"Download endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': predictor.model is not None})

if __name__ == '__main__':
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create necessary directories
    os.makedirs(os.path.join(script_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'models'), exist_ok=True)

    # Run app
    app.run(debug=True, host='0.0.0.0', port=5000)