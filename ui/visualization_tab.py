import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from graph_with_height import create_plots  # Assuming this module exists
from animations import get_animation  # Assuming this module exists
from stack import create_3d_stack_plots
import random, time
from paths import available_days, file_paths, file_paths_dec
import xarray as xr
import numpy as np
import pandas as pd


def extract_time_from_path(file_path):
    data = xr.open_dataset(file_path)
    return pd.to_datetime(data['time'].values[0]).strftime('%Y-%m-%d %H:%M:%S')

def create_tab(notebook):
    visualization_tab = ttk.Frame(notebook)

    # Create a canvas and scrollbar for the visualization tab
    canvas = tk.Canvas(visualization_tab)
    scrollbar_y = ttk.Scrollbar(visualization_tab, orient=VERTICAL, command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(visualization_tab, orient=HORIZONTAL, command=canvas.xview)
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

    # Frame for buttons, inputs, and dropdowns
    control_frame = ttk.Frame(scrollable_frame, padding=10, borderwidth=2, relief="solid")
    control_frame.pack(fill='x', pady=10)

    canvas_widget_dbz = None
    canvas_widget_vel = None
    toolbar_dbz = None
    toolbar_vel = None
    combobox = None
    entry_height = None
    loading_bar = None
    combobox_day = None
    selected_day = None
    selected_paths = None

    def clear_existing_widgets():
        nonlocal canvas_widget_dbz, canvas_widget_vel, toolbar_dbz, toolbar_vel

        if canvas_widget_dbz is not None:
            canvas_widget_dbz.get_tk_widget().destroy()
            toolbar_dbz.destroy()
        
        if canvas_widget_vel is not None:
            canvas_widget_vel.get_tk_widget().destroy()
            toolbar_vel.destroy()

    def start_loading():
        nonlocal loading_bar
        loading_bar = ttk.Progressbar(scrollable_frame, orient=HORIZONTAL, mode='determinate', maximum=100)
        loading_bar.pack(fill='x', padx=10, pady=10)
    
        # Initialize the progress to 0
        loading_bar['value'] = 0
    
        # Simulate random progress
        for _ in range(10):  # 10 steps of loading
            increment = random.randint(5, 15)  # Randomly increment by 5 to 15
            loading_bar['value'] += increment
            scrollable_frame.update_idletasks()  # Force the GUI to update
            time.sleep(0.2)  # Simulate a delay for each step

        # Ensure the progress bar is filled to 100% at the end
        loading_bar['value'] = 100

    def stop_loading():
        if loading_bar:
            loading_bar.stop()
            loading_bar.destroy()

    def show_graphs_2d(file_path, height_index):
        nonlocal canvas_widget_dbz, toolbar_dbz
    
    # Clear existing widgets
        clear_existing_widgets()
    
    # Start loading animation
        start_loading()
    
    # Create the 2D plot with a fixed size
        fig = create_plots(file_path=file_path, height_index=height_index)
        fig.set_size_inches(8, 6)  # Fixed size for the figure
    
    # Attach the figure to the canvas
        canvas_widget_dbz = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas_widget_dbz.draw()
    
    # Create a toolbar
        toolbar_dbz = NavigationToolbar2Tk(canvas_widget_dbz, graph_frame)
        toolbar_dbz.update()
    
    # Pack the canvas and toolbar with a fixed size
        canvas_widget_dbz.get_tk_widget().pack(pady=10, expand=False, fill='none')
    
    # Stop loading animation
        stop_loading()

    def show_animations():
        nonlocal canvas_widget_dbz, toolbar_dbz
    
    # Clear existing widgets
        clear_existing_widgets()
    
    # Start loading animation
        start_loading()
    
    # Get the animation figure and animation object with a fixed size
        fig, anim = get_animation(selected_paths)
        fig.set_size_inches(8, 6)  # Fixed size for the animation
    
    # Attach the figure to the canvas
        canvas_widget_dbz = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas_widget_dbz.draw()
    
    # Create a toolbar
        toolbar_dbz = NavigationToolbar2Tk(canvas_widget_dbz, graph_frame)
        toolbar_dbz.update()
    
    # Pack the canvas and toolbar with a fixed size
        canvas_widget_dbz.get_tk_widget().pack(pady=10, expand=False, fill='none')

    # Stop loading animation
        stop_loading()

    def show_graphs_3d(file_path):
        nonlocal canvas_widget_dbz, canvas_widget_vel, toolbar_dbz, toolbar_vel
    
    # Clear existing widgets
        clear_existing_widgets()
    
    # Start loading animation
        start_loading()
    
    # Create the 3D plots (DBZ and VEL) with fixed sizes
        (fig_dbz, ax_dbz), (fig_vel, ax_vel) = create_3d_stack_plots(file_path)
        fig_dbz.set_size_inches(8, 6)  # Fixed size for the DBZ figure
        fig_vel.set_size_inches(8, 6)  # Fixed size for the VEL figure
    
    # Attach the DBZ figure to the canvas
        canvas_widget_dbz = FigureCanvasTkAgg(fig_dbz, master=graph_frame)
        canvas_widget_dbz.draw()
    
    # Create a toolbar
        toolbar_dbz = NavigationToolbar2Tk(canvas_widget_dbz, graph_frame)
        toolbar_dbz.update()
    
    # Pack the canvas and toolbar with a fixed size
        canvas_widget_dbz.get_tk_widget().pack(pady=10, expand=False, fill='none')
    
    # Attach the VEL figure to the canvas
        canvas_widget_vel = FigureCanvasTkAgg(fig_vel, master=graph_frame)
        canvas_widget_vel.draw()

    # Create a toolbar for the VEL plot
        toolbar_vel = NavigationToolbar2Tk(canvas_widget_vel, graph_frame)
        toolbar_vel.update()

    # Pack the canvas and toolbar for VEL plot with a fixed size
        canvas_widget_vel.get_tk_widget().pack(pady=10, expand=False, fill='none')

    # Stop loading animation
        stop_loading()


    def on_graphs_2d_button_click():
        nonlocal combobox, entry_height
        
        # Create and pack combobox if it doesn't exist
        if combobox is None:
            combobox_label = ttk.Label(control_frame, text="Select File:")
            combobox_label.pack(side=LEFT, padx=10, pady=5)
            
            combobox = ttk.Combobox(control_frame, values=[extract_time_from_path(fp) for fp in selected_paths])
            combobox.pack(side=LEFT, fill='x', padx=10, pady=5)
            combobox.current(0)  # Set default selection to the first item
        
        # Create and pack height entry if it doesn't exist
        if entry_height is None:
            entry_label = ttk.Label(control_frame, text="Height (0-80):")
            entry_label.pack(side=LEFT, padx=10, pady=5)
            
            entry_height = ttk.Entry(control_frame)
            entry_height.pack(side=LEFT, fill='x', padx=10, pady=5)
            entry_height.insert(0, "0")  # Default value
        
        selected_file = selected_paths[combobox.current()]
        height_value = entry_height.get()

        # Validate height input
        try:
            height_index = int(height_value)
            if 0 <= height_index <= 80:
                show_graphs_2d(selected_file, height_index)
            else:
                raise ValueError
        except ValueError:
            # Display an error message if the input is invalid
            ttk.Label(control_frame, text="Please enter a valid height (0-80).", foreground="red").pack(side=LEFT, pady=5)

    def on_graphs_3d_button_click():
        nonlocal combobox
        
        # Create and pack combobox if it doesn't exist
        if combobox is None:
            combobox_label = ttk.Label(control_frame, text="Select File:")
            combobox_label.pack(side=LEFT, padx=10, pady=5)
            
            combobox = ttk.Combobox(control_frame, values=[extract_time_from_path(fp) for fp in selected_paths])
            combobox.pack(side=LEFT, fill='x', padx=10, pady=5)
            combobox.current(0)  # Set default selection to the first item
        
        selected_file = selected_paths[combobox.current()]
        show_graphs_3d(selected_file)
    
    def on_animations_button_click():
        nonlocal combobox, entry_height
        
        # Remove combobox and entry_height if they exist
        if combobox is not None:
            combobox.pack_forget()
            combobox = None
        
        if entry_height is not None:
            entry_height.pack_forget()
            entry_height = None
        
        show_animations()

    def update_selected_day(event):
        nonlocal selected_day, selected_paths, combobox

        selected_day = combobox_day.get()
        if selected_day == available_days[0]:
            selected_paths = file_paths
        elif selected_day == available_days[1]:
            selected_paths = file_paths_dec
        
        earliest_time = extract_time_from_path(selected_paths[0])
        latest_time = extract_time_from_path(selected_paths[-1])
        
        info_text = f"Files from {selected_day} are chosen from {earliest_time} to {latest_time}"
        print(info_text)
        

        # Clear existing widgets when a new day is selected
        if combobox is not None:
            combobox.pack_forget()
            combobox = None

    # Day selection dropdown
    ttk.Label(control_frame, text="Select Day:").pack(side=LEFT, padx=10, pady=5)
    combobox_day = ttk.Combobox(control_frame, values=available_days)
    combobox_day.pack(side=LEFT, padx=10, pady=5)
    combobox_day.current(0)
    selected_day = combobox_day.get()
    selected_paths = file_paths
    combobox_day.bind("<<ComboboxSelected>>", update_selected_day)

    # Buttons for displaying different types of graphs/animations
    graphs_2d_button = ttk.Button(control_frame, text="Graphs-2D", command=on_graphs_2d_button_click)
    graphs_2d_button.pack(side=LEFT, padx=10, pady=5)

    graphs_3d_button = ttk.Button(control_frame, text="Graphs-3D", command=on_graphs_3d_button_click)
    graphs_3d_button.pack(side=LEFT, padx=10, pady=5)

    animations_button = ttk.Button(control_frame, text="Animations", command=on_animations_button_click)
    animations_button.pack(side=LEFT, padx=10, pady=5)

    # Frame for graph display
    graph_frame = ttk.Frame(scrollable_frame)
    graph_frame.pack(fill=BOTH, expand=True, pady=10)

    return visualization_tab

