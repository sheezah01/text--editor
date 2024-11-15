import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, colorchooser
from tkinter.font import Font, families
import os
from datetime import datetime

class ModernTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Text Editor")
        self.root.geometry("1000x700")
        
        # Theme colors
        self.colors = {
            'bg': '#2E2E2E',
            'text_bg': '#1E1E1E',
            'text_fg': '#FFFFFF',
            'status_bg': '#1E1E1E',
            'status_fg': '#FFFFFF',
            'highlight': '#404040'
        }
        
        # Initialize variables
        self.current_file = None
        self.text_modified = False
        self.highlight_line = True
        self.line_numbers = True
        self.current_theme = "dark"
        
        # Setup UI
        self.setup_styles()
        self.create_ui()
        self.create_menu()
        self.create_shortcuts()
        self.create_context_menu()
        self.setup_auto_save()
        
    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Editor.TFrame', background=self.colors['bg'])
        style.configure('Status.TLabel', 
                       background=self.colors['status_bg'],
                       foreground=self.colors['status_fg'],
                       padding=5)
        
    def create_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Editor.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self.create_toolbar()
        
        # Text area container with line numbers
        self.editor_frame = ttk.Frame(self.main_frame)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers_text = tk.Text(self.editor_frame,
                                       width=4,
                                       padx=3,
                                       pady=5,
                                       takefocus=0,
                                       border=0,
                                       background=self.colors['bg'],
                                       foreground='gray',
                                       font=('Consolas', 11))
        self.line_numbers_text.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text area
        self.text_area = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=('Consolas', 11),
            background=self.colors['text_bg'],
            foreground=self.colors['text_fg'],
            insertbackground=self.colors['text_fg'],
            selectbackground='#404040',
            selectforeground='white',
            pady=5,
            padx=5
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        self.text_area.bind('<KeyRelease>', self.update_line_numbers)
        self.text_area.bind('<Button-1>', self.update_line_numbers)
        self.text_area.bind('<MouseWheel>', self.update_line_numbers)
        
        # Status bars
        self.create_status_bars()
        
    def create_toolbar(self):
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Font selector
        ttk.Label(self.toolbar, text="Font:").pack(side=tk.LEFT, padx=2)
        self.font_family = ttk.Combobox(self.toolbar, width=15, values=sorted(families()))
        self.font_family.set('Consolas')
        self.font_family.pack(side=tk.LEFT, padx=2)
        self.font_family.bind('<<ComboboxSelected>>', self.change_font)
        
        # Font size
        ttk.Label(self.toolbar, text="Size:").pack(side=tk.LEFT, padx=2)
        self.font_size = ttk.Spinbox(self.toolbar, from_=8, to=72, width=5, command=self.change_font)
        self.font_size.set(11)
        self.font_size.pack(side=tk.LEFT, padx=2)
        
        # Buttons
        ttk.Button(self.toolbar, text="🔍", width=3, command=self.show_find_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="📁", width=3, command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="💾", width=3, command=self.save_file).pack(side=tk.LEFT, padx=2)
        
    def create_status_bars(self):
        # Bottom status bar frame
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X)
        
        # Left status
        self.status_left = ttk.Label(status_frame, 
                                   text="Ready", 
                                   style='Status.TLabel')
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Right status (cursor position, etc.)
        self.status_right = ttk.Label(status_frame,
                                    text="Ln 1, Col 1", 
                                    style='Status.TLabel')
        self.status_right.pack(side=tk.RIGHT)
        
        # Update cursor position on key/mouse events
        self.text_area.bind('<KeyRelease>', self.update_cursor_position)
        self.text_area.bind('<Button-1>', self.update_cursor_position)
        
    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        
        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Export as HTML", command=self.export_as_html)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit_application)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find", command=self.show_find_dialog, accelerator="Ctrl+F")
        self.edit_menu.add_command(label="Replace", command=self.show_replace_dialog, accelerator="Ctrl+H")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        
        # View Menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_checkbutton(label="Line Numbers", command=self.toggle_line_numbers)
        self.view_menu.add_checkbutton(label="Highlight Current Line", command=self.toggle_highlight_line)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        self.view_menu.add_command(label="Choose Colors", command=self.choose_colors)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        
        # Tools Menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label="Word Count", command=self.show_word_count)
        self.tools_menu.add_command(label="Character Count", command=self.show_char_count)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Insert DateTime", command=self.insert_datetime)
        self.tools_menu.add_command(label="Insert File Path", command=self.insert_file_path)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        
        self.root.config(menu=self.menu_bar)
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all)
        
        self.text_area.bind("<Button-3>", self.show_context_menu)
        
    def setup_auto_save(self):
        self.auto_save_enabled = False
        self.auto_save_interval = 300000  # 5 minutes in milliseconds
        self.schedule_auto_save()
        
    def schedule_auto_save(self):
        if self.auto_save_enabled and self.text_modified and self.current_file:
            self.save_file()
        self.root.after(self.auto_save_interval, self.schedule_auto_save)
        
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.colors = {
                'bg': '#FFFFFF',
                'text_bg': '#F5F5F5',
                'text_fg': '#000000',
                'status_bg': '#F0F0F0',
                'status_fg': '#000000',
                'highlight': '#E0E0E0'
            }
            self.current_theme = "light"
        else:
            self.colors = {
                'bg': '#2E2E2E',
                'text_bg': '#1E1E1E',
                'text_fg': '#FFFFFF',
                'status_bg': '#1E1E1E',
                'status_fg': '#FFFFFF',
                'highlight': '#404040'
            }
            self.current_theme = "dark"
        
        self.apply_theme()
        
    def apply_theme(self):
        self.text_area.configure(
            background=self.colors['text_bg'],
            foreground=self.colors['text_fg'],
            insertbackground=self.colors['text_fg']
        )
        self.line_numbers_text.configure(
            background=self.colors['bg'],
            foreground='gray'
        )
        self.status_left.configure(background=self.colors['status_bg'])
        self.status_right.configure(background=self.colors['status_bg'])
        
    def choose_colors(self):
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            self.text_area.configure(foreground=color)
            
    def show_word_count(self):
        content = self.text_area.get(1.0, tk.END)
        words = len(content.split())
        messagebox.showinfo("Word Count", f"Total words: {words}")
        
    def show_char_count(self):
        content = self.text_area.get(1.0, tk.END)
        chars = len(content) - 1  # Subtract 1 for the extra newline
        messagebox.showinfo("Character Count", f"Total characters: {chars}")
        
    def insert_datetime(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.INSERT, current_time)
        
    def insert_file_path(self):
        if self.current_file:
            self.text_area.insert(tk.INSERT, self.current_file)
            
    def show_replace_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Find and Replace")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        
        # Find frame
        find_frame = ttk.Frame(dialog)
        find_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(find_frame, text="Find:").pack(side=tk.LEFT)
        find_entry = ttk.Entry(find_frame)
        find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Replace frame
        replace_frame = ttk.Frame(dialog)
        replace_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(replace_frame, text="Replace:").pack(side=tk.LEFT)
        replace_entry = ttk.Entry(replace_frame)
        replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            content = self.text_area.get(1.0, tk.END)
            new_content = content.replace(find_text, replace_text)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, new_content)
            
        ttk.Button(button_frame, text="Replace All", command=replace).pack(side=tk.LEFT, padx=5)