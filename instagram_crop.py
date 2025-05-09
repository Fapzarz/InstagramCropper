import os
import sys
from PIL import Image, ImageTk
from tkinter import Tk, filedialog, Button, Label, StringVar, OptionMenu, Frame, Canvas, PhotoImage, BOTH, TOP, BOTTOM, LEFT, RIGHT, X, Y, HORIZONTAL, VERTICAL, SOLID, messagebox, ttk, IntVar, Checkbutton

class InstagramCropTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Crop Tool")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)
        self.root.minsize(800, 550)  # Set minimum window size
        
        # Presets for Instagram
        self.presets = {
            "Feed (4:5)": {"ratio": (4, 5), "size": (1080, 1350)},
            "Grid Feed (3:4)": {"ratio": (3, 4), "size": (354, 472)},
            "Reels (9:16)": {"ratio": (9, 16), "size": None}
        }
        
        self.selected_preset = StringVar(root)
        self.selected_preset.set("Feed (4:5)")  # default value
        self.selected_preset.trace("w", self.update_preview)  # Update preview when preset changes
        
        # Split wide images option
        self.split_wide_images = IntVar()
        self.split_wide_images.set(0)  # Default: not splitting
        self.split_wide_images.trace("w", self.update_preview)  # Update preview when option changes

        # Number of panels for split
        self.split_panels = IntVar()
        self.split_panels.set(3)  # Default: 3 panels
        self.split_panels.trace("w", self.update_preview)  # Update preview when split panels changes
        
        # Maximum allowed panels based on image width
        self.max_allowed_panels = 2
        
        # Image variables
        self.current_image_path = None
        self.original_image = None
        self.preview_original = None
        self.preview_cropped = None
        self.preview_images = []  # List of cropped preview images (for split view)
        
        # Create UI elements
        self.setup_ui()
        
        # Bind resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Last resize time to avoid excessive UI updates
        self.last_resize_time = 0
        self.resize_delay = 200  # milliseconds
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only process resize events for the main window
        if event.widget == self.root:
            # Get current time
            current_time = self.root.after_idle(lambda: None)
            
            # Cancel previous scheduled update if it exists
            if hasattr(self, 'resize_after_id'):
                self.root.after_cancel(self.resize_after_id)
            
            # Schedule update with delay
            self.resize_after_id = self.root.after(self.resize_delay, self.update_on_resize)
    
    def update_on_resize(self):
        """Update UI after resize"""
        if self.original_image:
            self.update_preview()
    
    def setup_ui(self):
        # Main frame
        main_frame = Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Header with gradient
        header_frame = Frame(main_frame, bg="#4f5bd5", height=60)
        header_frame.pack(fill=X, pady=(0, 10))
        
        header = Label(header_frame, text="Instagram Crop Tool", font=("Helvetica", 18, "bold"), 
                       bg="#4f5bd5", fg="white")
        header.pack(pady=15)
        
        # Content area - split into left (controls) and right (preview) sections
        content_frame = Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=BOTH, expand=True)
        
        # Left side - controls
        controls_frame = Frame(content_frame, bg="#f5f5f5", width=280, padx=15, pady=15, 
                              highlightbackground="#e0e0e0", highlightthickness=1)
        controls_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        controls_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Preset selection with modern styling
        preset_label = Label(controls_frame, text="Instagram Format", font=("Helvetica", 12, "bold"), 
                            bg="#f5f5f5", anchor="w")
        preset_label.pack(fill=X, pady=(0, 5))
        
        preset_style = ttk.Style()
        preset_style.configure('TMenubutton', font=('Helvetica', 10))
        
        preset_menu = ttk.OptionMenu(controls_frame, self.selected_preset, 
                                   self.selected_preset.get(), *self.presets.keys())
        preset_menu.pack(fill=X, pady=(0, 15))
        
        # Info label about selected format
        self.format_info = Label(controls_frame, text="", font=("Helvetica", 10), 
                               bg="#f5f5f5", fg="#555555", anchor="w", justify=LEFT)
        self.format_info.pack(fill=X, pady=(0, 15))
        self.update_format_info()  # Initial update
        
        # Wide image handling options
        wide_image_frame = Frame(controls_frame, bg="#f5f5f5", pady=5)
        wide_image_frame.pack(fill=X)
        
        wide_image_label = Label(wide_image_frame, text="Wide Image Options", font=("Helvetica", 12, "bold"), 
                             bg="#f5f5f5", anchor="w")
        wide_image_label.pack(fill=X, pady=(0, 5))
        
        split_check = Checkbutton(wide_image_frame, text="Split wide images (for carousel)", 
                               variable=self.split_wide_images, 
                               font=("Helvetica", 10),
                               bg="#f5f5f5", anchor="w")
        split_check.pack(fill=X, pady=5)
        
        # Panel count frame and label
        panel_label_frame = Frame(wide_image_frame, bg="#f5f5f5")
        panel_label_frame.pack(fill=X, pady=(0, 5))
        
        panel_label = Label(panel_label_frame, text="Number of panels:", font=("Helvetica", 10), 
                          bg="#f5f5f5", anchor="w")
        panel_label.pack(side=LEFT, padx=(20, 5))
        
        # Radiobutton frame with better layout
        self.panel_radio_frame = Frame(wide_image_frame, bg="#f5f5f5")
        self.panel_radio_frame.pack(fill=X, pady=(0, 5))
        
        # Create radiobuttons for panel count in a grid layout for better fit
        self.panel_radios = []
        panel_values = [2, 3, 4, 5]
        for i, val in enumerate(panel_values):
            rb = ttk.Radiobutton(self.panel_radio_frame, text=str(val), variable=self.split_panels, 
                              value=val, command=self.update_preview)
            rb.grid(row=0, column=i, padx=10, sticky="w")
            self.panel_radio_frame.columnconfigure(i, weight=1)
            self.panel_radios.append(rb)
            
        # Add status info about minimum width for split
        self.split_info = Label(wide_image_frame, 
                            text="",
                            font=("Helvetica", 9), bg="#f5f5f5", fg="#555555", 
                            anchor="w", justify=LEFT)
        self.split_info.pack(fill=X, padx=(20, 0), pady=(0, 5))
        
        # Information about wide images
        wide_info = Label(wide_image_frame, 
                        text="Automatically splits panoramic images\ninto multiple posts for Instagram carousel",
                        font=("Helvetica", 9), bg="#f5f5f5", fg="#555555", 
                        anchor="w", justify=LEFT)
        wide_info.pack(fill=X, padx=(20, 0), pady=(0, 5))
        
        # Separator
        ttk.Separator(controls_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        
        # Buttons with modern styling
        button_style = ttk.Style()
        button_style.configure('TButton', font=('Helvetica', 10))
        
        select_btn = ttk.Button(controls_frame, text="Select Image", command=self.select_image, style='TButton')
        select_btn.pack(fill=X, pady=5)
        
        process_btn = ttk.Button(controls_frame, text="Process Image(s)", command=self.process_images, style='TButton')
        process_btn.pack(fill=X, pady=5)
        
        # Status
        self.status_frame = Frame(controls_frame, bg="#f5f5f5", height=30)
        self.status_frame.pack(fill=X, pady=(15, 0))
        
        self.status_label = Label(self.status_frame, text="Ready to crop images", 
                               font=("Helvetica", 10), bg="#f5f5f5", fg="#555555")
        self.status_label.pack(pady=5)
        
        # Right side - preview
        self.preview_frame = Frame(content_frame, bg="white", padx=15, pady=15,
                           highlightbackground="#e0e0e0", highlightthickness=1)
        self.preview_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        preview_label = Label(self.preview_frame, text="Image Preview", font=("Helvetica", 12, "bold"), bg="white")
        preview_label.pack(pady=(0, 10))
        
        # Preview area - can change between single crop and split view
        self.preview_container = Frame(self.preview_frame, bg="white")
        self.preview_container.pack(fill=BOTH, expand=True)
        
        # Original image preview
        self.setup_standard_preview()
        
        # Footer
        footer_frame = Frame(main_frame, bg="#f0f0f0")
        footer_frame.pack(fill=X, pady=(10, 0))
        
        credits = Label(footer_frame, text="Made with ❤️", font=("Helvetica", 8), bg="#f0f0f0", fg="#888888")
        credits.pack(side=RIGHT)
    
    def setup_standard_preview(self):
        # Clear the preview container
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        # Preview area - split into before and after
        preview_split = Frame(self.preview_container, bg="white")
        preview_split.pack(fill=BOTH, expand=True)
        
        # Original image preview
        original_frame = Frame(preview_split, bg="white", padx=5, pady=5, width=250)
        original_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        Label(original_frame, text="Original", font=("Helvetica", 10, "bold"), bg="white").pack(pady=(0, 5))
        
        self.original_canvas = Canvas(original_frame, bg="#f8f8f8", highlightthickness=1, 
                                   highlightbackground="#e0e0e0")
        self.original_canvas.pack(fill=BOTH, expand=True)
        
        # Separator
        sep_frame = Frame(preview_split, bg="white", width=1)
        sep_frame.pack(side=LEFT, fill=Y, padx=2)
        ttk.Separator(sep_frame, orient=VERTICAL).pack(fill=Y, expand=True)
        
        # Cropped image preview
        cropped_frame = Frame(preview_split, bg="white", padx=5, pady=5, width=250)
        cropped_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        Label(cropped_frame, text="Cropped Preview", font=("Helvetica", 10, "bold"), bg="white").pack(pady=(0, 5))
        
        self.cropped_canvas = Canvas(cropped_frame, bg="#f8f8f8", highlightthickness=1, 
                                  highlightbackground="#e0e0e0")
        self.cropped_canvas.pack(fill=BOTH, expand=True)
        
        # Add weight to properly distribute space
        preview_split.columnconfigure(0, weight=1)
        preview_split.columnconfigure(2, weight=1)
    
    def setup_split_preview(self, num_panels):
        # Clear the preview container
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        # Original image frame
        orig_frame = Frame(self.preview_container, bg="white", height=120)
        orig_frame.pack(fill=X, pady=(0, 10))
        
        Label(orig_frame, text="Original", font=("Helvetica", 10, "bold"), bg="white").pack(pady=(0, 5))
        
        self.original_canvas = Canvas(orig_frame, bg="#f8f8f8", height=100, highlightthickness=1, 
                                   highlightbackground="#e0e0e0")
        self.original_canvas.pack(fill=X)
        
        # Label for split panels
        Label(self.preview_container, text=f"Split Preview ({num_panels} panels for carousel)", 
            font=("Helvetica", 10, "bold"), bg="white").pack(pady=(5, 10))
        
        # Create split preview grid
        split_frame = Frame(self.preview_container, bg="white")
        split_frame.pack(fill=BOTH, expand=True)
        
        # Create canvas for each panel
        self.split_canvases = []
        
        # Calculate grid layout
        if num_panels <= 3:
            cols = num_panels
            rows = 1
        else:
            cols = 3
            rows = (num_panels + 2) // 3  # Ceiling division
        
        # Create frames for each panel
        for i in range(num_panels):
            row = i // cols
            col = i % cols
            
            # Panel frame
            panel_frame = Frame(split_frame, bg="white", padx=3, pady=3)
            panel_frame.grid(row=row, column=col, sticky="nsew")
            
            # Make columns and rows expandable
            split_frame.grid_columnconfigure(col, weight=1)
            split_frame.grid_rowconfigure(row, weight=1)
            
            # Panel number label
            Label(panel_frame, text=f"Panel {i+1}", font=("Helvetica", 9), bg="white").pack(pady=(0, 3))
            
            # Panel canvas
            canvas = Canvas(panel_frame, bg="#f8f8f8", highlightthickness=1, highlightbackground="#e0e0e0")
            canvas.pack(fill=BOTH, expand=True)
            
            self.split_canvases.append(canvas)
    
    def update_format_info(self):
        preset = self.presets[self.selected_preset.get()]
        ratio_text = f"{preset['ratio'][0]}:{preset['ratio'][1]}"
        
        if preset["size"]:
            size_text = f"{preset['size'][0]}×{preset['size'][1]} pixels"
        else:
            size_text = "Custom size"
            
        info_text = f"Aspect ratio: {ratio_text}\nOutput size: {size_text}"
        self.format_info.config(text=info_text)
    
    def update_split_info(self):
        """Update information about minimum width required for splitting"""
        if not self.original_image:
            self.split_info.config(text="")
            return
            
        preset = self.presets[self.selected_preset.get()]
        if not preset["size"]:
            self.split_info.config(text="")
            return
            
        # Get standard width for selected format
        std_width = preset["size"][0]
        
        # Calculate minimum width for each panel count
        min_widths = {}
        for panels in range(2, 6):
            min_widths[panels] = std_width * panels
        
        # Get image width
        img_width = self.original_image.size[0]
        
        # Determine how many panels this image can be split into
        max_panels = 1
        for panels, min_width in min_widths.items():
            if img_width >= min_width:
                max_panels = panels
        
        self.max_allowed_panels = max_panels
        
        # Update UI based on max panels
        if max_panels <= 1:
            # Image not wide enough for any splitting
            info_text = f"This image is not wide enough for splitting."
            info_color = "#CC5555"  # Red
            
            # Disable all radio buttons
            for i, rb in enumerate(self.panel_radios):
                rb.config(state="disabled")
                
            # Disable split checkbox
            if self.split_wide_images.get() == 1:
                self.split_wide_images.set(0)
                
        else:
            # Image can be split into some number of panels
            info_text = f"Image can be split into up to {max_panels} panels."
            info_color = "#555555"
            
            # Enable/disable appropriate radio buttons
            for i, rb in enumerate(self.panel_radios):
                panel_value = i + 2  # Panel values start at 2
                if panel_value <= max_panels:
                    rb.config(state="normal")
                else:
                    rb.config(state="disabled")
                    
            # Ensure selected panels value is valid
            if self.split_panels.get() > max_panels:
                self.split_panels.set(max_panels)
            
        # Update info text
        self.split_info.config(text=info_text, fg=info_color)
    
    def select_image(self):
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.webp"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )
        
        if not filename:
            return
            
        self.current_image_path = filename
        self.load_preview_image(filename)
        self.status_label.config(text=f"Image loaded: {os.path.basename(filename)}")
    
    def load_preview_image(self, image_path):
        try:
            # Open the image
            self.original_image = Image.open(image_path)
            
            # Update split info
            self.update_split_info()
            
            # Update the preview display
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
    
    def update_preview(self, *args):
        if self.original_image is None:
            return
            
        # Update format info when preset changes
        self.update_format_info()
        
        # Update split info
        self.update_split_info()
        
        # Get selected preset
        preset = self.presets[self.selected_preset.get()]
        
        # Check if splitting is enabled and image is eligible
        can_split = (self.split_wide_images.get() == 1 and self.max_allowed_panels >= 2)
        
        if can_split:
            # Get valid panel count
            panel_count = min(self.split_panels.get(), self.max_allowed_panels)
            
            # Setup split preview UI
            self.setup_split_preview(panel_count)
            
            # Show original image in top canvas
            self.display_original_wide_preview(self.original_image, self.original_canvas)
            
            # Generate and show split panels
            split_images = self.split_image_preview(self.original_image, preset, panel_count)
            self.preview_images = []  # Clear previous references
            
            for i, img in enumerate(split_images):
                if i < len(self.split_canvases):
                    self.display_panel_preview(img, self.split_canvases[i], i)
        else:
            # Setup standard preview UI
            self.setup_standard_preview()
            
            # Show original image preview
            self.display_preview_image(self.original_image, self.original_canvas, self.preview_original)
            
            # Show cropped image preview
            cropped_img = self.crop_image_preview(self.original_image, preset)
            self.display_preview_image(cropped_img, self.cropped_canvas, self.preview_cropped)
    
    def should_split_image(self, img, preset):
        """Determine if an image should be split based on its aspect ratio and width"""
        # Check if the format has a standard size
        if not preset["size"]:
            return False
            
        # Get image dimensions
        width, height = img.size
        
        # Get standard width for selected format
        std_width = preset["size"][0]
        
        # Calculate how many standard widths fit into the image
        panels_possible = width // std_width
        
        # Can split if image can fit 2 or more panels
        return panels_possible >= 2
    
    def get_max_possible_panels(self, img, preset):
        """Calculate how many panels the image can be split into"""
        if not preset["size"]:
            return 1
            
        # Get image dimensions
        width, height = img.size
        
        # Get standard width for selected format
        std_width = preset["size"][0]
        
        # Calculate how many standard widths fit into the image
        panels_possible = width // std_width
        
        # Limit to 5 panels maximum
        return min(panels_possible, 5)
    
    def display_original_wide_preview(self, img, canvas):
        """Display the original wide image in a letterbox format"""
        # Clear canvas
        canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width() or 400
        canvas_height = canvas.winfo_height() or 100
        
        # Ensure valid dimensions
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 100
        
        # Calculate scaled dimensions (fit to width)
        img_width, img_height = img.size
        scale_factor = canvas_width / img_width
        new_width = canvas_width
        new_height = int(img_height * scale_factor)
        
        # Adjust height if needed
        if new_height > canvas_height:
            scale_factor = canvas_height / new_height
            new_width = int(new_width * scale_factor)
            new_height = canvas_height
        
        # Resize image for display
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img_resized)
        self.preview_original = photo  # Keep reference
        
        # Display in canvas center
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.create_image(x, y, anchor="nw", image=photo)
    
    def split_image_preview(self, img, preset, num_panels):
        """Split a wide image into multiple panels that follow the target aspect ratio"""
        try:
            # Get image dimensions
            img_width, img_height = img.size
            
            # Get target aspect ratio
            target_ratio = preset["ratio"][0] / preset["ratio"][1]
            
            # Calculate the width of each panel based on height and target ratio
            panel_width = int(img_height * target_ratio)
            
            # Calculate the standard width based on preset
            std_panel_width = panel_width
            if preset["size"]:
                std_panel_width = preset["size"][0] * (img_height / preset["size"][1])
            
            # Determine panel width based on image width
            total_width = img_width
            panel_width = total_width // num_panels
            
            # Adjust panel width to match aspect ratio
            new_height = int(panel_width / target_ratio)
            if new_height < img_height:
                # If calculated height is too small, use target aspect ratio instead
                panel_width = int(img_height * target_ratio)
            
            # Calculate overlap
            total_width_needed = panel_width * num_panels
            
            if total_width_needed <= img_width:
                # No overlap needed - image is wide enough
                overlap = 0
                # Distribute panels evenly across the image
                spacing = (img_width - total_width_needed) // (num_panels + 1)
                start_offset = spacing
            else:
                # Need overlap - calculate how much
                overlap_pixels = total_width_needed - img_width
                overlap_per_panel = overlap_pixels / (num_panels - 1)
                overlap = int(overlap_per_panel)
                start_offset = 0
            
            # Create panels
            panels = []
            for i in range(num_panels):
                # Calculate panel boundaries
                left = start_offset + (i * (panel_width - overlap))
                
                # Ensure we don't go out of bounds
                if left < 0:
                    left = 0
                if left + panel_width > img_width:
                    left = img_width - panel_width
                
                right = min(left + panel_width, img_width)
                
                # Ensure panel has valid dimensions
                if left >= right or right <= left:
                    continue
                
                # Crop the panel
                panel = img.crop((left, 0, right, img_height))
                
                # Validate panel
                if panel.width > 0 and panel.height > 0:
                    panels.append(panel)
            
            return panels
            
        except Exception as e:
            print(f"Error in split_image_preview: {str(e)}")
            # Return empty list in case of error
            return []
    
    def display_panel_preview(self, img, canvas, index):
        """Display a panel image in the split view"""
        # Clear canvas
        canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width() or 150
        canvas_height = canvas.winfo_height() or 150
        
        # Ensure valid dimensions
        if canvas_width <= 1:
            canvas_width = 150
        if canvas_height <= 1:
            canvas_height = 150
        
        # Calculate scaled dimensions
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Resize image for display
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img_resized)
        
        # Store reference to prevent garbage collection
        if len(self.preview_images) <= index:
            self.preview_images.append(photo)
        else:
            self.preview_images[index] = photo
        
        # Display in canvas center
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.create_image(x, y, anchor="nw", image=photo)
    
    def crop_image_preview(self, img, preset):
        # Create a copy of the image for preview
        img_copy = img.copy()
        
        # Get target aspect ratio
        target_ratio = preset["ratio"][0] / preset["ratio"][1]
        
        # Calculate current aspect ratio
        width, height = img_copy.size
        current_ratio = width / height
        
        # Determine crop box
        if current_ratio > target_ratio:
            # Image is wider than target, crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = height
        else:
            # Image is taller than target, crop height
            new_height = int(width / target_ratio)
            left = 0
            top = (height - new_height) // 2
            right = width
            bottom = top + new_height
        
        # Crop the image
        return img_copy.crop((left, top, right, bottom))
    
    def display_preview_image(self, img, canvas, photo_ref):
        # Clear canvas
        canvas.delete("all")
        
        # Get current canvas dimensions
        canvas.update_idletasks()  # Force geometry update
        canvas_width = canvas.winfo_width() 
        canvas_height = canvas.winfo_height()
        
        # Set fallback dimensions if canvas hasn't been properly sized yet
        if canvas_width <= 1:
            canvas_width = 250
        if canvas_height <= 1:
            canvas_height = 250
        
        # Calculate scaled dimensions to fit canvas while maintaining aspect ratio
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = max(int(img_width * ratio), 1)  # Ensure at least 1 pixel
        new_height = max(int(img_height * ratio), 1)  # Ensure at least 1 pixel
        
        # Resize the image for display
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage and keep reference
        photo = ImageTk.PhotoImage(img_resized)
        
        # Store reference to prevent garbage collection
        if canvas == self.original_canvas:
            self.preview_original = photo
        else:
            self.preview_cropped = photo
        
        # Display in canvas at center
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.create_image(x, y, anchor="nw", image=photo)
    
    def process_images(self):
        if not self.current_image_path:
            messagebox.showinfo("Select Image", "Please select an image first")
            return
            
        # Ask if user wants to process the current image or select multiple images
        response = messagebox.askyesno("Process Images", 
                                      "Do you want to process the current image?\n\n"
                                      "Click 'Yes' to process the current image.\n"
                                      "Click 'No' to select multiple images.")
        
        if response:
            # Process current image
            filenames = [self.current_image_path]
        else:
            # Select multiple images
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.webp"),
                ("All files", "*.*")
            ]
            
            filenames = filedialog.askopenfilenames(
                title="Select Images",
                filetypes=filetypes
            )
            
            if not filenames:
                return
        
        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            self.status_label.config(text="Operation cancelled")
            return
            
        # Print debug information
        print(f"Output directory: {output_dir}")
        print(f"Files to process: {filenames}")
            
        # Verify output directory exists and is writable
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created directory: {output_dir}")
            except Exception as e:
                error_msg = f"Cannot create output directory: {str(e)}"
                print(error_msg)
                messagebox.showerror("Error", error_msg)
                return
                
        if not os.access(output_dir, os.W_OK):
            error_msg = f"Cannot write to the output directory: {output_dir}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            return
            
        preset = self.presets[self.selected_preset.get()]
        print(f"Using preset: {self.selected_preset.get()}, ratio: {preset['ratio']}, size: {preset['size']}")
        
        # Progress bar setup
        progress_window = Tk()
        progress_window.title("Processing Images")
        progress_window.geometry("300x150")
        progress_window.configure(bg="#f0f0f0")
        
        Label(progress_window, text="Processing images...", font=("Helvetica", 10), bg="#f0f0f0").pack(pady=(20, 10))
        
        progress = ttk.Progressbar(progress_window, orient=HORIZONTAL, length=250, mode='determinate')
        progress.pack(pady=10, padx=20)
        
        status_text = StringVar()
        status_text.set(f"Processing 0/{len(filenames)}")
        status_label = Label(progress_window, textvariable=status_text, font=("Helvetica", 9), bg="#f0f0f0")
        status_label.pack(pady=10)
        
        progress_window.update()
        
        # Process images
        processed = 0
        failed = 0
        total_images = 0  # Total including split panels
        progress["maximum"] = len(filenames)
        
        for i, filename in enumerate(filenames):
            try:
                print(f"Processing file: {filename}")
                # Check if we should split the image
                if self.split_wide_images.get() == 1:
                    print("Split mode enabled")
                    img = Image.open(filename)
                    max_panels = self.get_max_possible_panels(img, preset)
                    print(f"Max possible panels: {max_panels}")
                    
                    if max_panels >= 2 and self.split_panels.get() <= max_panels:
                        # Process as split image
                        num_panels = min(self.split_panels.get(), max_panels)
                        print(f"Splitting into {num_panels} panels")
                        output_paths = self.process_split_image(filename, output_dir, preset, num_panels)
                        print(f"Split output paths: {output_paths}")
                        if output_paths and len(output_paths) > 0:
                            processed += 1
                            total_images += len(output_paths)
                        else:
                            print("No output paths returned from process_split_image")
                            failed += 1
                    else:
                        # Process as normal image
                        print("Image not wide enough for splitting, processing as normal")
                        output_path = self.crop_image(filename, output_dir, preset)
                        print(f"Normal output path: {output_path}")
                        if output_path:
                            processed += 1
                            total_images += 1
                        else:
                            print("No output path returned from crop_image")
                            failed += 1
                else:
                    # Process as normal image
                    print("Normal crop mode")
                    output_path = self.crop_image(filename, output_dir, preset)
                    print(f"Output path: {output_path}")
                    if output_path:
                        processed += 1
                        total_images += 1
                    else:
                        print("No output path returned from crop_image")
                        failed += 1
            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                print(error_msg)
                failed += 1
                
            progress["value"] = i + 1
            status_text.set(f"Processing {i+1}/{len(filenames)}")
            progress_window.update()
        
        progress_window.destroy()
        
        # Show completion message
        completion_msg = ""
        if failed > 0:
            completion_msg = f"Successfully processed {processed} of {len(filenames)} images.\n{failed} images could not be processed.\nTotal output images: {total_images}"
        else:
            completion_msg = f"Successfully processed {processed} images.\nTotal output images: {total_images}"
            
        print(completion_msg)
        messagebox.showinfo("Processing Complete", completion_msg)
        
        # Open output directory
        try:
            if processed > 0:
                if os.name == 'nt':  # Windows
                    os.startfile(output_dir)
                elif os.name == 'posix':  # macOS/Linux
                    import subprocess
                    subprocess.Popen(['xdg-open', output_dir])
        except Exception as e:
            print(f"Could not open output directory: {str(e)}")
        
        self.status_label.config(text=f"Successfully processed {processed} images")
    
    def crop_image(self, image_path, output_dir, preset):
        try:
            print(f"Starting crop_image for {image_path}")
            # Open the image
            img = Image.open(image_path)
            print(f"Image opened: {img.size}")
            
            # Get target aspect ratio
            target_ratio = preset["ratio"][0] / preset["ratio"][1]
            
            # Calculate current aspect ratio
            width, height = img.size
            current_ratio = width / height
            print(f"Target ratio: {target_ratio}, Current ratio: {current_ratio}")
            
            # Determine crop box
            if current_ratio > target_ratio:
                # Image is wider than target, crop width
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = height
            else:
                # Image is taller than target, crop height
                new_height = int(width / target_ratio)
                left = 0
                top = (height - new_height) // 2
                right = width
                bottom = top + new_height
                
            print(f"Crop box: ({left}, {top}, {right}, {bottom})")
            
            # Validate crop box
            if left >= right or top >= bottom:
                # Invalid crop dimensions
                error_msg = f"Invalid crop dimensions: ({left}, {top}, {right}, {bottom})"
                print(error_msg)
                messagebox.showerror("Error", error_msg)
                return None
            
            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))
            print(f"Cropped image: {cropped_img.size}")
            
            # Validate cropped image
            if cropped_img.width <= 0 or cropped_img.height <= 0:
                error_msg = f"Invalid cropped dimensions: {cropped_img.width}x{cropped_img.height}"
                print(error_msg)
                messagebox.showerror("Error", error_msg)
                return None
            
            # Resize if size is specified
            if preset["size"]:
                print(f"Resizing to {preset['size']}")
                cropped_img = cropped_img.resize(preset["size"], Image.LANCZOS)
            
            # Save the cropped image
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            format_name = self.selected_preset.get().replace(" ", "").replace("(", "").replace(")", "").replace(":", "-")
            new_filename = f"{name}_{format_name}{ext}"
            output_path = os.path.join(output_dir, new_filename)
            print(f"Output path: {output_path}")
            
            # Ensure format is correct based on extension
            save_format = ext.lower().replace('.', '')
            if save_format == 'jpg':
                save_format = 'JPEG'
            elif save_format == 'jpeg':
                save_format = 'JPEG'
            
            print(f"Saving with format: {save_format}")
            
            # Save with quality parameter for JPEG
            if save_format.upper() == 'JPEG':
                cropped_img.save(output_path, format=save_format.upper(), quality=95)
            else:
                # For non-JPEG formats
                if save_format.upper() in ['PNG', 'GIF', 'BMP', 'WEBP']:
                    cropped_img.save(output_path, format=save_format.upper())
                else:
                    # Default to PNG if format not recognized
                    print(f"Unrecognized format: {save_format}, defaulting to PNG")
                    new_output_path = os.path.splitext(output_path)[0] + ".png"
                    cropped_img.save(new_output_path, format="PNG")
                    output_path = new_output_path
            
            # Verify the file was created and has content
            if not os.path.exists(output_path):
                error_msg = f"Error: Output file was not created: {output_path}"
                print(error_msg)
                messagebox.showerror("Error", error_msg)
                return None
                
            if os.path.getsize(output_path) == 0:
                error_msg = f"Error: Output file is empty: {output_path}"
                print(error_msg)
                messagebox.showerror("Error", error_msg)
                # Try saving again with a different method
                try:
                    print("Trying alternative save method...")
                    # Convert to RGB if needed (to avoid transparency issues)
                    if cropped_img.mode in ['RGBA', 'LA']:
                        print(f"Converting from {cropped_img.mode} to RGB")
                        rgb_img = Image.new("RGB", cropped_img.size, (255, 255, 255))
                        rgb_img.paste(cropped_img, mask=cropped_img.split()[3] if cropped_img.mode == 'RGBA' else None)
                        cropped_img = rgb_img
                    
                    # Try with a different name and format
                    backup_path = os.path.join(output_dir, f"{name}_backup.jpg")
                    print(f"Saving backup to: {backup_path}")
                    cropped_img.save(backup_path, format="JPEG", quality=95)
                    return backup_path
                except Exception as e:
                    print(f"Alternative save failed: {e}")
                    return None
                
            print(f"File saved successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
            
        except Exception as e:
            error_msg = f"Error processing {image_path}: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
            return None
            
    def process_split_image(self, image_path, output_dir, preset, num_panels):
        """Process a wide image by splitting it into multiple panels"""
        try:
            print(f"Starting process_split_image for {image_path}")
            # Open the image
            img = Image.open(image_path)
            print(f"Image opened: {img.size}")
            
            # Check if image is wide enough for requested number of panels
            max_panels = self.get_max_possible_panels(img, preset)
            if num_panels > max_panels:
                # Adjust to maximum possible
                num_panels = max_panels
                print(f"Adjusted to maximum possible panels: {num_panels}")
            
            # Split the image into panels
            panels = self.split_image_preview(img, preset, num_panels)
            print(f"Split into {len(panels)} panels")
            
            # Get base filename
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            format_name = self.selected_preset.get().replace(" ", "").replace("(", "").replace(")", "").replace(":", "-")
            
            # Save each panel
            output_paths = []
            
            for i, panel in enumerate(panels):
                try:
                    print(f"Processing panel {i+1} size: {panel.size}")
                    # Validate the panel image
                    if panel.width <= 0 or panel.height <= 0:
                        print(f"Invalid panel dimensions: {panel.width}x{panel.height}")
                        continue
                        
                    # Resize if size is specified
                    if preset["size"]:
                        print(f"Resizing panel to {preset['size']}")
                        panel = panel.resize(preset["size"], Image.LANCZOS)
                    
                    # Save the panel
                    new_filename = f"{name}_{format_name}_panel{i+1}of{num_panels}{ext}"
                    output_path = os.path.join(output_dir, new_filename)
                    print(f"Panel output path: {output_path}")
                    
                    # Ensure format is correct based on extension
                    save_format = ext.lower().replace('.', '')
                    if save_format == 'jpg':
                        save_format = 'JPEG'
                    elif save_format == 'jpeg':
                        save_format = 'JPEG'
                    
                    print(f"Saving panel with format: {save_format}")
                    
                    # Save with quality parameter for JPEG
                    if save_format.upper() == 'JPEG':
                        panel.save(output_path, format=save_format.upper(), quality=95)
                    else:
                        # For non-JPEG formats
                        if save_format.upper() in ['PNG', 'GIF', 'BMP', 'WEBP']:
                            panel.save(output_path, format=save_format.upper())
                        else:
                            # Default to PNG if format not recognized
                            print(f"Unrecognized format: {save_format}, defaulting to PNG")
                            new_output_path = os.path.splitext(output_path)[0] + ".png"
                            panel.save(new_output_path, format="PNG")
                            output_path = new_output_path
                    
                    # Verify the file was created and has content
                    if not os.path.exists(output_path):
                        print(f"Error: Panel file was not created: {output_path}")
                        continue
                        
                    if os.path.getsize(output_path) == 0:
                        print(f"Error: Panel file is empty: {output_path}")
                        # Try saving again with a different method
                        try:
                            print("Trying alternative save method for panel...")
                            # Convert to RGB if needed
                            if panel.mode in ['RGBA', 'LA']:
                                print(f"Converting from {panel.mode} to RGB")
                                rgb_img = Image.new("RGB", panel.size, (255, 255, 255))
                                rgb_img.paste(panel, mask=panel.split()[3] if panel.mode == 'RGBA' else None)
                                panel = rgb_img
                            
                            # Try with a different name and format
                            backup_path = os.path.join(output_dir, f"{name}_panel{i+1}_backup.jpg")
                            print(f"Saving backup to: {backup_path}")
                            panel.save(backup_path, format="JPEG", quality=95)
                            output_paths.append(backup_path)
                        except Exception as e:
                            print(f"Alternative panel save failed: {e}")
                    else:
                        print(f"Panel saved successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
                        output_paths.append(output_path)
                        
                except Exception as e:
                    print(f"Error saving panel {i+1}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            print(f"Total panels saved: {len(output_paths)}")
            return output_paths
            
        except Exception as e:
            error_msg = f"Error in process_split_image: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Could not process split image: {str(e)}")
            return []

def main():
    root = Tk()
    app = InstagramCropTool(root)
    root.mainloop()

if __name__ == "__main__":
    main() 