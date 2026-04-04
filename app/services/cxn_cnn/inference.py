# NOTE:
# 当前项目中检测模型尚未接入真实训练好的权重，
# 本文件中的预测函数返回的是「伪数据占位」，
# 方便演示完整的异步检测流程与前后端联调。


def predict_cnn(file_path: str) -> float:
    """
    Predict using CNN model on binary image.
    """
    # Placeholder: convert binary to image
    # In practice, implement binary to grayscale image conversion
    # image = convert_binary_to_image(file_path)
    # prediction = cnn_model.predict(np.expand_dims(image, axis=0))[0][0]
    del file_path  # 占位阶段未读文件
    prediction = 0.5  # Placeholder
    return float(prediction)
