import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import home_tab
import visualization_tab
import prediction_tab

# Create the main application window
app = ttk.Window(themename="cyborg")
app.title("Full Screen GUI")


# Make the window fullscreen and non-resizable
app.attributes('-fullscreen', True)
app.resizable(False, False)

# Create a Notebook (tabbed interface)

notebook = ttk.Notebook(app)

# Create tabs and link them to the respective content
home_tab = home_tab.create_tab(notebook)
visualization_tab = visualization_tab.create_tab(notebook)
prediction_tab = prediction_tab.create_tab(notebook)

# Add tabs to the notebook
notebook.add(home_tab, text='Home')
notebook.add(visualization_tab, text='Visualization')
notebook.add(prediction_tab, text='Prediction')

# Position the Notebook in the grid layout
notebook.grid(row=0, column=0, sticky="nsew")

# Add a close button in the top right corner, outside the notebook
close_button = ttk.Button(app, text="Close", command=app.destroy)
close_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

# Configure the grid to make the notebook expand
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

# Start the application's main loop
app.mainloop()
