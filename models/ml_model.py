import numpy as np
from sklearn.linear_model import LinearRegression

# Global model instance
_model = None

def train_predictor_model():
    """
    Generates a synthetic student dataset and trains a LinearRegression model.
    Features: [Attendance (%), Avg Daily Study Hours, Internal Marks (out of 30)]
    Target: Final Exam Score (out of 100)
    """
    global _model
    
    # Random seed for reproducibility
    np.random.seed(42)
    
    # Generate 100 student records
    # Attendance between 50% and 100%
    attendance = np.random.uniform(50, 100, 100)
    # Study hours between 1 and 10
    study_hours = np.random.uniform(1, 10, 100)
    # Internal marks between 10 and 30
    internal_marks = np.random.uniform(10, 30, 100)
    
    # Calculate final score: 
    # Base is 25. Attendance contributes up to 25%, Study hours up to 25%, Internal marks up to 30%
    # plus some random noise
    base_score = 25
    final_scores = (
        base_score + 
        (attendance * 0.25) + 
        (study_hours * 2.5) + 
        (internal_marks * 1.0) + 
        np.random.normal(0, 2, 100)
    )
    
    # Clip final scores between 0 and 100
    final_scores = np.clip(final_scores, 0, 100)
    
    X = np.column_stack((attendance, study_hours, internal_marks))
    y = final_scores
    
    model = LinearRegression()
    model.fit(X, y)
    
    _model = model
    print("[ML] Marks Prediction Model trained successfully.")

def predict_score(attendance, study_hours, internal_marks):
    """
    Predicts the final exam score using the trained model.
    Ensures input validation and bounds the result between 0 and 100.
    """
    global _model
    if _model is None:
        train_predictor_model()
        
    # Standardize inputs
    attendance = float(attendance)
    study_hours = float(study_hours)
    internal_marks = float(internal_marks)
    
    # Predict
    input_data = np.array([[attendance, study_hours, internal_marks]])
    predicted = _model.predict(input_data)[0]
    
    # Bounded between 0 and 100
    return min(100.0, max(0.0, round(float(predicted), 2)))
