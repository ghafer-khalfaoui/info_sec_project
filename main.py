
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sdes
import access_control

class EmbeddedDatabase:
    def __init__(self):
        self.users = {
            "dhafer": {"password": "123", "role": "Admin", "clearance": 3},
            "abdallah": {"password": "111", "role": "Admin", "clearance": 3},
            "qais": {"password": "222", "role": "User", "clearance": 1}
        }

        self.roles_permissions = {
            "Admin": ["Read", "Write", "Create", "Delete"],
            "User": ["Read", "Write"]
        }

        self.files = {
            "report.txt": {
                "content": "",
                "classification": 2, 
                "owner": "dhafer"
            }
        }

db = EmbeddedDatabase()
crypto_engine = sdes.SDES()
db.files["report.txt"]["content"] = crypto_engine.encrypt_text("Confidential Project Data")

class SecureFSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CS356 Secure File System")
        self.root.geometry("650x650")
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
        tk.Label(self.root, text="Try 'abdallah' (Admin/3) or 'qais' (User/1) or 'dhafer' (Admin/3)").pack(pady=10)

    def login(self):
        username = self.entry_user.get().strip().lower()
        password = self.entry_pass.get()
        
        if username in db.users and db.users[username]["password"] == password:
            self.current_user = username
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for f in db.files.keys():
            self.file_listbox.insert(tk.END, f)

    def show_dashboard(self):
        self.clear_frame()
        user_info = db.users[self.current_user]
        header = f"Logged in: {self.current_user.capitalize()} | Role: {user_info['role']} | Clearance: {user_info['clearance']}"
        tk.Label(self.root, text=header, font=("Arial", 12, "bold"), fg="blue").pack(pady=10)
        
        tk.Label(self.root, text="Select Encryption Algorithm:", font=("Arial", 10, "bold")).pack()
        self.cipher_box = ttk.Combobox(self.root, values=["Modern: S-DES", "Classical: Caesar Cipher"], state="readonly")
        self.cipher_box.current(0)
        self.cipher_box.pack(pady=5)

        tk.Label(self.root, text="Available Files:").pack()
        self.file_listbox = tk.Listbox(self.root, height=5)
        self.file_listbox.pack()
        self.update_file_list()
        
        frame_btns = tk.Frame(self.root)
        frame_btns.pack(pady=10)
        tk.Button(frame_btns, text="Read File", command=lambda: self.execute_action("Read"), width=10).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_btns, text="Write File", command=lambda: self.execute_action("Write"), width=10).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_btns, text="Create File", command=lambda: self.execute_action("Create"), width=10, bg="lightgreen").grid(row=0, column=2, padx=5, pady=5)
        tk.Button(frame_btns, text="Delete File", command=lambda: self.execute_action("Delete"), width=10, bg="lightcoral").grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(self.root, text="Logout", command=self.show_login, fg="red").pack(pady=5)

        self.lbl_status = tk.Label(self.root, text="Status: Waiting for action...", font=("Arial", 10, "italic"))
        self.lbl_status.pack(pady=5)

        tk.Label(self.root, text="Original Text (Input):").pack()
        self.txt_original = tk.Text(self.root, height=3, width=60)
        self.txt_original.pack()

        tk.Label(self.root, text="Encrypted Data (Binary):").pack()
        self.txt_encrypted = tk.Text(self.root, height=3, width=60)
        self.txt_encrypted.pack()
        
        tk.Label(self.root, text="Decrypted Data (Plaintext):").pack()
        self.txt_decrypted = tk.Text(self.root, height=3, width=60)
        self.txt_decrypted.pack()

    def execute_action(self, action):
        cipher_choice = self.cipher_box.get()
        
        self.txt_original.delete("1.0", tk.END)
        self.txt_encrypted.delete("1.0", tk.END)
        self.txt_decrypted.delete("1.0", tk.END)

        filename = ""
        if action in ["Read", "Write", "Delete"]:
            selection = self.file_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a file first.")
                return
            filename = self.file_listbox.get(selection[0])
        else:
            filename = simpledialog.askstring("Create File", "Enter new filename:")
            if not filename: return

        granted, message = access_control.check_access(self.current_user, filename, action, db)
        
        if not granted:
            self.lbl_status.config(text=message, fg="red")
            messagebox.showerror("Access Denied", message)
            return

        self.lbl_status.config(text=message, fg="green")

        if action == "Read":
            enc_data = db.files[filename]["content"]
            self.txt_encrypted.insert(tk.END, enc_data)
            
            if "Modern" in cipher_choice:
                dec_data = crypto_engine.decrypt_text(enc_data)
            else:
                dec_data = crypto_engine.decrypt_caesar(enc_data)
                
            self.txt_decrypted.insert(tk.END, dec_data)
            
        elif action == "Write":
            user_input = simpledialog.askstring("Input Data", f"Enter text to append to '{filename}':")
            if not user_input: return
            
            self.txt_original.insert(tk.END, user_input)
            old_enc = db.files[filename]["content"]
            
            if "Modern" in cipher_choice:
                old_dec = crypto_engine.decrypt_text(old_enc) if old_enc else ""
                new_enc = crypto_engine.encrypt_text(old_dec + " " + user_input)
            else:
                old_dec = crypto_engine.decrypt_caesar(old_enc) if old_enc else ""
                new_enc = crypto_engine.encrypt_caesar(old_dec + " " + user_input)

            db.files[filename]["content"] = new_enc
            self.txt_encrypted.insert(tk.END, new_enc)
            self.txt_decrypted.insert(tk.END, old_dec + " " + user_input)
            messagebox.showinfo("Success", "File updated and encrypted.")

        elif action == "Create":
            file_text = simpledialog.askstring("File Content", "Enter initial text for the file:")
            cls_input = simpledialog.askinteger("Classification", "Enter Security Level (0-3):", minvalue=0, maxvalue=3)
            
            if file_text is None or cls_input is None: return
            
            self.txt_original.insert(tk.END, file_text)
            
            if "Modern" in cipher_choice:
                enc_text = crypto_engine.encrypt_text(file_text)
            else:
                enc_text = crypto_engine.encrypt_caesar(file_text)
                
            db.files[filename] = {
                "content": enc_text,
                "classification": cls_input,
                "owner": self.current_user
            }
            self.update_file_list()
            self.txt_encrypted.insert(tk.END, enc_text)
            messagebox.showinfo("Success", f"File '{filename}' created successfully!")

        elif action == "Delete":
            del db.files[filename]
            self.update_file_list()
            messagebox.showinfo("Success", f"File '{filename}' deleted successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureFSApp(root)
    root.mainloop()
