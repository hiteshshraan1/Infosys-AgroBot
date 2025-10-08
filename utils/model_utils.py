
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import streamlit as st
import os

@st.cache_resource
def load_tf_model():
    """Loads and caches the TensorFlow .h5 model."""
    model_path = "models/plant_disease_cnn.h5"
    if not os.path.exists(model_path):
        st.error(f"⚠️ Model file not found at '{model_path}'. Please make sure it exists.")
        return None
    try:
        model = tf.keras.models.load_model(model_path)
        print("Model loaded successfully!")
        return model
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        return None

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
    Predicts the disease class from an image path using your trained CNN model.
    Returns the predicted class name (string) and confidence score.
    """
    model = load_tf_model()
    if model is None:
        return "Model not loaded.", 0.0

    try:
        img = image.load_img(img_path, target_size=(128, 128))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])

        predicted_label = CLASS_LABELS[class_idx]
        return predicted_label, confidence

    except Exception as e:
        st.error(f"Error during prediction: {e}")
        return f"Error: {e}", 0.0