import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext, Canvas, Frame, Entry
import re
import subprocess
import threading
import os
import sys
from urllib.request import urlretrieve
import winreg
import shutil
import atexit
import json

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

INDEX_JS_PATH = get_resource_path("index.js")
process = None

def validate_inputs():
    """Validate the Discord invite URL."""
    discord_invite = discord_invite_url_var.get()
    if not re.match(r"^https?://", discord_invite):
        messagebox.showwarning("Validation Error", "DISCORD_INVITE_URL must be a valid link (starting with http:// or https://).")
        return False
    return True

def update_constants():
    """Update constants in the index.js file."""
    if not validate_inputs():
        return

    try:
        with open(INDEX_JS_PATH, "r") as file:
            content = file.read()

        content = re.sub(r"const BOT_TOKEN = '.*?';", f"const BOT_TOKEN = '{bot_token_var.get()}';", content)
        content = re.sub(r"const CLIENT_ID = '.*?';", f"const CLIENT_ID = '{client_id_var.get()}';", content)
        content = re.sub(r"const ALLOWED_USER_ID = '.*?';", f"const ALLOWED_USER_ID = '{allowed_user_id_var.get()}';", content)
        content = re.sub(r"const DISCORD_INVITE_URL = '.*?';", f"const DISCORD_INVITE_URL = '{discord_invite_url_var.get()}';", content)
        content = re.sub(r"const REPEAT_COUNT = '.*?';", f"const REPEAT_COUNT = '{repeat_count_var.get()}';", content)

        with open(INDEX_JS_PATH, "w") as file:
            file.write(content)

        messagebox.showinfo("Success", "Constants updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def run_script():
    """Run the index.js script and display logs."""
    global process
    try:

        log_text.insert("end", f"Attempting to run: {INDEX_JS_PATH}\n")
        log_text.see("end")

     
        notebook.select(log_frame)
        log_text.delete(1.0, "end")

        def run_and_log():
            global process
            try:
                project_dir = os.path.dirname(os.path.abspath(__file__))
                log_text.insert("end", f"Working directory: {project_dir}\n")

                process = subprocess.Popen(
                    ["node", INDEX_JS_PATH],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_dir  
                )

                while True:
                    error = process.stderr.readline()
                    if error:
                        log_text.insert("end", f"ERROR: {error}\n")
                        log_text.see("end")
                    else:
                        break

                for line in process.stdout:
                    log_text.insert("end", line)
                    log_text.see("end")

            except Exception as e:
                log_text.insert("end", f"Error running script: {str(e)}\n")
                log_text.see("end")

        threading.Thread(target=run_and_log, daemon=True).start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        log_text.insert("end", f"Error: {str(e)}\n")
        log_text.see("end")

def stop_script():
    """Stop the currently running script."""
    global process
    if process and process.poll() is None:  
        process.terminate()
        log_text.insert("end", "\nScript stopped.\n")
        log_text.see("end")
    else:
        messagebox.showinfo("Info", "No script is currently running.")

def restart_script():
    """Restart the script."""
    stop_script()  
    run_script() 


def create_styled_label(parent, text):
    """Create a styled label with gradient, glow and shadow effect."""
    frame = Frame(parent, bg="#0d1117")
    frame.grid_propagate(False)
    
    
    glow_label = ttk.Label(frame,
                        text=text,
                        bootstyle="info",
                        font=("Bahnschrift", 11, "bold"),  # Added bold
                        foreground="#0066cc")
    glow_label.place(x=1, y=1)
    
    label = ttk.Label(frame, 
                    text=text,
                    bootstyle="info",
                    font=("Bahnschrift", 11, "bold"),  # Added bold
                    foreground="#00a8ff")
    
    label.place(x=0, y=0)
    
    return frame

# Update the create_rounded_entry function to have larger dimensions
def create_rounded_entry(parent, textvariable, show_dots=False):
    """Create a styled rounded entry field with enhanced 3D effect and gradient."""
    # Create a container frame that won't resize
    container = Frame(parent, bg="#1e1e1e")
    container.pack_propagate(False)
    container.configure(width=400, height=45)  # Increased from 300x35
    
    outer_frame = Frame(container, bg="#1e1e1e", highlightthickness=1, 
                     highlightbackground="#00a8ff", bd=0)
    outer_frame.pack(fill="both", expand=True)
    
    middle_frame = Frame(outer_frame, bg="#252525", 
                      highlightthickness=1,
                      highlightbackground="#0066cc",
                      bd=0)
    middle_frame.pack(fill="both", expand=True, padx=1, pady=1)
    
    inner_frame = Frame(middle_frame, bg="#151515", 
                     highlightthickness=1,
                     highlightbackground="#252525",
                     bd=0)
    inner_frame.pack(fill="both", expand=True, padx=1, pady=1)
    
    entry = Entry(inner_frame, 
                textvariable=textvariable,
                bg="#1a1a1a",
                fg="#ffffff",
                insertbackground="#00a8ff",
                relief="flat",
                font=("Bahnschrift", 11, "bold"),
                show="●" if show_dots else "",
                bd=0)
    entry.pack(fill="both", expand=True, padx=8, pady=6)
    
    def on_enter(e):
        outer_frame.config(highlightbackground="#00ccff")
        middle_frame.config(highlightbackground="#00a8ff")
    
    def on_leave(e):
        outer_frame.config(highlightbackground="#00a8ff")
        middle_frame.config(highlightbackground="#0066cc")
    
    entry.bind("<Enter>", on_enter)
    entry.bind("<Leave>", on_leave)
    
    return container

def check_node_installed():
    """Check if Node.js is installed."""
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_node():
    """Download and install Node.js."""
    try:
        url = "https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi"
        installer_path = os.path.join(os.getenv('TEMP'), "node_installer.msi")
        urlretrieve(url, installer_path)
        
        subprocess.run(['msiexec', '/i', installer_path, '/quiet', '/norestart'], check=True)
        os.remove(installer_path)
        messagebox.showinfo('Success', 'Node.js installed successfully!')
        os.environ['PATH'] = f"{os.environ['PATH']};C:\\Program Files\\nodejs"
    except Exception as e:
        messagebox.showerror('Error', f'Failed to install Node.js: {e}')

def install_dependencies():
    """Install Discord.js and dotenv using npm."""
    try:
        # Get the directory where index.js is located
        js_dir = os.path.dirname(os.path.abspath(INDEX_JS_PATH))
        
        # Initialize npm project if package.json doesn't exist
        if not os.path.exists(os.path.join(js_dir, 'package.json')):
            subprocess.run(['npm', 'init', '-y'], check=True, cwd=js_dir)
        
        # Install dependencies
        subprocess.run(['npm', 'install', 'discord.js', 'dotenv'], 
                      check=True, 
                      cwd=js_dir)
        
        messagebox.showinfo('Success', 'Dependencies installed successfully!')
    except subprocess.CalledProcessError as e:
        messagebox.showerror('Error', f'Failed to install dependencies: {e}')

def setup_environment():
    """Set execution policy and install required dependencies."""
    try:
        # Set execution policy
        subprocess.run([
            'powershell',
            'Start-Process',
            'powershell',
            '-Verb', 'RunAs',
            '-ArgumentList',
            '"-Command Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"'
        ], check=True)
        
        # Check and install Node.js if needed
        if not check_node_installed():
            install_node()
            
        # Install Discord.js and dotenv
        install_dependencies()
        
        messagebox.showinfo('Success', 'Environment setup completed successfully!')
    except Exception as e:
        messagebox.showerror('Error', f'Setup failed: {e}')

# Create the main window with ttkbootstrap
root = ttk.Window(themename="darkly")
root.title("Discord Bot Manager")
root.state("zoomed")

# Create agreement frame that will overlay the main content
agreement_frame = ttk.Frame(root, style='dark.TFrame')
agreement_frame.place(relx=0.5, rely=0.5, anchor="center")

agreement_text = ("I AGREE TO ALL INFORMATION THAT WAS SET AT "
                 "https://github.com/easteregg-lover/Server-raider-discord, "
                 "AND I AGREE THAT I READ EVERYTHING THAT WAS THERE.")

ttk.Label(
    agreement_frame,
    text=agreement_text,
    font=("Bahnschrift", 12, "bold"),  # Increased from 10
    wraplength=850,  # Increased from 750
    justify="center"
).pack(padx=30, pady=15)  # Increased padding

agreement_var = ttk.BooleanVar()

def on_agree():
    if agreement_var.get():
        agreement_frame.place_forget()  # Hide agreement frame
        container.grid()  # Show main content
        
        # Ensure container fills the window
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
    else:
        messagebox.showwarning(
            "Agreement Required",
            "You must agree to the terms to use this application."
        )

def on_cancel():
    root.quit()

# Checkbox
ttk.Checkbutton(
    agreement_frame,
    text="I Agree",
    variable=agreement_var,
    bootstyle="primary"
).pack(pady=5)

# Buttons
button_frame = ttk.Frame(agreement_frame)
button_frame.pack(pady=10)

ttk.Button(
    button_frame,
    text="Continue",
    command=on_agree,
    bootstyle="primary"
).pack(side="left", padx=5)

ttk.Button(
    button_frame,
    text="Exit",
    command=on_cancel,
    bootstyle="danger"
).pack(side="left", padx=5)

ttk.Button(
    button_frame,
    text='Setup Environment',
    command=setup_environment,
    bootstyle='primary'
).pack(side='left', padx=5)

# Create but initially hide the main container
container = Frame(root, bg="#0d1117")
container.grid(row=0, column=0, sticky="nsew")  # Changed from grid_remove() to grid()
container.grid_remove()  # Hide container initially

# Configure grid weights for dynamic resizing
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create info label with link
info_label = ttk.Label(
    container, 
    text="More info: https://github.com/easteregg-lover/Server-raider-discord",
    font=("Bahnschrift", 11, "bold"),  # Increased from 9
    bootstyle="info",
    cursor="hand2"  # Change cursor to hand when hovering
)
info_label.grid(row=1, column=0, sticky="sw", padx=20, pady=10)

# Add click event to open the link
def open_link(event):
    import webbrowser
    webbrowser.open("https://github.com/easteregg-lover/Server-raider-discord")

info_label.bind("<Button-1>", open_link)

# Create a Notebook (tabbed interface)
notebook = ttk.Notebook(container, bootstyle="primary")
notebook.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

# Tab 1: Edit Constants
edit_frame = ttk.Frame(notebook)
notebook.add(edit_frame, text="Edit Constants")

# Create a container for vertical centering
vertical_center = ttk.Frame(edit_frame)
vertical_center.pack(expand=True, fill="both", padx=20, pady=100)  # Added top padding

# Configure grid weights for vertical centering
vertical_center.grid_rowconfigure(0, weight=1)  # Top spacing
vertical_center.grid_rowconfigure(6, weight=1)  # Bottom spacing
vertical_center.grid_columnconfigure(1, weight=1)

# Input fields for constants - now in vertical_center frame
ttk.Label(vertical_center, text="BOT_TOKEN:", bootstyle="info", font=("Bahnschrift", 11, "bold")).grid(row=1, column=0, sticky="w", padx=15)
bot_token_var = ttk.StringVar()
create_rounded_entry(vertical_center, bot_token_var, show_dots=True).grid(row=1, column=1, sticky="ew", padx=10)

ttk.Label(vertical_center, text="CLIENT_ID:", bootstyle="info", font=("Bahnschrift", 11, "bold")).grid(row=2, column=0, sticky="w", padx=15)
client_id_var = ttk.StringVar()
create_rounded_entry(vertical_center, client_id_var, show_dots=True).grid(row=2, column=1, sticky="ew", padx=10)

ttk.Label(vertical_center, text="ALLOWED_USER_ID:", bootstyle="info", font=("Bahnschrift", 11, "bold")).grid(row=3, column=0, sticky="w", padx=15)
allowed_user_id_var = ttk.StringVar()
create_rounded_entry(vertical_center, allowed_user_id_var).grid(row=3, column=1, sticky="ew", padx=10)

ttk.Label(vertical_center, text="DISCORD_INVITE_URL:", bootstyle="info", font=("Bahnschrift", 11, "bold")).grid(row=4, column=0, sticky="w", padx=15)
discord_invite_url_var = ttk.StringVar()
create_rounded_entry(vertical_center, discord_invite_url_var).grid(row=4, column=1, sticky="ew", padx=10)

ttk.Label(vertical_center, text="REPEAT_COUNT:", bootstyle="info", font=("Bahnschrift", 11, "bold")).grid(row=5, column=0, sticky="w", padx=15)
repeat_count_var = ttk.StringVar()
create_rounded_entry(vertical_center, repeat_count_var).grid(row=5, column=1, sticky="ew", padx=10)

# Buttons for updating constants and running the script
button_frame = Frame(vertical_center, bg="#0d1117")
button_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")  # Added sticky="ew" to expand frame
button_frame.grid_columnconfigure(0, weight=1)  # Allow frame to expand
button_frame.grid_columnconfigure(1, weight=1)  # Center buttons

# Center the buttons within the frame
ttk.Button(button_frame, text="Update Constants", command=update_constants, bootstyle="primary").grid(row=0, column=0, padx=5, sticky="e")
ttk.Button(button_frame, text="Run Script", command=run_script, bootstyle="primary").grid(row=0, column=1, padx=5, sticky="w")

# Tab 2: Logs
log_frame = ttk.Frame(notebook)
notebook.add(log_frame, text="Logs")

# Configure grid weights for the log frame
log_frame.grid_rowconfigure(0, weight=1)
log_frame.grid_columnconfigure(0, weight=1)

# Log text area
log_text = scrolledtext.ScrolledText(
    log_frame, 
    width=100,  # Increased from 80
    height=25,  # Increased from 20
    bg="#0d1117", 
    fg="white", 
    insertbackground="white", 
    relief="sunken", 
    borderwidth=3, 
    font=("Bahnschrift", 12, "bold")  # Increased from 10
)
log_text.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

# Stop and Restart buttons
button_frame = ttk.Frame(log_frame)
button_frame.grid(row=1, column=0, sticky="ew", pady=10)
ttk.Button(button_frame, text="Stop", command=stop_script, bootstyle="danger").pack(side="left", padx=10)
ttk.Button(button_frame, text="Restart", command=restart_script, bootstyle="warning").pack(side="left", padx=10)

# Update font sizes
style = ttk.Style()
style.configure('TNotebook.Tab', font=("Bahnschrift", 12, "bold"))  # Increased from 10
style.configure('primary.TButton', font=("Bahnschrift", 12, "bold"))  # Increased from 10
style.configure('danger.TButton', font=("Bahnschrift", 12, "bold"))  # Increased from 10
style.configure('warning.TButton', font=("Bahnschrift", 12, "bold"))  # Increased from 10
style.configure('TCheckbutton', font=("Bahnschrift", 12, "bold"))

# Resize and center GUI dynamically
def resize_gui(event):
    width, height = event.width, event.height
    if width > 1200 or height > 800:  # If window size is too large
        notebook.grid_configure(padx=120, pady=120)  # Increased from 100
    else:
        notebook.grid_configure(padx=30, pady=30)  # Increased from 20

root.bind("<Configure>", resize_gui)

def find_latest_mei_folder():
    """Find the newest _MEI**** folder in Temp."""
    temp_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Temp")
    mei_folders = [f for f in os.listdir(temp_dir) if f.startswith("_MEI")]

    if not mei_folders:
        print("No _MEI folder found in Temp!")
        return None

    # Get the latest _MEI folder based on creation time
    latest_mei = max(mei_folders, key=lambda f: os.path.getctime(os.path.join(temp_dir, f)))
    return os.path.join(temp_dir, latest_mei)

def copy_and_move_node_modules():
    """Copy node_modules from Downloads and move it to the newest _MEI folder."""
    downloads_path = os.path.expanduser("~/Downloads/node_modules")
    mei_path = find_latest_mei_folder()

    if not mei_path:
        return  # No _MEI folder found, stop execution

    try:
        if os.path.exists(downloads_path):
            # Copy node_modules to _MEI folder
            copied_path = os.path.join(mei_path, "node_modules")
            shutil.copytree(downloads_path, copied_path)
            print(f"Successfully copied node_modules to {copied_path}")

            # Move the copied folder to its final location inside _MEI
            final_path = os.path.join(mei_path, "node_modules")
            shutil.move(copied_path, final_path)
            print(f"Moved node_modules to {final_path}")
        else:
            print("node_modules folder not found in Downloads!")
    except Exception as e:
        print(f"Error while copying/moving node_modules: {e}")

# Call the function
copy_and_move_node_modules()

def cleanup_node_modules():
    """Deletes the node_modules folder when the app closes."""
    mei_path = find_latest_mei_folder()
    if mei_path:
        node_modules_path = os.path.join(mei_path, "node_modules")
        if os.path.exists(node_modules_path):
            shutil.rmtree(node_modules_path)
            print(f"Deleted {node_modules_path} on exit.")

# Register cleanup function to execute when app exits
atexit.register(cleanup_node_modules)


# Run the application
root.mainloop()