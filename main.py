
import tkinter as tk
from tkinter import messagebox, simpledialog 
import database
import sdes
import access_control


crypto_engine = sdes.SDES()
database.files["report.txt"]["content"] = crypto_engine.encrypt_text("Confidential Project Data")

class SecureFSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CS356 Secure File System")
        self.root.geometry("600x550")
        self.current_user = None
        
        self.show_login()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        
        tk.Label(self.root, text="Secure File System Login", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(self.root, text="Username:").pack()
        self.entry_user = tk.Entry(self.root)
        self.entry_user.pack(pady=5)
        
        tk.Label(self.root, text="Password:").pack()
        self.entry_pass = tk.Entry(self.root, show="*")
        self.entry_pass.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.login, bg="lightblue").pack(pady=20)
        
        tk.Label(self.root, text="Try 'dhafer' (pwd:123) or 'hamza ' (pwd:456) or 'ahmed ' (pwd:789)").pack(pady=10)

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        if username in database.users and database.users[username]["password"] == password:
            self.current_user = username
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_dashboard(self):
        self.clear_frame()
        
        user_info = database.users[self.current_user]
        header = f"Logged in: {self.current_user.capitalize()} | Role: {user_info['role']} | Clearance: {user_info['clearance']}"
        tk.Label(self.root, text=header, font=("Arial", 12, "bold"), fg="blue").pack(pady=10)
        
        # File Selection
        tk.Label(self.root, text="Available Files:").pack()
        self.file_listbox = tk.Listbox(self.root, height=4)
        for f in database.files.keys():
            self.file_listbox.insert(tk.END, f)
        self.file_listbox.pack()
        
        # Action Buttons
        frame_btns = tk.Frame(self.root)
        frame_btns.pack(pady=10)
        tk.Button(frame_btns, text="Read File", command=lambda: self.execute_action("Read")).grid(row=0, column=0, padx=5)
        tk.Button(frame_btns, text="Write File", command=lambda: self.execute_action("Write")).grid(row=0, column=1, padx=5)
        
        tk.Button(self.root, text="Logout", command=self.show_login, fg="red").pack(pady=5)

        # Status Display
        self.lbl_status = tk.Label(self.root, text="Status: Waiting for action...", font=("Arial", 10, "italic"))
        self.lbl_status.pack(pady=5)

        # Display Text Areas
        tk.Label(self.root, text="Encrypted Data (Binary):").pack()
        self.txt_encrypted = tk.Text(self.root, height=4, width=60)
        self.txt_encrypted.pack()
        
        tk.Label(self.root, text="Decrypted Data (Plaintext):").pack()
        self.txt_decrypted = tk.Text(self.root, height=4, width=60)
        self.txt_decrypted.pack()

    def execute_action(self, action):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
            
        filename = self.file_listbox.get(selection[0])
        
        # 1. Perform RBAC and BLP Check using access_control module
        granted, message = access_control.check_access(self.current_user, filename, action)
        
        self.txt_encrypted.delete("1.0", tk.END)
        self.txt_decrypted.delete("1.0", tk.END)
        
        if granted:
            self.lbl_status.config(text=message, fg="green")
            
            if action == "Read":
                enc_data = database.files[filename]["content"]
                self.txt_encrypted.insert(tk.END, enc_data)
                
                dec_data = crypto_engine.decrypt_text(enc_data)
                self.txt_decrypted.insert(tk.END, dec_data)
                
            elif action == "Write":
                
               
                user_input = simpledialog.askstring("Input Data", f"Enter text to add to '{filename}':")
                
               
                if not user_input:
                    self.lbl_status.config(text="Write operation cancelled.", fg="blue")
                    return
                
                # Add a space before the new text so it doesn't run into the old text
                new_text = " " + user_input
                
                # Decrypt the old data, append the new text, and re-encrypt
                old_decrypted = crypto_engine.decrypt_text(database.files[filename]["content"])
                new_encrypted = crypto_engine.encrypt_text(old_decrypted + new_text)
                database.files[filename]["content"] = new_encrypted
                
                # Display the results
                self.txt_encrypted.insert(tk.END, new_encrypted)
                self.txt_decrypted.insert(tk.END, old_decrypted + new_text)
                messagebox.showinfo("Success", f"File '{filename}' successfully updated and encrypted.")
        else:
            self.lbl_status.config(text=message, fg="red")
            messagebox.showerror("Access Denied", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureFSApp(root)
    root.mainloop()
