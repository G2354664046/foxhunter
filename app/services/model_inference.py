import joblib
import numpy as np

# NOTE:
# 当前项目中检测模型尚未接入真实训练好的权重，
# 本文件中的预测函数返回的是「伪数据占位」，
# 方便演示完整的异步检测流程与前后端联调。

def predict_random_forest(features: dict) -> float:
    """
    Predict using Random Forest model on structured features.
    """
    # Placeholder: convert features to numpy array
    # Here we demonstrate using some of the extracted header values plus
    # the first few HOG coefficients (if available) for the RF model input.
    header_vals = [
        features.get('size_of_image', 0),
        features.get('number_of_sections', 0)
    ]
    hog_vals = features.get('hog_features', [])
    if hog_vals:
        # take first 10 hog features as example
        header_vals += hog_vals[:10]
    feature_vector = np.array(header_vals)
    # prediction = rf_model.predict_proba(feature_vector.reshape(1, -1))[0][1]
    prediction = 0.5  # Placeholder
    return prediction

def predict_cnn(file_path: str) -> float:
    """
    Predict using CNN model on binary image.
    """
    # Placeholder: convert binary to image
    # In practice, implement binary to grayscale image conversion
    # image = convert_binary_to_image(file_path)
    # prediction = cnn_model.predict(np.expand_dims(image, axis=0))[0][0]
    prediction = 0.5  # Placeholder
    return prediction

def ensemble_prediction(rf_confidence: float, cnn_confidence: float) -> dict:
    """
    Ensemble prediction using weighted voting.
    """
    # Weighted average
    weight_rf = 0.6
    weight_cnn = 0.4
    final_score = weight_rf * rf_confidence + weight_cnn * cnn_confidence
    
    is_malware = final_score > 0.5
    confidence = final_score if is_malware else 1 - final_score
    
    return {
        "is_malware": is_malware,
        "confidence": confidence,
        "rf_score": rf_confidence,
        "cnn_score": cnn_confidence
    }