import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import json

def load_metrics_from_json(file_path):
    """Load metrics from a JSON file."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_meter_style(value):
    """Determine the style of the meter based on the value."""
    if value >= 90:
        return "success"
    elif 70 <= value < 90:
        return "warning"
    else:
        return "danger"

def get_progress_style(value, max_value):
    """Determine the style of the progress bar based on the value."""
    percentage = (value / max_value) * 100
    if percentage <= 30:
        return "success"
    elif 30 < percentage <= 70:
        return "warning"
    else:
        return "danger"

def create_tab(notebook):
    file_path = r'metrics.json'
    metrics = load_metrics_from_json(file_path)
    home_tab = ttk.Frame(notebook)

    # Create a canvas and scrollbar for the home tab
    canvas = tk.Canvas(home_tab)
    scrollbar_y = ttk.Scrollbar(home_tab, orient=VERTICAL, command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(home_tab, orient=HORIZONTAL, command=canvas.xview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Pack the scrollbars and canvas
    scrollbar_y.pack(side=RIGHT, fill=Y)
    scrollbar_x.pack(side=BOTTOM, fill=X)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Ensure the scrollable_frame fills the canvas
    scrollable_frame.pack(expand=True, fill=BOTH)

    # Dashboard: Display Accuracy
    accuracy = metrics['accuracy']
    accuracy_style = get_meter_style(accuracy)

    accuracy_gauge = ttk.Meter(
        scrollable_frame, 
        amounttotal=100,
        amountused=accuracy, 
        metertype='full',
        subtext='Accuracy (%)', 
        wedgesize=accuracy*1.75,  # Fixed size to ensure consistent display
        bootstyle=accuracy_style,  # Valid ttkbootstrap style
        metersize=300,
        textfont=("Helvetica", 16),
        subtextfont=("Helvetica", 14)
    )
    accuracy_gauge.configure(textbackground=None)
    accuracy_gauge.pack(pady=20, padx=20)

    # Dashboard: Display Errors using progress bars
    rmse = metrics['rmse']
    mae = metrics['mae']
    percentage_error = metrics['percentage_error']

    error_frame = ttk.Labelframe(scrollable_frame, text="Error Metrics")
    error_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    rmse_style = get_progress_style(rmse, 5)
    mae_style = get_progress_style(mae, 5)
    percentage_error_style = get_progress_style(percentage_error, 10)

    rmse_bar = ttk.Progressbar(error_frame, 
                               value=rmse, 
                               maximum=5, 
                               bootstyle=rmse_style, 
                               length=200)
    rmse_label = ttk.Label(error_frame, text=f"Root Mean Squared Error: {rmse:.3f}", font=("Helvetica", 14))
    rmse_label.pack(anchor='w', pady=5, padx=10)
    rmse_bar.pack(anchor='w', pady=5, padx=10)

    mae_bar = ttk.Progressbar(error_frame, 
                              value=mae, 
                              maximum=5, 
                              bootstyle=mae_style, 
                              length=200)
    mae_label = ttk.Label(error_frame, text=f"Mean Absolute Error: {mae:.3f}", font=("Helvetica", 14))
    mae_label.pack(anchor='w', pady=5, padx=10)
    mae_bar.pack(anchor='w', pady=5, padx=10)

    percentage_error_bar = ttk.Progressbar(error_frame, 
                                           value=percentage_error, 
                                           maximum=10, 
                                           bootstyle=percentage_error_style, 
                                           length=200)
    percentage_error_label = ttk.Label(error_frame, text=f"Percentage Error: {percentage_error:.3f}%", font=("Helvetica", 14))
    percentage_error_label.pack(anchor='w', pady=5, padx=10)
    percentage_error_bar.pack(anchor='w', pady=5, padx=10)

    # Dashboard: Display Additional Information
    info_frame = ttk.Labelframe(scrollable_frame, text="Additional Information")
    info_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    models_label = ttk.Label(info_frame, text="Models Used: Neural Network Model, Mathematical Model, Neural Combinational Model", font=("Helvetica", 14))
    models_label.pack(anchor='w', pady=5, padx=10)

    libraries_label = ttk.Label(info_frame, text="Libraries Used: TensorFlow, Scikit-learn, NumPy, Matplotlib, Pysteps, Pandas", font=("Helvetica", 14))
    libraries_label.pack(anchor='w', pady=5, padx=10)

    credits_label = ttk.Label(info_frame, text="Credits: Team Falcons", font=("Helvetica", 14))
    credits_label.pack(anchor='w', pady=5, padx=10)

    return home_tab


