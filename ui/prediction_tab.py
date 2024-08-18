import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import IntVar, StringVar
from prediction_graphs import create_plots_dbz, create_plots_vel, prediction_plot_vel, prediction_plot_dbz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from paths import file_paths, file_paths_dec, available_days, all_paths
from get_differences import get_differences

canvas_widget = None
canvas_widget2 = None

selected_file = file_paths[0]
difference = 3
selected_file_new = file_paths[file_paths.index(selected_file) + difference]

def create_tab(notebook):
    prediction_tab = ttk.Frame(notebook)

    # Create a canvas and scrollbar for the prediction tab
    canvas = tk.Canvas(prediction_tab)
    scrollbar_y = ttk.Scrollbar(prediction_tab, orient=VERTICAL, command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(prediction_tab, orient=HORIZONTAL, command=canvas.xview)
    global scrollable_frame  # Make scrollable_frame accessible to other functions
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
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar_y.pack(side=RIGHT, fill=Y)
    scrollbar_x.pack(side=BOTTOM, fill=X)

    # Function to display the graph
    def show_graph():
        global canvas_widget, canvas_widget2

        # Clear the previous plots
        if canvas_widget:
            canvas_widget.get_tk_widget().pack_forget()

        if canvas_widget2:
            canvas_widget2.get_tk_widget().pack_forget()

        # Determine the graph type and create the first plot
        if graph_type_var.get() == "DBZ":
            fig1 = create_plots_dbz(selected_file_new, height_index_var.get())
        else:
            fig1 = create_plots_vel(selected_file_new, height_index_var.get())

        # Create the second plot using prediction_plot_vel() with height_index + 10
        if graph_type_var.get() == "DBZ":
            fig2 = prediction_plot_dbz(dbz, height_index_var.get())
        else:
            fig2 = prediction_plot_vel(vel, height_index_var.get())

        # Resize the plots
        fig1.set_size_inches(6, 6, forward=True)
        fig2.set_size_inches(6, 6, forward=True)

        # Display the first plot
        canvas_widget = FigureCanvasTkAgg(fig1, master=graph_frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(side=LEFT, padx=10, pady=10)

        label1 = ttk.Label(graph_frame, text="Actual")
        label1.pack(side=LEFT, padx=10, pady=(0, 10))

        # Display the second plot
        canvas_widget2 = FigureCanvasTkAgg(fig2, master=graph_frame)
        canvas_widget2.draw()
        canvas_widget2.get_tk_widget().pack(side=LEFT, padx=10, pady=10)

        label2 = ttk.Label(graph_frame, text="Predicted")
        label2.pack(side=LEFT, padx=10, pady=(0, 10))

    # Create a frame for the controls (top-left corner)
    controls_frame = ttk.Frame(scrollable_frame)
    controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

    # Dropdown menu to select a day
    day_var = StringVar(value=available_days[0])
    
    def update_times_menu(*args):
        selected_day_index = available_days.index(day_var.get())
        paths = all_paths[selected_day_index]
        time_diffs = get_differences(paths)
        times_menu['menu'].delete(0, 'end')
        for i, diff in enumerate(time_diffs):
            times_menu['menu'].add_command(label=diff, command=lambda value=diff: time_var.set(value))

    day_var.trace('w', update_times_menu)

    day_label = ttk.Label(controls_frame, text="Select Date:")
    day_label.grid(row=0, column=0, padx=5, pady=5)

    day_menu = ttk.OptionMenu(controls_frame, day_var, available_days[0], *available_days)
    day_menu.grid(row=0, column=1, padx=5, pady=5)

    # Dropdown menu to select a time
    time_var = StringVar(value="")
    
    # Initialize `times_menu` here and make it global
    global times_menu
    times_menu = ttk.OptionMenu(controls_frame, time_var, "")
    times_menu.grid(row=1, column=1, padx=5, pady=5)

    def print_time_and_file(*args):
        global selected_file_new

        selected_day_index = available_days.index(day_var.get())
        paths = all_paths[selected_day_index]
        selected_time_index = get_differences(paths).index(float(time_var.get()))
        selected_file = paths[selected_time_index + 1]
        selected_file_new = file_paths[file_paths.index(selected_file) + difference]
        print(f"Selected Time: {time_var.get()} minutes")
        print(f"Corresponding File: {selected_file}")
        return selected_file


    time_var.trace('w', print_time_and_file)

    time_label = ttk.Label(controls_frame, text="Select Time after initial(min):")
    time_label.grid(row=1, column=0, padx=5, pady=5)

    # Create a height index input
    height_index_label = ttk.Label(controls_frame, text="Height Index (0-80):")
    height_index_label.grid(row=2, column=0, padx=5, pady=5)

    height_index_var = IntVar(value=0)
    height_index_entry = ttk.Entry(controls_frame, textvariable=height_index_var, width=5)
    height_index_entry.grid(row=2, column=1, padx=5, pady=5)

    # Create a toggle button to switch between DBZ and VEL graphs
    graph_type_var = StringVar(value="DBZ")

    def toggle_graph_type():
        if graph_type_var.get() == "DBZ":
            graph_type_var.set("VEL")
        else:
            graph_type_var.set("DBZ")
        show_graph()

    toggle_button = ttk.Button(controls_frame, text="Toggle Graph Type", command=toggle_graph_type)
    toggle_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    # Create a button to update the graph without toggling
    update_button = ttk.Button(controls_frame, text="Update Graph", command=show_graph)
    update_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    # Create a frame for the graph (below the controls frame)
    graph_frame = ttk.Frame(scrollable_frame, width=800)
    graph_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nw", columnspan=2)

    # Initially, no plot is displayed
    canvas_widget = None
    canvas_widget2 = None

    # Initialize the times dropdown based on the default selected day
    update_times_menu()

    return prediction_tab
