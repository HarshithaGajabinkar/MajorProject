import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import json
from utils.preprocess import preprocess_pipeline

def train_model():
    print("Starting model training...")
    
    # Step 1: Preprocess data
    X, y, label_encoder, symptom_encoder, all_symptoms, df, severity_mapping = preprocess_pipeline()
    
    # Step 2: Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Step 3: Train model
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Step 4: Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=label_encoder.classes_))
    
    # Step 5: Save everything
    print("\nSaving model and encoders...")
    joblib.dump(model, 'model/disease_model.pkl')
    joblib.dump(label_encoder, 'model/label_encoder.pkl')
    joblib.dump(symptom_encoder, 'model/symptom_encoder.pkl')
    
    # Save metadata
    metadata = {
        'all_symptoms': all_symptoms,
        'disease_names': label_encoder.classes_.tolist(),
        'severity_mapping': severity_mapping,
        'accuracy': float(accuracy),
        'num_diseases': len(label_encoder.classes_),
        'num_symptoms': len(all_symptoms)
    }
    
    with open('model/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nModel training completed successfully!")
    print(f"Model saved to: model/disease_model.pkl")
    print(f"Accuracy: {accuracy:.2%}")
    
    return model, label_encoder, symptom_encoder

if __name__ == '__main__':
    train_model()