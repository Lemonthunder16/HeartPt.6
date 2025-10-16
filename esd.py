import serial
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from collections import deque
import os

# === Define class labels (update based on your model) ===
CLASS_LABELS = {
    0: "Normal",
    1: "Arrhythmia",
    2: "Tachycardia",
    3: "Bradycardia",
    4: "Irregular Beat"
}

# === Suppress TensorFlow warnings ===
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# === Load the trained LSTM model ===
model = load_model(r"C:\Projects\ESD PROJECT\ecg_classification_model.h5")

# === Setup Serial Connection with Arduino ===
SERIAL_PORT = "COM3"  # Change if needed
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {SERIAL_PORT}")
except serial.SerialException:
    print(f"❌ Error: Could not open {SERIAL_PORT}. Check if Arduino is connected.")
    exit()

# === Setup Data Storage & Plot ===
SEQUENCE_LENGTH = 187
bpm_buffer = deque(maxlen=SEQUENCE_LENGTH)
pulse_data_log = []

# === Live Plot Setup ===
plt.ion()
fig, ax = plt.subplots()
x_vals = np.arange(SEQUENCE_LENGTH)
y_vals = np.zeros(SEQUENCE_LENGTH)
plot_line, = ax.plot(x_vals, y_vals, 'r-', label="Pulse BPM")
ax.set_ylim(40, 200)
ax.set_xlim(0, SEQUENCE_LENGTH)
ax.set_title("Live Pulse BPM")
ax.set_xlabel("Time Steps")
ax.set_ylabel("BPM")
ax.legend()

print("✅ System Ready! Waiting for BPM Data...")

while True:
    try:
        # === Read Serial Data ===
        serial_data = ser.readline().strip()
        if serial_data:
            try:
                bpm_value = int(serial_data)
                bpm_buffer.append(bpm_value)
                pulse_data_log.append([bpm_value])

                if len(bpm_buffer) < SEQUENCE_LENGTH:
                    existing_values = np.array(list(bpm_buffer))
                    interpolated_values = np.interp(
                        np.linspace(0, len(existing_values) - 1, SEQUENCE_LENGTH),
                        np.arange(len(existing_values)),
                        existing_values
                    )
                else:
                    interpolated_values = np.array(list(bpm_buffer))

                # === Update Live Plot ===
                plot_line.set_xdata(np.arange(len(interpolated_values)))
                plot_line.set_ydata(interpolated_values)
                ax.set_xlim(0, SEQUENCE_LENGTH)
                plt.draw()
                plt.pause(0.01)

                # === Format for model ===
                bpm_array = interpolated_values / 400.0
                bpm_array = bpm_array.reshape(1, SEQUENCE_LENGTH, 1)

                # === Predict class ===
                prediction = model.predict(bpm_array, verbose=0)
                predicted_class = np.argmax(prediction)
                predicted_label = CLASS_LABELS[predicted_class]
                confidence = prediction[0][predicted_class]

                # === Log prediction ===
                pulse_data_log[-1].append(predicted_class)

                # === Display ===
                print(f"💓 BPM: {bpm_value} | Prediction: {predicted_label} | Confidence: {confidence:.2f}")

                # === Send to Arduino ===
                ser.write((predicted_label + "\n").encode())

            except ValueError:
                print("⚠️ Non-numeric data received. Skipping...")
                continue

    except KeyboardInterrupt:
        print("\n⏹️ Stopping BPM Monitoring...")
        ser.close()
        df = pd.DataFrame(pulse_data_log, columns=["BPM", "Prediction"])
        df.to_csv("pulse_predictions.csv", index=False)
        print("✅ BPM Predictions saved to pulse_predictions.csv")
        break
