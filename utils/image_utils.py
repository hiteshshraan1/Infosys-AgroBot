
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import streamlit as st
import os

@st.cache_resource
def load_model():
    model_path = "models/Plant_disease.h5"
    if not os.path.exists(model_path):
        st.error("⚠️ Model file not found at 'models/Plant_disease.h5'. Please upload your trained model.")
        return None
    model = tf.keras.models.load_model(model_path)
    return model

model = load_model()

CLASS_LABELS = [
    'Tomato_Bacterial_spot',
    'Pepper__bell___healthy',
    'Potato___Early_blight',
    'Tomato_Late_blight',
    'Tomato_healthy',
    'Tomato_Septoria_leaf_spot',
    'Potato___Late_blight',
    'Tomato_Early_blight'
]

def predict_disease(img_path):
    """
    Predicts the disease class from an image path using the CNN model.
    Returns the class index or error message.
    """
    if model is None:
        return "❌ Model not loaded."

    try:
        img = image.load_img(img_path, target_size=(128, 128))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        predictions = model.predict(img_array)
        class_idx = np.argmax(predictions[0])
        confidence = predictions[0][class_idx]

        st.write(f"🧾 Model Confidence: {confidence * 100:.2f}%")

        return CLASS_LABELS[class_idx]
    except Exception as e:
        return f"Error processing image: {e}"
