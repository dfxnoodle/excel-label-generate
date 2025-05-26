import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import traceback
import json # Added for JSON editing
# from io import BytesIO # Appears unused, commented out.

# Now attempt to import the necessary functions from simple_labels
try:
    from simple_labels import load_data_from_excel, generate_labels, load_config
except ImportError:
    # This message can be improved or logged if necessary
    print("Critical Error: Could not import from simple_labels. Ensure it's in the Python path.")
    sys.exit(1)

# Mappings will now be loaded from config
# CATEGORY_MAP = { ... } # REMOVED
# CODE_FROM_DESC = {v: k for k, v in CATEGORY_MAP.items()} # REMOVED

# STATUS_MAP = { ... } # REMOVED
# STATUS_CODE_FROM_DESC = {v: k, for k, v in STATUS_MAP.items()} # REMOVED

# MAIL_ZONE_MAP = { ... } # REMOVED
# MAIL_ZONE_CODE_FROM_DESC = {v: k, for k, v in MAIL_ZONE_MAP.items()} # REMOVED

class LabelApp:
    def __init__(self, master):
        self.master = master
        master.title("Distribution List Label Generator")

        # Default paths (can be improved to be more dynamic or user-configurable)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.output_dir = os.path.join(self.base_dir, "output")
        self.config_dir = os.path.join(self.base_dir, "config")
        self.icon_path = os.path.join(self.base_dir, "icon")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # master.iconbitmap(os.path.join(self.icon_path, "icon.ico"))

        # Load initial configuration, which now includes maps
        self.config_file_path_var = tk.StringVar()
        self.config_file_path_var.set(os.path.join(self.config_dir, "label_config.json"))
        self.app_config = load_config(self.config_file_path_var.get())

        # Dynamically create reverse maps from loaded config
        self.CATEGORY_MAP = self.app_config.get("category_map", {})
        self.CODE_FROM_DESC = {v: k for k, v in self.CATEGORY_MAP.items()}
        
        self.STATUS_MAP = self.app_config.get("status_map", {})
        self.STATUS_CODE_FROM_DESC = {v: k for k, v in self.STATUS_MAP.items()}

        self.MAIL_ZONE_MAP = self.app_config.get("mail_zone_map", {})
        self.MAIL_ZONE_CODE_FROM_DESC = {v: k for k, v in self.MAIL_ZONE_MAP.items()}
        
        self.publication_options_map = self.app_config.get("publication_options_map", {})
        self.all_fields_info = self.app_config.get("all_fields_info", [])

        # --- Main Layout PanedWindow ---
        self.main_paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        self.main_paned_window.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # --- Left Controls Frame ---
        self.left_controls_frame = ttk.Frame(self.main_paned_window, padding="5 5 5 5")
        self.main_paned_window.add(self.left_controls_frame, weight=1) # Allow this pane to resize

        # --- Input File ---
        tk.Label(self.left_controls_frame, text="Excel File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.excel_file_path_var = tk.StringVar()
        self.excel_file_entry = tk.Entry(self.left_controls_frame, textvariable=self.excel_file_path_var, width=50)
        self.excel_file_entry.grid(row=0, column=1, padx=5, pady=5)
        self.browse_button = tk.Button(self.left_controls_frame, text="Browse...", command=self.browse_excel_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        # Set default excel file
        self.excel_file_path_var.set(os.path.join(self.data_dir, "SourceExcel.xlsx"))

        # --- Category Filter ---
        tk.Label(self.left_controls_frame, text="Include Category Filter:").grid(row=1, column=0, sticky="w", padx=5, pady=5) # Renamed label
        self.category_filter_var = tk.StringVar()
        category_options = ["(All Categories)"] + list(self.CATEGORY_MAP.values())
        self.category_filter_combo = ttk.Combobox(self.left_controls_frame, textvariable=self.category_filter_var, values=category_options, width=47, state="readonly")
        self.category_filter_combo.grid(row=1, column=1, padx=5, pady=5)
        self.category_filter_combo.set("(All Categories)") # Default selection

        # --- Exclude Category Filter ---
        tk.Label(self.left_controls_frame, text="Exclude Category Filter:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.category_exclude_filter_var = tk.StringVar()
        # Options are same as include, but with a different default/meaning
        self.category_exclude_filter_combo = ttk.Combobox(self.left_controls_frame, textvariable=self.category_exclude_filter_var, values=category_options, width=47, state="readonly") # category_options is already defined
        self.category_exclude_filter_combo.grid(row=2, column=1, padx=5, pady=5)
        self.category_exclude_filter_combo.set("(No Exclusions)") # Default selection, can use one of the category_options like "(All Categories)" if it makes sense or add a specific "(No Exclusions)" if not present

        # --- Status Filter ---
        tk.Label(self.left_controls_frame, text="Include Status Filter:").grid(row=3, column=0, sticky="w", padx=5, pady=5) # Renamed label
        self.status_filter_var = tk.StringVar()
        status_options = ["(All Statuses)"] + list(self.STATUS_MAP.values())
        self.status_filter_combo = ttk.Combobox(self.left_controls_frame, textvariable=self.status_filter_var, values=status_options, width=47, state="readonly")
        self.status_filter_combo.grid(row=3, column=1, padx=5, pady=5)
        self.status_filter_combo.set("(All Statuses)") # Default selection

        # --- Exclude Status Filter ---
        tk.Label(self.left_controls_frame, text="Exclude Status Filter:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.status_exclude_filter_var = tk.StringVar()
        # Options are same as include, but with a different default
        self.status_exclude_filter_combo = ttk.Combobox(self.left_controls_frame, textvariable=self.status_exclude_filter_var, values=status_options, width=47, state="readonly")
        self.status_exclude_filter_combo.grid(row=4, column=1, padx=5, pady=5)
        self.status_exclude_filter_combo.set("(No Exclusions)") # Default selection

        # --- Mail Zone Filter ---
        tk.Label(self.left_controls_frame, text="Mail Zone Filter:").grid(row=5, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        self.mail_zone_filter_var = tk.StringVar()
        mail_zone_options = ["(All Mail Zones)"] + list(self.MAIL_ZONE_MAP.values())
        self.mail_zone_filter_combo = ttk.Combobox(self.left_controls_frame, textvariable=self.mail_zone_filter_var, values=mail_zone_options, width=47, state="readonly")
        self.mail_zone_filter_combo.grid(row=5, column=1, padx=5, pady=5) # Adjusted row
        self.mail_zone_filter_combo.set("(All Mail Zones)")
        
        # --- Publication Filter ---
        tk.Label(self.left_controls_frame, text="Publication Filter:").grid(row=6, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        self.publication_filter_var = tk.StringVar()
        # Ensure "(All Publications)" is included in the options
        publication_display_options = ["(All Publications)"] + list(self.publication_options_map.keys())
        self.publication_filter_combo = ttk.Combobox(self.left_controls_frame, textvariable=self.publication_filter_var, values=publication_display_options, width=47, state="readonly")
        self.publication_filter_combo.grid(row=6, column=1, padx=5, pady=5) # Adjusted row
        self.publication_filter_combo.set("(All Publications)") # Default selection
        
        # --- Output File Path ---
        tk.Label(self.left_controls_frame, text="Output File Path:").grid(row=7, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        self.output_filename_var = tk.StringVar()
        self.output_filename_entry = tk.Entry(self.left_controls_frame, textvariable=self.output_filename_var, width=50)
        self.output_filename_entry.grid(row=7, column=1, padx=5, pady=5) # Adjusted row
        self.browse_output_button = tk.Button(self.left_controls_frame, text="Browse...", command=self.browse_output_file)
        self.browse_output_button.grid(row=7, column=2, padx=5, pady=5) # Adjusted row
        self.output_filename_var.set(os.path.join(self.output_dir, "labels.pdf")) # Default full output path
        
        # --- Config File (optional) ---
        tk.Label(self.left_controls_frame, text="Config File (optional):").grid(row=8, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        # self.config_file_path_var is already defined and set earlier
        self.config_file_entry = tk.Entry(self.left_controls_frame, textvariable=self.config_file_path_var, width=50)
        self.config_file_entry.grid(row=8, column=1, padx=5, pady=5) # Adjusted row
        self.browse_config_button = tk.Button(self.left_controls_frame, text="Browse...", command=self.browse_config_file)
        self.browse_config_button.grid(row=8, column=2, padx=5, pady=5) # Adjusted row
        self.config_file_path_var.set(os.path.join(self.config_dir, "label_config.json"))        
        
        # --- Bulletin Text ---
        tk.Label(self.left_controls_frame, text="Issue Text (optional):").grid(row=9, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        self.bulletin_text_var = tk.StringVar()
        self.bulletin_text_entry = tk.Entry(self.left_controls_frame, textvariable=self.bulletin_text_var, width=50)
        self.bulletin_text_entry.grid(row=9, column=1, padx=5, pady=5) # Adjusted row

        # --- Bulletin Number Text ---
        tk.Label(self.left_controls_frame, text="Issue Number (optional):").grid(row=10, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        self.bulletin_number_text_var = tk.StringVar()
        self.bulletin_number_text_entry = tk.Entry(self.left_controls_frame, textvariable=self.bulletin_number_text_var, width=50)
        self.bulletin_number_text_entry.grid(row=10, column=1, padx=5, pady=5) # Adjusted row
        
        # --- Custom Right Panel Text ---
        tk.Label(self.left_controls_frame, text="Right Panel Text (max 3 chars):").grid(row=11, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        self.custom_right_panel_text_var = tk.StringVar()
        self.custom_right_panel_text_entry = tk.Entry(self.left_controls_frame, textvariable=self.custom_right_panel_text_var, width=50)
        self.custom_right_panel_text_entry.grid(row=11, column=1, padx=5, pady=5) # Adjusted row
        self.custom_right_panel_text_var.trace_add("write", self.validate_custom_right_panel_text)
        
        # --- Field Selection ---
        # self.all_fields_info is now loaded from config
        self.field_vars = {}

        field_selection_frame = ttk.Frame(self.left_controls_frame, padding="5 5 5 5")
        field_selection_frame.grid(row=12, column=0, columnspan=3, sticky="ew", padx=5, pady=5) # Adjusted row

        recipient_fields_frame = ttk.Labelframe(field_selection_frame, text="Recipient Fields for Preview")
        recipient_fields_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        address_fields_frame = ttk.Labelframe(field_selection_frame, text="Address Fields for Preview")
        address_fields_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        for field_info in self.all_fields_info:
            key = field_info["key"]
            label = field_info["label"]
            default_state = field_info["default"]
            group = field_info["group"]

            var = tk.IntVar(value=default_state)
            self.field_vars[key] = var
            
            parent_frame = recipient_fields_frame if group == "recipient" else address_fields_frame
            cb = ttk.Checkbutton(parent_frame, text=label, variable=var, command=self.draw_placeholder_on_canvas) # Auto-update preview
            cb.pack(anchor=tk.W, padx=5)        
        # --- Generate Button ---
        self.generate_button = tk.Button(self.left_controls_frame, text="Generate Labels", command=self.generate)
        self.generate_button.grid(row=13, column=0, columnspan=3, pady=10) # Adjusted row

        # --- Status Label ---
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.left_controls_frame, textvariable=self.status_var)
        self.status_label.grid(row=14, column=0, columnspan=3, sticky="w", padx=5, pady=2) # Adjusted row

        # --- Placeholder Preview Button ---
        self.placeholder_preview_button = tk.Button(self.left_controls_frame, text="Show/Update Preview", command=self.draw_placeholder_on_canvas)
        self.placeholder_preview_button.grid(row=15, column=0, columnspan=3, pady=2) # Adjusted row
        
        # --- Preview Canvas ---
        # Approx. 95mm x 30mm at 96 DPI (1mm ~ 3.78px)
        # Width: 95 * 3.78 = 359.1 -> 360
        # Height: 30 * 3.78 = 113.4 -> 114
        # Add some padding to the canvas itself
        self.preview_canvas_width_px = 370
        self.preview_canvas_height_px = 125
        self.preview_canvas = tk.Canvas(self.left_controls_frame, width=self.preview_canvas_width_px, height=self.preview_canvas_height_px, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.preview_canvas.grid(row=16, column=0, columnspan=3, pady=10) # Adjusted row

        # --- JSON Configuration Editor (Right Pane) ---
        self.config_editor_frame = ttk.Labelframe(self.main_paned_window, text="Configuration Editor", padding="5 5 5 5")
        self.main_paned_window.add(self.config_editor_frame, weight=1) # Allow this pane to resize
        
        # master.grid_rowconfigure(15, weight=1) # Removed, handled by PanedWindow and internal frame config

        self.config_text_area = tk.Text(self.config_editor_frame, wrap=tk.WORD, height=15, undo=True) # Height is now more flexible
        self.config_text_scroll_y = ttk.Scrollbar(self.config_editor_frame, orient=tk.VERTICAL, command=self.config_text_area.yview)
        self.config_text_scroll_x = ttk.Scrollbar(self.config_editor_frame, orient=tk.HORIZONTAL, command=self.config_text_area.xview)
        self.config_text_area.configure(yscrollcommand=self.config_text_scroll_y.set, xscrollcommand=self.config_text_scroll_x.set)
        
        self.config_text_area.grid(row=0, column=0, sticky="nsew")
        self.config_text_scroll_y.grid(row=0, column=1, sticky="ns")
        self.config_text_scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.config_editor_frame.grid_columnconfigure(0, weight=1) # Text area column
        self.config_editor_frame.grid_rowconfigure(0, weight=1)    # Text area row

        config_editor_buttons_frame = ttk.Frame(self.config_editor_frame)
        config_editor_buttons_frame.grid(row=2, column=0, sticky="ew", pady=(5,0)) # Buttons below text area

        self.save_config_button = ttk.Button(config_editor_buttons_frame, text="Save Changes to Config File", command=self.save_config_from_editor)
        self.save_config_button.pack(side=tk.LEFT, padx=5)

        self.reload_config_button = ttk.Button(config_editor_buttons_frame, text="Reload Config from File", command=self.reload_config_from_file_button_action)
        self.reload_config_button.pack(side=tk.LEFT, padx=5)
        
        self.load_defaults_from_config() 
        # master.grid_columnconfigure(1, weight=1) # Removed, handled by left_controls_frame config

    def validate_custom_right_panel_text(self, *args):
        text = self.custom_right_panel_text_var.get()
        if len(text) > 3:
            self.custom_right_panel_text_var.set(text[:3])

    def load_defaults_from_config(self):
        config_file = self.config_file_path_var.get()
        self.app_config = load_config(config_file if os.path.exists(config_file) else None)
        
        # Update maps and comboboxes if config changed
        self.CATEGORY_MAP = self.app_config.get("category_map", {})
        self.CODE_FROM_DESC = {v: k for k, v in self.CATEGORY_MAP.items()}
        self.category_filter_combo['values'] = ["(All Categories)"] + list(self.CATEGORY_MAP.values())
        self.category_exclude_filter_combo['values'] = ["(No Exclusions)"] + list(self.CATEGORY_MAP.values()) # Update exclude filter options
        # Potentially reset selection if current is no longer valid, or try to preserve
        current_cat_filter_selection = self.category_filter_var.get()
        if current_cat_filter_selection not in self.category_filter_combo['values']:
            self.category_filter_var.set("(All Categories)")

        current_cat_exclude_filter_selection = self.category_exclude_filter_var.get()
        if current_cat_exclude_filter_selection not in self.category_exclude_filter_combo['values']:
            self.category_exclude_filter_var.set("(No Exclusions)")
        
        selected_category_exclude_description = self.category_exclude_filter_var.get()
        category_exclude_code = None
        if selected_category_exclude_description and selected_category_exclude_description != "(No Exclusions)":
            # Assuming CODE_FROM_DESC can be used for exclusion as well
            category_exclude_code = self.CODE_FROM_DESC.get(selected_category_exclude_description)
        
        selected_status_description = self.status_filter_var.get()
        status_code = None
        if selected_status_description and selected_status_description != "(All Statuses)":
            status_code = self.STATUS_CODE_FROM_DESC.get(selected_status_description)

        selected_status_exclude_description = self.status_exclude_filter_var.get()
        status_exclude_code = None
        if selected_status_exclude_description and selected_status_exclude_description != "(No Exclusions)":
            status_exclude_code = self.STATUS_CODE_FROM_DESC.get(selected_status_exclude_description)

        self.MAIL_ZONE_MAP = self.app_config.get("mail_zone_map", {})
        self.MAIL_ZONE_CODE_FROM_DESC = {v: k for k, v in self.MAIL_ZONE_MAP.items()}
        self.mail_zone_filter_combo['values'] = ["(All Mail Zones)"] + list(self.MAIL_ZONE_MAP.values())
        
        self.publication_options_map = self.app_config.get("publication_options_map", {})
        # Ensure "(All Publications)" is included when updating options
        self.publication_filter_combo['values'] = ["(All Publications)"] + list(self.publication_options_map.keys())
        # Attempt to preserve selection if still valid, otherwise default
        current_pub_filter_selection = self.publication_filter_var.get()
        if current_pub_filter_selection not in self.publication_filter_combo['values']:
            self.publication_filter_var.set("(All Publications)")


        self.all_fields_info = self.app_config.get("all_fields_info", [])
        # Re-populate field checkboxes if necessary, or assume they don\'t change structure often
        # For simplicity, not re-creating checkboxes here, but a full implementation might.

        self.bulletin_text_var.set(self.app_config.get("bulletin_text", ""))
        self.bulletin_number_text_var.set(self.app_config.get("bulletin_number_text", ""))
        self.custom_right_panel_text_var.set(self.app_config.get("custom_right_panel_text", "")) # Default to empty
        
        self.populate_config_editor() # Populate the editor after loading config

    def browse_excel_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.data_dir,
            title="Select Excel File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if file_path:
            self.excel_file_path_var.set(file_path)
            # REMOVED: self.preview_first_label() 

    def browse_config_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.config_dir,
            title="Select JSON Config File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if file_path:
            self.config_file_path_var.set(file_path)
            self.load_defaults_from_config() # Reload config and update editor

    def browse_output_file(self):
        # Suggest a filename and default to the output directory
        initial_file = os.path.basename(self.output_filename_var.get() or "labels.pdf")
        file_path = filedialog.asksaveasfilename(
            initialdir=self.output_dir,
            initialfile=initial_file,
            title="Save Output PDF As...",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
            defaultextension=".pdf"
        )
        if file_path:
            # asksaveasfilename already appends .pdf if defaultextension is used and type is selected
            self.output_filename_var.set(file_path)

    def get_current_config_for_generation(self):
        # config_file_path is now self.config_file_path_var.get().strip()
        # current_config is self.app_config, potentially overridden by GUI elements
        
        # Start with a copy of the currently loaded app_config
        current_config_overrides = self.app_config.copy()

        # Add selected fields to the config overrides
        selected_field_keys = [key for key, var in self.field_vars.items() if var.get() == 1]
        current_config_overrides["selected_fields_for_label"] = selected_field_keys

        bulletin_text_gui = self.bulletin_text_var.get().strip()
        if bulletin_text_gui:
            current_config_overrides["bulletin_text"] = bulletin_text_gui
        
        bulletin_number_text_gui = self.bulletin_number_text_var.get().strip()
        if bulletin_number_text_gui:
            current_config_overrides["bulletin_number_text"] = bulletin_number_text_gui
        
        custom_right_panel_text_gui = self.custom_right_panel_text_var.get().strip()
        # Always use the value from the GUI field.
        # If the user cleared it, it will be an empty string.
        # If it was loaded from config (or defaulted to "E" on initial load) and not changed, that value will be used.
        current_config_overrides["custom_right_panel_text"] = custom_right_panel_text_gui

        selected_publication_display_name = self.publication_filter_var.get()
        display_publication_codes_on_label = None # For text on label

        if selected_publication_display_name and selected_publication_display_name != "(All Publications)":
            publication_config_entry = self.publication_options_map.get(selected_publication_display_name)
            if publication_config_entry: # Check if the key exists and entry is not None
                display_publication_codes_on_label = publication_config_entry.get("label_codes")
        
        current_config_overrides["display_publication_codes_on_label"] = display_publication_codes_on_label

        # The config file path itself is needed by generate_labels if it were to reload, 
        # but we are passing temp_config_overrides which is a fully resolved config dictionary.
        # So, we can pass the path, or None if generate_labels should not try to reload it.
        # For consistency, let\'s ensure generate_labels uses the passed dictionary primarily.
        return current_config_overrides, self.config_file_path_var.get().strip()

    def mm_to_px(self, mm_val, dpi=96):
        return int(mm_val * (dpi / 25.4))

    def populate_config_editor(self):
        self.config_text_area.delete("1.0", tk.END) # Clear existing content
        config_file_path = self.config_file_path_var.get()
        if config_file_path and os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.config_text_area.insert("1.0", content)
            except Exception as e:
                self.config_text_area.insert("1.0", f"Error loading config: {e}")
                messagebox.showerror("Config Load Error", f"Could not load config file content into editor: {e}")
        else:
            self.config_text_area.insert("1.0", "{}") # Default to empty JSON if no file
            # Optionally inform user or log this state

    def save_config_from_editor(self):
        config_file_path = self.config_file_path_var.get()
        if not config_file_path:
            messagebox.showerror("Save Error", "No configuration file path is set.")
            return

        content_to_save = self.config_text_area.get("1.0", tk.END).strip()
        
        try:
            # Validate JSON
            json.loads(content_to_save) 
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON: {e}")
            return
        
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write(content_to_save)
            messagebox.showinfo("Success", "Configuration saved successfully.")
            self.load_defaults_from_config() # Reload to apply changes and refresh UI
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save configuration: {e}")

    def reload_config_from_file_button_action(self):
        # This effectively re-runs the logic that loads config and populates the editor
        # It will discard any unsaved changes in the text area.
        if messagebox.askokcancel("Reload Config", "Reload configuration from file? Any unsaved changes in the editor will be lost."):
            self.load_defaults_from_config()
            messagebox.showinfo("Reloaded", "Configuration reloaded from file.")
            
    def draw_placeholder_on_canvas(self):        
        self.preview_canvas.delete("all") # Clear previous drawing
        
        # Get current config for fonts and other settings
        # Use a minimal version of get_current_config_for_generation or load directly
        # For simplicity, let's assume default font sizes for preview if not easily available
        # Or, better, load the config to get font details
        config_path = self.config_file_path_var.get()
        current_config = load_config(config_path if os.path.exists(config_path) else None)

        # Override with GUI inputs for bulletin text for preview
        bulletin_text_preview = self.bulletin_text_var.get().strip() or current_config.get("bulletin_text", "Bulletin")
        bulletin_number_preview = self.bulletin_number_text_var.get().strip() or current_config.get("bulletin_number_text", "No.X-YYYY")
        custom_right_panel_text_preview = self.custom_right_panel_text_var.get().strip() or current_config.get("custom_right_panel_text", "E")


        # Label dimensions in mm (approximate, for preview)
        label_width_mm = 95
        label_height_mm = 30
        
        # Convert to pixels for canvas drawing
        label_width_px = self.mm_to_px(label_width_mm)
        label_height_px = self.mm_to_px(label_height_mm)
        
        # Center the label on the canvas
        canvas_w = self.preview_canvas_width_px
        canvas_h = self.preview_canvas_height_px
        x_offset = (canvas_w - label_width_px) / 2
        y_offset = (canvas_h - label_height_px) / 2
        
        # Draw border
        self.preview_canvas.create_rectangle(x_offset, y_offset, x_offset + label_width_px, y_offset + label_height_px, outline="black")
        
        # Draw vertical divider
        divider_x_px = x_offset + (label_width_px * 0.75)
        self.preview_canvas.create_line(divider_x_px, y_offset, divider_x_px, y_offset + label_height_px, fill="black")
        
        # Padding for text inside label (in px)
        padding_px = self.mm_to_px(2) # Approx 2mm padding
        
        # --- LEFT SIDE ---
        # Collect selected fields for preview
        selected_preview_fields = []
        # Recipient part
        for field_key in ["TITLE1", "NAME1", "surname", "post"]:
            if self.field_vars.get(field_key) and self.field_vars[field_key].get() == 1:
                # Find the label for this key
                field_label = next((f["label"] for f in self.all_fields_info if f["key"] == field_key), field_key)
                if field_key == "post":
                    selected_preview_fields.append(f"({field_label})")
                else:
                    selected_preview_fields.append(field_label)
        
        # Join recipient fields into one line for preview simplicity
        recipient_line = " ".join(selected_preview_fields)
        if recipient_line:
            self.preview_canvas.create_text(x_offset + padding_px, y_offset + padding_px + 5, anchor="nw", text=recipient_line, font=("Helvetica", 9, "bold"))

        # Address part
        current_y_text = y_offset + padding_px + 20 # Start below recipient line
        address_line_height_px = 12 # Approx line height for preview
        
        address_field_keys = ["co_name", "co_name_chi", "UNIT_NAME", "unit_name_chi", "sub_unit", "sub_unit_chi", "add1", "add2", "state"]
        for field_key in address_field_keys:
            if self.field_vars.get(field_key) and self.field_vars[field_key].get() == 1:
                field_label = next((f["label"] for f in self.all_fields_info if f["key"] == field_key), field_key)
                self.preview_canvas.create_text(x_offset + padding_px, current_y_text, anchor="nw", text=field_label, font=("Helvetica", 8))
                current_y_text += address_line_height_px
                if current_y_text > y_offset + label_height_px - padding_px: # Avoid overflow
                    break
        
        # --- RIGHT SIDE ---
        right_section_start_x = divider_x_px
        right_section_width_px = (x_offset + label_width_px) - divider_x_px
        
        # Placeholder for Receipt ID (top-right of right panel)
        self.preview_canvas.create_text(right_section_start_x + padding_px, y_offset + padding_px + 5, anchor="nw", text="Rec. # XXXX", font=("Helvetica", 7))
        
        # Custom Right Panel Text (centered in right panel)
        # Use a slightly larger font for the "E" like text
        
        # Get the text directly from the GUI var for the preview of this element
        custom_text_from_gui_for_preview = self.custom_right_panel_text_var.get().strip()
        # Note: For a full preview of combined text (pub code + custom text), 
        # similar logic to simple_labels.py create_label would be needed here,
        # potentially using a dummy data row or simplified logic for pub codes.
        # For now, this just previews the custom text part accurately.

        font_size_custom_text = 12
        # Estimate text width to center it. Tkinter canvas doesn\\'t have a direct stringWidth.
        # This is a rough approximation.
        estimated_text_width = len(custom_text_from_gui_for_preview) * font_size_custom_text * 0.5 
        text_x = right_section_start_x + (right_section_width_px / 2) - (estimated_text_width / 2)
        text_y = y_offset + (label_height_px / 2) # Vertically center
        self.preview_canvas.create_text(text_x, text_y, anchor="w", text=custom_text_from_gui_for_preview, font=("Helvetica", font_size_custom_text, "bold"))

        # Bulletin text (below the custom text)
        bulletin_y_start = text_y + font_size_custom_text # Start below the custom text
        
        # Estimate bulletin text width for centering
        estimated_bulletin_width = len(bulletin_text_preview) * 7 * 0.6 # Assuming font size 7
        bulletin_x = right_section_start_x + (right_section_width_px / 2) - (estimated_bulletin_width / 2)
        self.preview_canvas.create_text(bulletin_x, bulletin_y_start + 5, anchor="w", text=bulletin_text_preview, font=("Helvetica", 7))
        
        # Estimate bulletin number width for centering
        estimated_bulletin_num_width = len(bulletin_number_preview) * 7 * 0.6
        bulletin_num_x = right_section_start_x + (right_section_width_px / 2) - (estimated_bulletin_num_width / 2)
        self.preview_canvas.create_text(bulletin_num_x, bulletin_y_start + 5 + 10, anchor="w", text=bulletin_number_preview, font=("Helvetica", 7))


    def generate(self):
        excel_file = self.excel_file_path_var.get()
        if not excel_file or not os.path.exists(excel_file):
            messagebox.showerror("Error", "Excel file not found.")
            return
        
        selected_category_description = self.category_filter_var.get()
        category_code = None
        if selected_category_description and selected_category_description != "(All Categories)":
            category_code = self.CODE_FROM_DESC.get(selected_category_description)

        selected_category_exclude_description = self.category_exclude_filter_var.get()
        category_exclude_code = None
        if selected_category_exclude_description and selected_category_exclude_description != "(No Exclusions)":
            # Assuming CODE_FROM_DESC can be used for exclusion as well
            category_exclude_code = self.CODE_FROM_DESC.get(selected_category_exclude_description)
        
        selected_status_description = self.status_filter_var.get()
        status_code = None
        if selected_status_description and selected_status_description != "(All Statuses)":
            status_code = self.STATUS_CODE_FROM_DESC.get(selected_status_description)

        selected_status_exclude_description = self.status_exclude_filter_var.get()
        status_exclude_code = None
        if selected_status_exclude_description and selected_status_exclude_description != "(No Exclusions)":
            status_exclude_code = self.STATUS_CODE_FROM_DESC.get(selected_status_exclude_description)

        selected_mail_zone_description = self.mail_zone_filter_var.get()
        mail_zone_code = None
        if selected_mail_zone_description and selected_mail_zone_description != "(All Mail Zones)":
            mail_zone_code = self.MAIL_ZONE_CODE_FROM_DESC.get(selected_mail_zone_description)

        selected_publication_display_name = self.publication_filter_var.get()
        publication_columns_to_check = None 

        if selected_publication_display_name and selected_publication_display_name != "(All Publications)":
            publication_config_entry = self.publication_options_map.get(selected_publication_display_name) # get the entry from the map
            if publication_config_entry: # Check if the key exists and entry is not None
                publication_columns_to_check = publication_config_entry.get("data_columns")
        
        output_path = self.output_filename_var.get().strip() # Now this is the full path
        if not output_path:
            messagebox.showerror("Error", "Output file path cannot be empty.")
            return
        
        # Ensure the path ends with .pdf, though asksaveasfilename should handle this with defaultextension
        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"
        
        # output_path = os.path.join(self.output_dir, output_filename) # REMOVED: output_filename_var now holds full path

        # Restore original config loading logic for generate()
        config_file_path = self.config_file_path_var.get().strip()
        # if not config_file_path or not os.path.exists(config_file_path):
        #     config_to_use = None # This will make generate_labels use its internal default
        # else:
        #      config_to_use = config_file_path # Pass the path

        current_config_overrides, config_file_path_for_generation = self.get_current_config_for_generation()
        
        try:
            self.status_var.set("Generating labels...")
            self.master.update_idletasks() # Refresh UI

            # Get current config overrides from GUI settings
            current_config_for_generation, _ = self.get_current_config_for_generation() # We already have config_file_path

            df = load_data_from_excel(
                excel_file,
                category_filter=category_code,
                category_exclude_filter=category_exclude_code, # Pass the new exclusion filter
                status_filter=status_code,
                mail_zone_filter=mail_zone_code,
                publication_columns=publication_columns_to_check # Pass the data columns for filtering
            )

            if df.empty and (category_code or category_exclude_code or status_code or mail_zone_code or publication_columns_to_check):
                self.status_var.set("No data matches the selected filters.")
                messagebox.showinfo("No Data", "No data matches the selected filters. PDF not generated.")
                return
            elif df.empty:
                self.status_var.set("No data found in the Excel file.")
                messagebox.showinfo("No Data", "No data found in the Excel file. PDF not generated.")
                return

            # Use the full output_path from the variable
            output_pdf_path = self.output_filename_var.get().strip()
            if not output_pdf_path: # Should be caught by earlier check in get_current_config_for_generation, but double check
                messagebox.showerror("Error", "Output file path is empty.")
                self.status_var.set("Error: Output file path empty.")
                return
            if not output_pdf_path.lower().endswith(".pdf"): # Ensure .pdf extension
                 output_pdf_path += ".pdf"


            generate_labels(
                df.to_dict(orient='records'), 
                output_path=output_pdf_path, # Use the full path
                config_file=config_file_path, # Pass the path to the config file
                temp_config_overrides=current_config_for_generation # Pass the GUI overrides
            )
            self.status_var.set(f"Labels generated: {os.path.basename(output_pdf_path)}")
            messagebox.showinfo("Success", f"Labels successfully generated to {output_pdf_path}")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Could not generate labels: {e}\\n{traceback.format_exc()}")


def main_gui():
    root = tk.Tk()
    # Set a wider default geometry for the main window
    # Format: "widthxheight+x_offset+y_offset"
    # Increase width, keep height and offsets reasonable or let window manager decide
    root.geometry("1280x900")
    app = LabelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
