# ct_scan_analyzer.py
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os

# --- CONFIGURACIÓN DEL MODELO ---
MODEL_PATH = "rsna-atd.keras"
model = None
MODEL_LOADED = False

def load_ct_model():
    """Carga el modelo Keras desde el disco. Se ejecuta una sola vez."""
    global model, MODEL_LOADED
    if MODEL_LOADED:
        return True
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ ERROR: No se encontró el archivo del modelo en la ruta: {MODEL_PATH}")
        return False
        
    try:
        model = load_model(MODEL_PATH, compile=False)
        MODEL_LOADED = True
        print("✅ Modelo de análisis de CT cargado exitosamente.")
        return True
    except Exception as e:
        print(f"❌ ERROR: No se pudo cargar el modelo '{MODEL_PATH}'. Detalles: {e}")
        return False

def _preprocess_image(image_path):
    """Preprocesa una imagen para que sea compatible con el modelo."""
    try:
        file_bytes = tf.io.read_file(image_path)
        # Asegurarse de que se decodifique como PNG. Cambiar si tus imágenes son JPG.
        image = tf.io.decode_png(file_bytes, channels=3, dtype=tf.uint8)
        image = tf.image.resize(image, [256, 256], method="bilinear")
        image = tf.cast(image, tf.float32) / 255.0
        return tf.expand_dims(image, axis=0)
    except Exception as e:
        print(f"Error al preprocesar la imagen: {e}")
        return None

def _interpret_predictions(prediction):
    """Interpreta la salida cruda del modelo en un diccionario estructurado."""
    results = {}
    organ_keys = ['liver', 'kidney', 'spleen']
    class_labels = ['Sano', 'Lesión Leve', 'Lesión Grave']
    
    # Lesiones binarias (sigmoid)
    results['bowel_injury'] = float(prediction[0][0][0])
    results['extravasation_injury'] = float(prediction[1][0][0])
    
    # Lesiones de órganos (softmax)
    for i, organ in enumerate(organ_keys, start=2):
        probs = prediction[i][0]
        results[f'{organ}_healthy'] = float(probs[0])
        results[f'{organ}_low'] = float(probs[1])
        results[f'{organ}_high'] = float(probs[2])
        pred_class = np.argmax(probs)
        results[f'{organ}_prediction'] = class_labels[pred_class]
    
    return results

def format_prediction_for_display(prediction):
    """Formatea la predicción en un texto legible para la UI."""
    bowel_prob = prediction['bowel_injury'] * 100
    extra_prob = prediction['extravasation_injury'] * 100
    
    text_content = [
        "--- ANÁLISIS DE TOMOGRAFÍA (IA) ---",
        f"Prob. de Lesión Intestinal: {bowel_prob:.2f}%",
        f"Prob. de Extravasación: {extra_prob:.2f}%",
        "\n--- Estado de Órganos ---",
        f"Hígado: {prediction['liver_prediction']}",
        f"  (Sano: {prediction['liver_healthy']:.2%}, Leve: {prediction['liver_low']:.2%}, Grave: {prediction['liver_high']:.2%})",
        "",
        f"Riñón: {prediction['kidney_prediction']}",
        f"  (Sano: {prediction['kidney_healthy']:.2%}, Leve: {prediction['kidney_low']:.2%}, Grave: {prediction['kidney_high']:.2%})",
        "",
        f"Bazo: {prediction['spleen_prediction']}",
        f"  (Sano: {prediction['spleen_healthy']:.2%}, Leve: {prediction['spleen_low']:.2%}, Grave: {prediction['spleen_high']:.2%})",
    ]
    return "\n".join(text_content)

def analyze_ct_scan(image_path):
    """Función principal para analizar una imagen de CT."""
    if not MODEL_LOADED:
        if not load_ct_model():
            error_msg = "El modelo de IA no está disponible."
            return {"error": error_msg}, error_msg

    preprocessed_image = _preprocess_image(image_path)
    if preprocessed_image is None:
        error_msg = "No se pudo leer o procesar la imagen."
        return {"error": error_msg}, error_msg

    try:
        raw_prediction = model.predict(preprocessed_image)
        interpreted_prediction = _interpret_predictions(raw_prediction)
        formatted_text = format_prediction_for_display(interpreted_prediction)
        return interpreted_prediction, formatted_text
    except Exception as e:
        error_msg = f"Ocurrió un error durante la predicción: {e}"
        return {"error": error_msg}, error_msg

# Cargar el modelo al iniciar el módulo
load_ct_model()