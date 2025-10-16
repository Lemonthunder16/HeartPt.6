import serial
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import os
import time

# === Define class labels ===
CLASS_LABELS = {
    "Normal": 70,
    "Arrhythmia": 85,
    "Tachycardia": 130,
    "Bradycardia": 45,
    "Irregular Beat": 60
}

# === Serial Port Setup ===
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SEQUENCE_LENGTH = 187

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {SERIAL_PORT}")
except serial.SerialException:
    print(f"❌ Error: Could not open {SERIAL_PORT}. Check Arduino.")
    exit()

# === Plot Setup ===
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

# === Simulated data for display and testing ===
simulated_inputs = {
    "Normal": [70] * SEQUENCE_LENGTH,
    "Tachycardia": [130] * SEQUENCE_LENGTH,
    "Bradycardia": [45] * SEQUENCE_LENGTH,
    "Irregular Beat": [60 + (-1)**i * i for i in range(SEQUENCE_LENGTH)],
    "Arrhythmia": [85 + 10 * np.sin(i / 5) for i in range(SEQUENCE_LENGTH)]
}

print("🧪 Printing Simulated Heartbeat Types Without Model...")

for label, bpm_list in simulated_inputs.items():
    fake_bpm = int(np.mean(bpm_list))

    # Plot
    interpolated_values = np.array(bpm_list)
    plot_line.set_ydata(interpolated_values)
    plot_line.set_xdata(np.arange(SEQUENCE_LENGTH))
    plt.draw()
    plt.pause(0.01)

    # Print and send fake label
    print(f"💓 BPM: ~{fake_bpm} | Prediction: {label} | Confidence: Simulated")
    ser.write((label + "\n").encode())
    time.sleep(3)

print("\n✅ Done. All heartbeat types simulated.")
ser.close()
input("Press Enter to close plot...")
plt.ioff()
plt.close()
