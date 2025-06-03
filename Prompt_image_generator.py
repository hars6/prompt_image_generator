import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import os
from tkinter import messagebox

# Function to check internet connectivity
def check_internet():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False

# Function to update the connectivity status
def update_connectivity_status():
    if check_internet():
        connectivity_label.config(text="Connected", bg="#4CAF50", fg="white")
    else:
        connectivity_label.config(text="Disconnected", bg="#F44336", fg="white")
    root.after(5000, update_connectivity_status)  # Check every 5 seconds

# Function to fetch the image asynchronously
def fetch_image_async(entered_text):
    global fetched_image
    image_url = 'https://image.pollinations.ai/prompt/' + entered_text
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check for a successful response (status code 200)

        # Open the image using PIL from the response content
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        image = image.resize((240, 200))  # Resize the image to fit the window

        # Store the image globally for later use in the download function
        fetched_image = image

        # After image fetching, update the UI in the main thread
        root.after(0, update_image_label, image)  # Safely update the image in the Tkinter main thread

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        # If fetching image fails, use a placeholder image
        root.after(0, update_image_label, None)  # Update the label with a placeholder image

# Function to update the image label in the UI
def update_image_label(image):
    if image:
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection
        loading_label.pack_forget()  # Hide loading animation after the image is shown
        download_button.pack(pady=20)  # Show download button once the image is fetched
    else:
        # Use a placeholder image in case of an error
        placeholder = Image.new("RGB", (240, 200), color="grey")
        photo = ImageTk.PhotoImage(placeholder)
        image_label.config(image=photo)
        image_label.image = photo
        loading_label.pack_forget()  # Hide loading animation after the placeholder is shown
        download_button.pack_forget()  # Hide download button if image fetching failed

# Function to start the loading animation
def start_loading_animation():
    loading_images = ['.', '..', '...', '....', ' ']
    def update_loading_image(i):
        loading_label.config(text=loading_images[i % len(loading_images)], fg="#FFA500")
        root.after(200, update_loading_image, i + 1)  # Repeat every 200ms

    update_loading_image(0)  # Start animation

# Function to handle button click
def on_button_click(event=None):
    # Get the text from the textbox and set it to the label
    entered_text = text_box.get()
    
    if not entered_text.strip():
        # Show error message for empty input
        connectivity_label.config(text="Please enter text", bg="orange", fg="black")
        return
    
    # Show loading animation while fetching image
    loading_label.pack(pady=20)
    start_loading_animation()
    
    # Start a background thread to fetch the image
    threading.Thread(target=fetch_image_async, args=(entered_text,)).start()

# Function to download the fetched image to the Downloads folder
def download_image():
    if fetched_image:
        # Get the path to the Downloads folder
        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Save the image as a PNG file in the Downloads folder
        image_path = os.path.join(download_folder, "generated_image.png")
        fetched_image.save(image_path)

        # Notify the user that the image has been downloaded
        messagebox.showinfo("Download Complete", f"Image has been downloaded to {image_path}")
    else:
        messagebox.showerror("Error", "No image to download.")

# Create the main window
root = tk.Tk()
root.title("Prompt Image Generator")

# Set the window size and background color
root.geometry("500x500")
root.config(bg="#ECECEC")

# Create a Label widget to display the image
image_label = tk.Label(root, bg="#ECECEC")
image_label.pack(pady=20)

# Create a Textbox widget below the image
text_box = tk.Entry(root, width=40, font=("Helvetica", 12), bd=2, relief="solid", justify="center")
text_box.pack(pady=15)

# Create a Button widget below the textbox
button = tk.Button(root, text="Generate Image", command=on_button_click, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="flat", width=15, height=2)
button.pack(pady=10)

# Create a Label widget to show internet connection status
connectivity_label = tk.Label(root, text="Checking connection...", anchor="ne", width=15, height=1, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
connectivity_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=5)

# Create a Label widget to show loading animation
loading_label = tk.Label(root, text="", font=("Courier", 24))

# Create a Button widget for downloading the image
download_button = tk.Button(root, text="Download Image", command=download_image, bg="#FF9800", fg="white", font=("Helvetica", 12, "bold"), relief="flat", width=15, height=2)
download_button.pack_forget()  # Hide the download button initially

# Bind the Enter key (Return) to trigger the button click
root.bind('<Return>', on_button_click)

# Run the connectivity check on an interval (every 5 seconds)
update_connectivity_status()

# Initialize the fetched image variable
fetched_image = None

# Run the application
root.mainloop()
