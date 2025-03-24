import customtkinter as ctk

root = ctk.CTk()

def open_toplevel():
    top = ctk.CTkToplevel(root)
    top.title("Fenêtre Toplevel")
    top.attributes("-topmost", True)  # Forcer au premier plan
    top.lift()                       # Remonter la fenêtre
    top.focus_force()                # Donner le focus à la fenêtre toplevel
    # Après 100 ms, retirer l'attribut pour permettre l'interaction normale
    top.after(100, lambda: top.attributes("-topmost", False))

btn = ctk.CTkButton(root, text="Ouvrir Toplevel", command=open_toplevel)
btn.pack(pady=20)

root.mainloop()
