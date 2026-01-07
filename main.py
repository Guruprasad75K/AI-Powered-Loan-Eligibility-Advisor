"""
MAIN RUNNER - Loan Eligibility Advisor
Initializes and runs the complete loan approval system
"""

import sys
import os


def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'pandas',
        'numpy',
        'xgboost',
        'joblib',
        'huggingface_hub',
        'reportlab'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n💡 Install them using: pip install -r requirements.txt")
        return False

    return True


def check_model_files():
    """Check if model files exist"""
    required_files = [
        './models/loan_model.ubj',
        './models/loan_encoder.joblib'
    ]

    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("⚠️  Warning: Model files not found:")
        for file in missing_files:
            print(f"   • {file}")
        print("\n💡 Please ensure model files are in the './models/' directory")
        print("   The application will start but predictions won't work without them.\n")
        return False

    return True


def main():
    """Main entry point"""
    print("=" * 70)
    print("Loan Eligibility Advisor")
    print("=" * 70)
    print()

    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies installed\n")

    # Check model files
    print("🔍 Checking model files...")
    check_model_files()

    # Import and run Flask app
    print("🚀 Starting Flask application...")
    print("-" * 70)
    print()

    try:
        from app import app

        print("✓ Application started successfully!")
        print()
        print("📱 Access the application at:")
        print("   • http://localhost:5000")
        print("   • http://127.0.0.1:5000")
        print()
        print("Press CTRL+C to stop the server")
        print("=" * 70)
        print()

        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)

    except KeyboardInterrupt:
        print("\n\n✓ Server stopped gracefully")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()