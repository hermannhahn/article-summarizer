import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys

# Add the project root to the Python path to resolve module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.api_config import configure_api
from src.core.text_extraction import extract_text_from_article
from src.core.summarization import summarize_text
from src.utils.file_exporter import save_as_txt, save_as_pdf, save_as_docx, save_as_xlsx, save_as_image

class SummarizerApp:
    def __init__(self, master):
        self.master = master
        master.title("AI Article Summarizer")
        master.geometry("800x600")

        # Configure grid for responsiveness
        master.grid_rowconfigure(0, weight=0)
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Input Frame
        self.input_frame = ttk.LabelFrame(master, text="Input Options", padding="10 10 10 10")
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.input_frame, text="URL(s):").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = tk.Text(self.input_frame, height=4, width=70)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.url_entry.delete('1.0', tk.END) # Explicitly clear it

        ttk.Label(self.input_frame, text="Language:").grid(row=1, column=0, sticky="w", pady=2)
        self.language_var = tk.StringVar(value="português")
        self.language_entry = ttk.Entry(self.input_frame, textvariable=self.language_var)
        self.language_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.input_frame, text="Style:").grid(row=2, column=0, sticky="w", pady=2)
        self.style_var = tk.StringVar(value="a concise paragraph")
        self.style_entry = ttk.Entry(self.input_frame, textvariable=self.style_var)
        self.style_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.input_frame, text="Output File:").grid(row=3, column=0, sticky="w", pady=2)
        self.output_file_var = tk.StringVar()
        self.output_file_var.set("") # Explicitly clear it
        self.output_file_entry = ttk.Entry(self.input_frame, textvariable=self.output_file_var)
        self.output_file_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self.input_frame, text="Browse", command=self.browse_output_file).grid(row=3, column=2, padx=5)

        # Buttons Frame
        self.button_frame = ttk.Frame(master, padding="5 5 5 5")
        self.button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.summarize_button = ttk.Button(self.button_frame, text="Summarize", command=self.start_summarization_thread)
        self.summarize_button.grid(row=0, column=0, sticky="ew", padx=5)

        self.clear_button = ttk.Button(self.button_frame, text="Clear", command=self.clear_fields)
        self.clear_button.grid(row=0, column=1, sticky="ew", padx=5)

        # Output Frame
        self.output_frame = ttk.LabelFrame(master, text="Summary Output", padding="10 10 10 10")
        self.output_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.summary_text = tk.Text(self.output_frame, wrap=tk.WORD, height=15)
        self.summary_text.grid(row=0, column=0, sticky="nsew")
        self.summary_text_scrollbar = ttk.Scrollbar(self.output_frame, command=self.summary_text.yview)
        self.summary_text_scrollbar.grid(row=0, column=1, sticky="ns")
        self.summary_text['yscrollcommand'] = self.summary_text_scrollbar.set

    def browse_output_file(self):
        file_types = [
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("Excel spreadsheets", "*.xlsx"),
            ("PNG images", "*.png"),
            ("JPG images", "*.jpg"),
            ("All files", "*.*")
        ]
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            defaultextension=".txt", 
            filetypes=file_types
        )
        if filename:
            self.output_file_var.set(filename)

    def clear_fields(self):
        self.url_entry.delete('1.0', tk.END)
        self.language_var.set("português")
        self.style_var.set("a concise paragraph")
        self.output_file_var.set("")
        self.summary_text.delete('1.0', tk.END)

    def start_summarization_thread(self):
        self.summarize_button.config(state=tk.DISABLED)
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert(tk.END, "Starting summarization...\n")
        
        urls_str = self.url_entry.get('1.0', tk.END).strip()
        urls = [url.strip() for url in urls_str.split('\n') if url.strip()]
        language = self.language_var.get()
        style = self.style_var.get()
        output_file = self.output_file_var.get()

        if not urls:
            messagebox.showerror("Input Error", "Please enter at least one URL.")
            self.summarize_button.config(state=tk.NORMAL)
            return

        # Run summarization in a separate thread to keep GUI responsive
        threading.Thread(target=self._run_summarization, args=(urls, language, style, output_file)).start()

    def _run_summarization(self, urls, language, style, output_file):
        try:
            model = configure_api()
            
            for i, url in enumerate(urls):
                self.update_status(f"\n--- Processing URL {i+1}/{len(urls)}: {url} ---\n")
                article_text = extract_text_from_article(url)
                
                if article_text:
                    summary = summarize_text(model, article_text, language, style)
                    self.update_status(f"\n--- Article Summary (Style: {style}) ---\n")
                    self.update_status(summary + "\n")
                    self.update_status("----------------------------------------------------\n")
                    
                    if output_file:
                        base_filename, ext = os.path.splitext(output_file.lower())
                        if len(urls) > 1: # Add index for batch processing
                            current_output_filename = f"{base_filename}_{i}{ext}"
                        else:
                            current_output_filename = output_file.lower()

                        if current_output_filename.endswith('.txt'):
                            save_as_txt(summary, current_output_filename)
                        elif current_output_filename.endswith('.pdf'):
                            save_as_pdf(summary, current_output_filename)
                        elif current_output_filename.endswith('.docx'):
                            save_as_docx(summary, current_output_filename)
                        elif current_output_filename.endswith('.xlsx'):
                            save_as_xlsx(summary, current_output_filename)
                        elif current_output_filename.endswith('.png'):
                            save_as_image(summary, current_output_filename, 'png')
                        elif current_output_filename.endswith('.jpg') or current_output_filename.endswith('.jpeg'):
                            save_as_image(summary, current_output_filename, 'jpeg')
                        else:
                            self.update_status("Unsupported file format. Use .txt, .pdf, .docx, .xlsx, .png, or .jpg.\n")
                else:
                    self.update_status(f"Skipping summarization for {url} due to text extraction failure.\n")
            
        except ValueError as e:
            messagebox.showerror("Configuration Error", str(e))
        except Exception as e:
            messagebox.showerror("An Error Occurred", str(e))
        finally:
            self.master.after(0, lambda: self.summarize_button.config(state=tk.NORMAL)) # Re-enable button

    def update_status(self, message):
        self.master.after(0, self._insert_text_into_summary_box, message)

    def _insert_text_into_summary_box(self, message):
        self.summary_text.insert(tk.END, message)
        self.summary_text.see(tk.END) # Scroll to the end


def main_gui():
    # Clear sys.argv to prevent unexpected arguments from external environments
    if len(sys.argv) > 1:
        sys.argv = [sys.argv[0]]
    root = tk.Tk()
    app = SummarizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
