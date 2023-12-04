import customtkinter as ctk

# Initialize the main window
root = ctk.CTk()
root.title("CustomTkinter Demo")
root.geometry("600x400")

# Function to update label
def update_label():
    label.config(text="Button Clicked!")

# # Create a label
# label = ctk.CTkLabel(root, text="Welcome to the CustomTkinter GUI!", text_font=("Arial", 16))
# label.pack(pady=20)

# Create a button
button = ctk.CTkButton(root, text="Click Me!", command=update_label)
button.pack(pady=10)

# Create an entry widget
entry = ctk.CTkEntry(root, width=200, placeholder_text="Type here")
entry.pack(pady=10)

# Create a checkbox
checkbox = ctk.CTkCheckBox(root, text="Check Me!")
checkbox.pack(pady=10)

# Create a switch
switch = ctk.CTkSwitch(root, text="Toggle Switch")
switch.pack(pady=10)

# Create a dropdown menu
options = ["Option A", "Option B", "Option C"]
dropdown = ctk.CTkOptionMenu(root, values=options)
dropdown.pack(pady=10)

# Start the GUI loop
root.mainloop()
