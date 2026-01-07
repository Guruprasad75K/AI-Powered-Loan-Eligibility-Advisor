"""
ULTRA MODERN REPORT GENERATOR MODULE
Generates beautiful visual reports with AI explainability
"""

import pandas as pd
import numpy as np
from lime.lime_tabular import LimeTabularExplainer
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle, FancyBboxPatch
from datetime import datetime
import io
import warnings
warnings.filterwarnings('ignore')


class LoanExplainer:
    """LIME-based explainability for loan predictions"""

    def __init__(self, model, encoder, expected_columns):
        self.model = model
        self.encoder = encoder
        self.expected_columns = expected_columns
        self.explainer = None

    def initialize_explainer(self, n_samples=100):
        """Initialize LIME explainer with synthetic training data"""
        np.random.seed(42)
        training_data = self._create_training_data(n_samples)

        feature_names = [
            'person_age', 'person_gender', 'person_education', 'person_income',
            'person_emp_exp', 'person_home_ownership', 'loan_amnt', 'loan_intent',
            'loan_percent_income', 'cb_person_cred_hist_length', 'credit_score',
            'previous_loan_defaults_on_file'
        ]

        categorical_features = [1, 2, 5, 7, 11]
        categorical_names = {
            1: ['female', 'male'],
            2: ['Associate', 'Bachelor', 'Doctorate', 'High School', 'Master'],
            5: ['MORTGAGE', 'OTHER', 'OWN', 'RENT'],
            7: ['DEBTCONSOLIDATION', 'EDUCATION', 'HOMEIMPROVEMENT', 'MEDICAL', 'PERSONAL', 'VENTURE'],
            11: ['No', 'Yes']
        }

        self.explainer = LimeTabularExplainer(
            training_data=training_data,
            feature_names=feature_names,
            categorical_features=categorical_features,
            categorical_names=categorical_names,
            mode='classification',
            random_state=42
        )

        return True

    def _create_training_data(self, n_samples):
        """Generate synthetic training data for LIME"""
        data = []
        for _ in range(n_samples):
            row = [
                np.random.randint(18, 70),  # age
                np.random.choice([0, 1]),  # gender
                np.random.randint(0, 5),  # education
                np.random.randint(20000, 150000),  # income
                np.random.randint(0, 30),  # employment exp
                np.random.randint(0, 4),  # home ownership
                np.random.randint(1000, 50000),  # loan amount
                np.random.randint(0, 6),  # loan intent
                0,  # loan percent income (calculated below)
                np.random.randint(0, 30),  # credit history length
                np.random.randint(300, 850),  # credit score
                np.random.choice([0, 1])  # defaults
            ]
            row[8] = row[6] / row[3]  # Calculate loan_percent_income
            data.append(row)
        return np.array(data)

    def _convert_to_encoded_format(self, instance):
        """Convert LIME instance to model input format"""
        maps = {
            'gender': {0: 'female', 1: 'male'},
            'education': {0: 'Associate', 1: 'Bachelor', 2: 'Doctorate', 3: 'High School', 4: 'Master'},
            'ownership': {0: 'MORTGAGE', 1: 'OTHER', 2: 'OWN', 3: 'RENT'},
            'intent': {0: 'DEBTCONSOLIDATION', 1: 'EDUCATION', 2: 'HOMEIMPROVEMENT', 3: 'MEDICAL', 4: 'PERSONAL', 5: 'VENTURE'},
            'defaults': {0: 'No', 1: 'Yes'}
        }

        data = pd.DataFrame({
            'person_age': [instance[0]],
            'person_gender': [maps['gender'][int(instance[1])]],
            'person_education': [maps['education'][int(instance[2])]],
            'person_income': [instance[3]],
            'person_emp_exp': [instance[4]],
            'person_home_ownership': [maps['ownership'][int(instance[5])]],
            'loan_amnt': [instance[6]],
            'loan_intent': [maps['intent'][int(instance[7])]],
            'loan_percent_income': [instance[8]],
            'cb_person_cred_hist_length': [instance[9]],
            'credit_score': [instance[10]],
            'previous_loan_defaults_on_file': [maps['defaults'][int(instance[11])]]
        })

        # Preprocess
        cat_columns = data.select_dtypes(include=['object']).columns
        encoded = self.encoder.transform(data[cat_columns])
        encoded_df = pd.DataFrame(encoded, columns=self.encoder.get_feature_names_out(cat_columns))
        numerical_df = data.drop(columns=cat_columns).astype(float)
        encoded_df = encoded_df.astype(float)
        final_data = pd.concat([encoded_df, numerical_df], axis=1)

        if self.expected_columns is not None:
            final_data = final_data[self.expected_columns]

        return final_data.astype(np.float32)

    def predict_fn(self, instances):
        """Prediction function for LIME"""
        predictions = []
        for instance in instances:
            processed = self._convert_to_encoded_format(instance)
            prob = self.model.predict_proba(processed)[0]
            predictions.append(prob)
        return np.array(predictions)

    def explain_prediction(self, application_data, prediction_result, num_features=10):
        """Generate explanation for a prediction"""
        maps = {
            'gender': {'female': 0, 'male': 1},
            'education': {'Associate': 0, 'Bachelor': 1, 'Doctorate': 2, 'High School': 3, 'Master': 4},
            'ownership': {'MORTGAGE': 0, 'OTHER': 1, 'OWN': 2, 'RENT': 3},
            'intent': {'DEBTCONSOLIDATION': 0, 'EDUCATION': 1, 'HOMEIMPROVEMENT': 2, 'MEDICAL': 3, 'PERSONAL': 4, 'VENTURE': 5},
            'defaults': {'No': 0, 'Yes': 1}
        }

        instance = np.array([
            application_data['person_age'],
            maps['gender'][application_data['person_gender']],
            maps['education'][application_data['person_education']],
            application_data['person_income'],
            application_data['person_emp_exp'],
            maps['ownership'][application_data['person_home_ownership']],
            application_data['loan_amnt'],
            maps['intent'][application_data['loan_intent']],
            application_data['loan_amnt'] / application_data['person_income'],
            application_data['cb_person_cred_hist_length'],
            application_data['credit_score'],
            maps['defaults'][application_data['previous_loan_defaults_on_file']]
        ])

        exp = self.explainer.explain_instance(instance, self.predict_fn, num_features=num_features)
        explanation_list = exp.as_list()

        top_positive = [{'feature': f, 'weight': float(w)} for f, w in explanation_list if w > 0]
        top_negative = [{'feature': f, 'weight': float(w)} for f, w in explanation_list if w < 0]

        return {
            'prediction': prediction_result['prediction'],
            'probability': prediction_result['probability'],
            'top_positive_factors': top_positive,
            'top_negative_factors': top_negative,
            'risk_factors': prediction_result['risk_factors'],
            'all_factors': explanation_list
        }


class UltraModernVisualizer:
    """Ultra-modern report visualizer"""

    def __init__(self):
        # Minimal modern color palette
        self.bg = '#FFFFFF'
        self.dark = '#1A1A2E'
        self.green = '#00D9A3'
        self.red = '#FF6B6B'
        self.gray = '#E8E8E8'
        self.text = '#2E3440'

    def create_report(self, explanation, app_data, filename=None):
        """Create ultra-modern A4 report"""

        # A4: 8.27 x 11.69 inches
        fig = plt.figure(figsize=(8.27, 11.69), facecolor=self.bg)

        # ==== HEADER ====
        decision = "APPROVED" if explanation['prediction'] == 1 else "REJECTED"
        color = self.green if explanation['prediction'] == 1 else self.red

        # Ultra-bold heading
        fig.text(0.5, 0.96, decision, ha='center', fontsize=56,
                fontweight='black', color=color, family='sans-serif')
        fig.text(0.5, 0.92, 'LOAN APPLICATION ANALYSIS', ha='center',
                fontsize=14, color=self.text, alpha=0.6)

        # ==== 4 QUADRANTS ====

        # QUADRANT 1: APPROVAL RING (Top Left)
        ax1 = plt.axes([0.08, 0.58, 0.38, 0.3])
        self._draw_approval_ring(ax1, explanation)

        # QUADRANT 2: FEATURE SPLIT (Top Right)
        ax2 = plt.axes([0.54, 0.58, 0.38, 0.3])
        self._draw_feature_split(ax2, explanation)

        # QUADRANT 3: KEY METRICS (Bottom Left)
        ax3 = plt.axes([0.08, 0.15, 0.38, 0.38])
        self._draw_key_metrics(ax3, app_data, explanation)

        # QUADRANT 4: IMPROVEMENT (Bottom Right)
        ax4 = plt.axes([0.54, 0.15, 0.38, 0.38])
        self._draw_improvements(ax4, app_data, explanation)

        # Footer
        fig.text(0.5, 0.05, datetime.now().strftime("%B %d, %Y"),
                ha='center', fontsize=9, color=self.text, alpha=0.4)

        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor=self.bg)
        buffer.seek(0)
        plt.close()

        return buffer

    def _draw_approval_ring(self, ax, explanation):
        """Circular progress ring"""
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')

        prob = explanation['probability']
        color = self.green if explanation['prediction'] == 1 else self.red

        # Title
        ax.text(0, 1.2, 'APPROVAL SCORE', ha='center', fontsize=13,
               fontweight='bold', color=self.text)

        # Background circle
        bg_circle = Circle((0, 0), 1, fill=False, edgecolor=self.gray, linewidth=20)
        ax.add_patch(bg_circle)

        # Progress arc (thick ring)
        angle = prob * 360
        theta = np.linspace(90, 90 - angle, 200)

        for i in range(len(theta) - 1):
            wedge = Wedge((0, 0), 1, theta[i+1], theta[i],
                         width=0.2, facecolor=color, edgecolor='none', alpha=0.9)
            ax.add_patch(wedge)

        # Center percentage - HUGE
        ax.text(0, 0, f'{prob*100:.1f}%', ha='center', va='center',
               fontsize=32, fontweight='black', color=color)

        # Subtitle
        status = 'EXCELLENT' if prob > 0.8 else 'GOOD' if prob > 0.6 else 'FAIR' if prob > 0.4 else 'LOW'
        ax.text(0, -0.4, status, ha='center', fontsize=12,
               color=color, fontweight='bold')

    def _draw_feature_split(self, ax, explanation):
        """Split positive/negative features"""
        ax.axis('off')

        # Title
        ax.text(0.5, 0.95, 'IMPACT ANALYSIS', transform=ax.transAxes,
               ha='center', fontsize=13, fontweight='bold', color=self.text)

        # Get factors
        factors = sorted(explanation['all_factors'], key=lambda x: abs(x[1]), reverse=True)[:8]
        positive = [(f, w) for f, w in factors if w > 0][:4]
        negative = [(f, w) for f, w in factors if w < 0][:4]

        # LEFT: Positive (Green)
        ax.text(0.25, 0.85, 'POSITIVE', transform=ax.transAxes, ha='center',
               fontsize=11, fontweight='bold', color=self.green)

        y = 0.75
        max_w = max([abs(w) for _, w in factors]) if factors else 1

        for feat, weight in positive:
            # Clean name
            name = feat.split('=')[0].split('<')[0].split('>')[0].replace('_', ' ').strip()[:15]

            # Bar
            bar_w = (abs(weight) / max_w) * 0.2
            rect = Rectangle((0.05, y), bar_w, 0.06,
                           facecolor=self.green, alpha=0.8, transform=ax.transAxes)
            ax.add_patch(rect)

            # Label
            ax.text(0.25, y + 0.03, name, transform=ax.transAxes,
                   ha='center', fontsize=8, color=self.text)

            y -= 0.15

        # RIGHT: Negative (Red)
        ax.text(0.75, 0.85, 'NEGATIVE', transform=ax.transAxes, ha='center',
               fontsize=11, fontweight='bold', color=self.red)

        y = 0.75
        for feat, weight in negative:
            # Clean name
            name = feat.split('=')[0].split('<')[0].split('>')[0].replace('_', ' ').strip()[:15]

            # Bar
            bar_w = (abs(weight) / max_w) * 0.2
            rect = Rectangle((0.75, y), bar_w, 0.06,
                           facecolor=self.red, alpha=0.8, transform=ax.transAxes)
            ax.add_patch(rect)

            # Label
            ax.text(0.75, y + 0.03, name, transform=ax.transAxes,
                   ha='center', fontsize=8, color=self.text)

            y -= 0.15

    def _draw_key_metrics(self, ax, app_data, explanation):
        """Key metrics visualization"""
        ax.axis('off')

        # Title
        ax.text(0.5, 0.95, 'KEY METRICS', transform=ax.transAxes, ha='center',
               fontsize=13, fontweight='bold', color=self.text)

        # Credit Score - Large visual
        score = app_data['credit_score']
        score_pct = (score - 300) / (850 - 300)

        if score >= 750:
            s_color = self.green
            rating = 'EXCELLENT'
        elif score >= 700:
            s_color = '#FFB800'
            rating = 'GOOD'
        elif score >= 650:
            s_color = '#FF9500'
            rating = 'FAIR'
        else:
            s_color = self.red
            rating = 'POOR'

        # Score bar
        rect_bg = Rectangle((0.1, 0.78), 0.8, 0.1, facecolor=self.gray, transform=ax.transAxes)
        ax.add_patch(rect_bg)
        rect_fill = Rectangle((0.1, 0.78), 0.8 * score_pct, 0.1,
                             facecolor=s_color, alpha=0.9, transform=ax.transAxes)
        ax.add_patch(rect_fill)

        ax.text(0.5, 0.83, f'{score}', transform=ax.transAxes, ha='center',
               fontsize=24, fontweight='bold', color='white', va='center')
        ax.text(0.5, 0.72, rating, transform=ax.transAxes, ha='center',
               fontsize=11, fontweight='bold', color=s_color)

        # Other metrics - Clean grid
        metrics = [
            ('INCOME', f'${app_data["person_income"]:,}'),
            ('LOAN', f'${app_data["loan_amnt"]:,}'),
            ('DTI', f'{(app_data["loan_amnt"]/app_data["person_income"])*100:.0f}%'),
            ('WORK', f'{app_data["person_emp_exp"]}y'),
            ('CREDIT AGE', f'{app_data["cb_person_cred_hist_length"]}y'),
            ('DEFAULTS', app_data['previous_loan_defaults_on_file'])
        ]

        y = 0.60
        for i in range(0, len(metrics), 2):
            # Left metric
            if i < len(metrics):
                label, value = metrics[i]
                ax.text(0.15, y, label, transform=ax.transAxes,
                       fontsize=8, color=self.text, alpha=0.6)
                ax.text(0.15, y - 0.05, value, transform=ax.transAxes,
                       fontsize=14, fontweight='bold', color=self.text)

            # Right metric
            if i + 1 < len(metrics):
                label, value = metrics[i + 1]
                ax.text(0.6, y, label, transform=ax.transAxes,
                       fontsize=8, color=self.text, alpha=0.6)
                ax.text(0.6, y - 0.05, value, transform=ax.transAxes,
                       fontsize=14, fontweight='bold', color=self.text)

            y -= 0.15

        # Risk factors if any
        if explanation['risk_factors']:
            ax.text(0.5, 0.08, '⚠ RISKS', transform=ax.transAxes, ha='center',
                   fontsize=10, fontweight='bold', color=self.red)
            risk_text = ' • '.join(explanation['risk_factors'][:2])
            ax.text(0.5, 0.02, risk_text[:40], transform=ax.transAxes, ha='center',
                   fontsize=8, color=self.red)

    def _draw_improvements(self, ax, app_data, explanation):
        """Improvement recommendations"""
        ax.axis('off')

        # Title
        ax.text(0.5, 0.95, 'HOW TO IMPROVE', transform=ax.transAxes, ha='center',
               fontsize=13, fontweight='bold', color=self.text)

        # Generate tips
        tips = []

        if app_data['credit_score'] < 700:
            tips.append(('CREDIT SCORE', f'Target 700+\nCurrent: {app_data["credit_score"]}'))

        dti = (app_data['loan_amnt'] / app_data['person_income']) * 100
        if dti > 40:
            tips.append(('DEBT RATIO', f'Reduce to <40%\nCurrent: {dti:.0f}%'))

        if app_data['cb_person_cred_hist_length'] < 5:
            tips.append(('CREDIT AGE', f'Build to 5+ years\nCurrent: {app_data["cb_person_cred_hist_length"]}y'))

        if app_data['person_emp_exp'] < 2:
            tips.append(('EMPLOYMENT', 'Gain work history\nTarget: 2+ years'))

        if app_data['previous_loan_defaults_on_file'] == 'Yes':
            tips.append(('DEFAULTS', 'Rebuild trust\nConsider secured credit'))

        if not tips or explanation['prediction'] == 1:
            tips = [
                ('MAINTAIN', 'Keep current habits'),
                ('MONITOR', 'Check credit reports'),
                ('SAVE', 'Build emergency fund')
            ]

        # Draw tips
        y = 0.85
        for title, desc in tips[:5]:
            # Box
            rect = FancyBboxPatch((0.05, y - 0.1), 0.9, 0.12,
                                 boxstyle="round,pad=0.01",
                                 facecolor=self.gray, alpha=0.3,
                                 transform=ax.transAxes)
            ax.add_patch(rect)

            # Title
            ax.text(0.1, y - 0.02, title, transform=ax.transAxes,
                   fontsize=10, fontweight='bold', color=self.text)

            # Description
            ax.text(0.1, y - 0.08, desc, transform=ax.transAxes,
                   fontsize=8, color=self.text, alpha=0.8)

            y -= 0.16


# ============================================================================
# MAIN REPORT GENERATION FUNCTION
# ============================================================================

# Global instances (initialized once)
_explainer = None
_visualizer = None

def generate_loan_report(prediction_result, model, encoder, expected_columns):
    """
    Generate ultra-modern visual loan report

    Args:
        prediction_result: Dictionary containing prediction data and application data
        model: The loaded XGBoost model
        encoder: The loaded OneHotEncoder
        expected_columns: List of expected column names

    Returns:
        BytesIO object containing the PNG image report
    """
    global _explainer, _visualizer

    try:
        print("Starting report generation...")

        # Validate inputs
        if model is None:
            raise ValueError("Model is None")
        if encoder is None:
            raise ValueError("Encoder is None")
        if 'application_data' not in prediction_result:
            raise ValueError("application_data not in prediction_result")

        # Initialize explainer and visualizer (once)
        if _explainer is None:
            print("Initializing explainer...")
            _explainer = LoanExplainer(model, encoder, expected_columns)
            _explainer.initialize_explainer(100)
            print("Explainer initialized")

        if _visualizer is None:
            print("Initializing visualizer...")
            _visualizer = UltraModernVisualizer()
            print("Visualizer initialized")

        # Generate explanation using LIME
        print("Generating LIME explanation...")
        explanation = _explainer.explain_prediction(
            prediction_result['application_data'],
            prediction_result,
            num_features=10
        )
        print("Explanation generated")

        # Create visual report
        print("Creating visual report...")
        report_buffer = _visualizer.create_report(
            explanation,
            prediction_result['application_data']
        )
        print("Visual report created")

        # Ensure buffer is at start
        report_buffer.seek(0)

        return report_buffer

    except Exception as e:
        print(f"ERROR in generate_loan_report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Report generation failed: {str(e)}")