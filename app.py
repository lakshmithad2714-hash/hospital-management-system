import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
from datetime import datetime, date
import webbrowser
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import re
from tkcalendar import Calendar

# ==================== DATABASE SETUP ====================
conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lab_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        report TEXT NOT NULL,
        image_path TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        speciality TEXT NOT NULL,
        contact TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        speciality TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        contact TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ambulance_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        location TEXT NOT NULL
    )
''')
conn.commit()

# ==================== CONSTANTS ====================
HOSPITAL_CONTACT = "123-456-7890"
AMBULANCE_CONTACT = "987-654-3210"

# ==================== VALIDATION FUNCTIONS ====================
def validate_alphabets(input_text):
    """Validate that the input contains only alphabets and spaces."""
    if re.match("^[A-Za-z ]+$", input_text):
        return True
    else:
        return False

def validate_contact(contact):
    """Validate that the contact number is exactly 10 digits."""
    if len(contact) == 10 and contact.isdigit():
        return True
    else:
        return False

# ==================== LOCATION FUNCTIONS ====================
def get_current_location():
    # Return a fixed address
    return "58, Palace Rd, Abshot Layout, Vasanth Nagar, Bengaluru, Karnataka 560052"

def open_google_maps(location=None):
    if location:
        # Open Google Maps with the specified location
        webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={location}")
    else:
        # Open Google Maps without a specific location
        webbrowser.open("https://www.google.com/maps")

# ==================== TKINTER FUNCTIONS ====================
def add_doctor():
    add_doctor_window = tk.Toplevel(root)
    add_doctor_window.title("Add Doctor")
    add_doctor_window.geometry("400x300")
    
    # Doctor Name Entry
    tk.Label(add_doctor_window, text="Doctor Name").pack(pady=5)
    doctor_name = tk.StringVar()
    tk.Entry(add_doctor_window, textvariable=doctor_name).pack()
    
    # Speciality Entry
    tk.Label(add_doctor_window, text="Speciality").pack(pady=5)
    speciality = tk.StringVar()
    tk.Entry(add_doctor_window, textvariable=speciality).pack()
    
    # Contact Entry
    tk.Label(add_doctor_window, text="Contact Number").pack(pady=5)
    contact = tk.StringVar()
    tk.Entry(add_doctor_window, textvariable=contact).pack()
    
    def save_doctor():
        # Validate doctor name (alphabets only)
        if not validate_alphabets(doctor_name.get()):
            messagebox.showerror("Error", "Doctor Name should contain only alphabets and spaces!")
            return
        # Validate speciality (alphabets only)
        if not validate_alphabets(speciality.get()):
            messagebox.showerror("Error", "Speciality should contain only alphabets and spaces!")
            return
        # Validate contact number
        if not validate_contact(contact.get()):
            messagebox.showerror("Error", "Contact number must be exactly 10 digits!")
            return
        
        # Save to database
        cursor.execute(
            "INSERT INTO doctors (name, speciality, contact) VALUES (?, ?, ?)",
            (doctor_name.get(), speciality.get(), contact.get())
        )
        conn.commit()
        messagebox.showinfo("Success", "Doctor Added Successfully")
        add_doctor_window.destroy()
    
    tk.Button(add_doctor_window, text="Save", command=save_doctor, bg="lightblue", font=("Helvetica", 14)).pack(pady=10)

def view_doctors():
    view_doctors_window = tk.Toplevel(root)
    view_doctors_window.title("View Doctors")
    view_doctors_window.geometry("600x400")
    
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    
    if not doctors:
        tk.Label(view_doctors_window, text="No doctors found").pack(pady=10)
    else:
        for doctor in doctors:
            frame = tk.Frame(view_doctors_window)
            frame.pack(pady=5)
            tk.Label(frame, text=f"ID: {doctor[0]}, Name: {doctor[1]}, Speciality: {doctor[2]}, Contact: {doctor[3]}").pack(side="left")

def delete_doctor():
    delete_doctor_window = tk.Toplevel(root)
    delete_doctor_window.title("Delete Doctor")
    delete_doctor_window.geometry("400x200")
    
    # Doctor Name Entry
    tk.Label(delete_doctor_window, text="Doctor Name").pack(pady=5)
    doctor_name = tk.StringVar()
    tk.Entry(delete_doctor_window, textvariable=doctor_name).pack()
    
    def confirm_delete():
        if not doctor_name.get():
            messagebox.showerror("Error", "Doctor Name is required!")
            return
        cursor.execute("DELETE FROM doctors WHERE name=?", (doctor_name.get(),))
        conn.commit()
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Doctor Deleted Successfully")
        else:
            messagebox.showerror("Error", "Doctor Not Found")
        delete_doctor_window.destroy()
    
    tk.Button(delete_doctor_window, text="Delete", command=confirm_delete, bg="lightcoral", font=("Helvetica", 14)).pack(pady=10)

def book_appointment():
    booking_window = tk.Toplevel(root)
    booking_window.title("Book Appointment")
    booking_window.geometry("500x600")
    
    # Display hospital contact number
    tk.Label(booking_window, text=f"Hospital Contact: {HOSPITAL_CONTACT}").pack(pady=5)
    
    # Patient Name Entry
    tk.Label(booking_window, text="Patient Name").pack(pady=5)
    patient_name = tk.StringVar()
    tk.Entry(booking_window, textvariable=patient_name).pack()
    
    # Speciality Dropdown
    tk.Label(booking_window, text="Select Speciality").pack(pady=5)
    speciality = tk.StringVar()
    speciality_dropdown = ttk.Combobox(booking_window, textvariable=speciality, state="readonly")
    speciality_dropdown['values'] = ('Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics')
    speciality_dropdown.current(0)
    speciality_dropdown.pack()
    
    # Doctor Dropdown (populated based on selected speciality)
    tk.Label(booking_window, text="Select Doctor").pack(pady=5)
    doctor = tk.StringVar()
    doctor_dropdown = ttk.Combobox(booking_window, textvariable=doctor, state="readonly")
    doctor_dropdown.pack()
    
    def update_doctor_list(event=None):
        selected_speciality = speciality.get()
        cursor.execute("SELECT name FROM doctors WHERE lower(speciality)=lower(?)", (selected_speciality,))
        doctors_list = cursor.fetchall()
        if doctors_list:
            doctors = [row[0] for row in doctors_list]
        else:
            doctors = ["No doctors available"]
        doctor_dropdown['values'] = doctors
        doctor_dropdown.current(0)
    
    speciality_dropdown.bind("<<ComboboxSelected>>", update_doctor_list)
    update_doctor_list()
    
    # Date Selection with Calendar
    tk.Label(booking_window, text="Select Date").pack(pady=5)
    cal_frame = tk.Frame(booking_window)
    cal_frame.pack(pady=5)
    cal = Calendar(cal_frame, selectmode='day', year=datetime.now().year, 
                   month=datetime.now().month, day=datetime.now().day)
    cal.pack(pady=5)
    
    # Time Selection
    tk.Label(booking_window, text="Select Time").pack(pady=5)
    time_frame = tk.Frame(booking_window)
    time_frame.pack(pady=5)
    
    hour_var = tk.StringVar(value="09")
    tk.Label(time_frame, text="Hour:").pack(side="left")
    hour_dropdown = ttk.Combobox(time_frame, textvariable=hour_var, width=3, state="readonly")
    hour_dropdown['values'] = tuple(f"{i:02d}" for i in range(1, 13))
    hour_dropdown.pack(side="left", padx=5)
    
    minute_var = tk.StringVar(value="00")
    tk.Label(time_frame, text="Minute:").pack(side="left")
    minute_dropdown = ttk.Combobox(time_frame, textvariable=minute_var, width=3, state="readonly")
    minute_dropdown['values'] = tuple(f"{i:02d}" for i in range(0, 60, 15))
    minute_dropdown.pack(side="left", padx=5)
    
    ampm_var = tk.StringVar(value="AM")
    tk.Label(time_frame, text="AM/PM:").pack(side="left")
    ampm_dropdown = ttk.Combobox(time_frame, textvariable=ampm_var, width=3, state="readonly")
    ampm_dropdown['values'] = ('AM', 'PM')
    ampm_dropdown.pack(side="left", padx=5)
    
    # Contact Entry
    tk.Label(booking_window, text="Contact Number").pack(pady=5)
    contact = tk.StringVar()
    tk.Entry(booking_window, textvariable=contact).pack()
    
    def confirm_booking():
        # Validate patient name
        if not validate_alphabets(patient_name.get()):
            messagebox.showerror("Error", "Patient Name should contain only alphabets and spaces!")
            return
        
        # Get selected date from calendar
        selected_date = cal.get_date()
        try:
            appt_date = datetime.strptime(selected_date, '%m/%d/%y').date()
            if appt_date < date.today():
                messagebox.showerror("Error", "Past date not allowed")
                return
        except:
            messagebox.showerror("Error", "Invalid date selection")
            return
        
        # Validate contact
        if not validate_contact(contact.get()):
            messagebox.showerror("Error", "Contact number must be exactly 10 digits!")
            return
        
        # Format time
        selected_time = f"{hour_var.get()}:{minute_var.get()} {ampm_var.get()}"
        
        cursor.execute("""INSERT INTO appointments 
                        (patient_name, doctor_name, speciality, date, time, contact) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (patient_name.get(), doctor.get(), speciality.get(), 
                         selected_date, selected_time, contact.get()))
        conn.commit()
        messagebox.showinfo("Success", "Appointment Booked Successfully")
        booking_window.destroy()
    
    tk.Button(booking_window, text="Confirm Booking", command=confirm_booking, 
              bg="lightgreen", font=("Helvetica", 14)).pack(pady=10)

def view_appointments():
    win = tk.Toplevel(root)
    win.title("View Appointments")
    win.geometry("600x400")
    
    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()
    
    if not appointments:
        tk.Label(win, text="No appointments found").pack(pady=10)
    else:
        for appt in appointments:
            frame = tk.Frame(win)
            frame.pack(pady=5)
            tk.Label(frame, text=f"ID: {appt[0]}, Patient: {appt[1]}, Doctor: {appt[2]}, Date: {appt[4]}, Time: {appt[5]}, Contact: {appt[6]}").pack(side="left")
            tk.Button(frame, text="Delete", command=lambda id=appt[0]: delete_appointment(id, win)).pack(side="right")

def delete_appointment(appointment_id, win):
    cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
    conn.commit()
    messagebox.showinfo("Success", "Appointment Deleted Successfully")
    win.destroy()
    view_appointments()

def book_ambulance():
    ambulance_window = tk.Toplevel(root)
    ambulance_window.title("Book Ambulance")
    ambulance_window.geometry("500x500")
    ambulance_window.grab_set()  # Make window modal
    
    # Display ambulance contact number
    tk.Label(ambulance_window, text=f"Ambulance Contact: {AMBULANCE_CONTACT}", 
             font=("Helvetica", 12, "bold")).pack(pady=10)
    
    # Patient Name Entry
    tk.Label(ambulance_window, text="Patient Name", font=("Helvetica", 12)).pack(pady=5)
    patient_name = tk.StringVar()
    tk.Entry(ambulance_window, textvariable=patient_name, font=("Helvetica", 12)).pack()
    
    # Contact Entry
    tk.Label(ambulance_window, text="Contact Number", font=("Helvetica", 12)).pack(pady=5)
    contact = tk.StringVar()
    tk.Entry(ambulance_window, textvariable=contact, font=("Helvetica", 12)).pack()
    
    # Location Entry
    tk.Label(ambulance_window, text="Location", font=("Helvetica", 12)).pack(pady=5)
    location = tk.StringVar()
    tk.Entry(ambulance_window, textvariable=location, font=("Helvetica", 12), width=50).pack()
    
    # Buttons Frame
    button_frame = tk.Frame(ambulance_window)
    button_frame.pack(pady=10)
    
    def set_current_location():
        current_location = get_current_location()
        location.set(current_location)
        messagebox.showinfo("Success", "Current location set successfully!")
    
    tk.Button(button_frame, text="Use Current Location", command=set_current_location,
              bg="lightblue", font=("Helvetica", 12)).pack(side="left", padx=5)
    
    def open_maps_for_location():
        if location.get():
            open_google_maps(location.get())
        else:
            messagebox.showerror("Error", "Please enter a location first!")
    
    tk.Button(button_frame, text="Search on Google Maps", command=open_maps_for_location,
              bg="lightgreen", font=("Helvetica", 12)).pack(side="left", padx=5)
    
    def confirm_ambulance_booking():
        # Validate patient name
        if not validate_alphabets(patient_name.get()):
            messagebox.showerror("Error", "Patient Name should contain only alphabets and spaces!")
            return
        
        # Validate contact
        if not validate_contact(contact.get()):
            messagebox.showerror("Error", "Contact number must be exactly 10 digits!")
            return
        
        # Validate location
        if not location.get():
            messagebox.showerror("Error", "Location is required!")
            return
        
        # Save to database
        cursor.execute("""INSERT INTO ambulance_bookings 
                        (patient_name, contact, location) VALUES (?, ?, ?)""",
                        (patient_name.get(), contact.get(), location.get()))
        conn.commit()
        messagebox.showinfo("Success", "Ambulance Booked Successfully!\n\nAmbulance will arrive shortly.")
        ambulance_window.destroy()
    
    tk.Button(ambulance_window, text="Confirm Booking", command=confirm_ambulance_booking,
              bg="orange", font=("Helvetica", 14)).pack(pady=20)

def view_ambulance_bookings():
    win = tk.Toplevel(root)
    win.title("View Ambulance Bookings")
    win.geometry("700x400")
    
    cursor.execute("SELECT * FROM ambulance_bookings")
    bookings = cursor.fetchall()
    
    if not bookings:
        tk.Label(win, text="No ambulance bookings found", font=("Helvetica", 14)).pack(pady=10)
    else:
        for booking in bookings:
            frame = tk.Frame(win)
            frame.pack(pady=5)
            tk.Label(frame, text=f"ID: {booking[0]}, Patient: {booking[1]}, Contact: {booking[2]}, Location: {booking[3]}",
                    font=("Helvetica", 12)).pack(side="left")

def add_lab_report_patient():
    lab_window = tk.Toplevel(root)
    lab_window.title("Add Lab Report")
    lab_window.geometry("700x700")
    lab_window.grab_set()  # Make window modal
    
    try:
        lab_bg_image = Image.open(r"C:\Users\raksh\Downloads\paitent background image.webp")
        lab_bg_image = lab_bg_image.resize((700, 700), Image.Resampling.LANCZOS)
        lab_bg_image_tk = ImageTk.PhotoImage(lab_bg_image)
        lab_bg_label = tk.Label(lab_window, image=lab_bg_image_tk)
        lab_bg_label.image = lab_bg_image_tk
        lab_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        pass
    
    # Main content frame (to place on top of background)
    content_frame = tk.Frame(lab_window, bg='white', bd=2, relief='solid')
    content_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=600)
    
    tk.Label(content_frame, text="Add Lab Report", font=("Helvetica", 16, "bold"), 
             bg='white').pack(pady=10)
    
    # Patient Name Entry
    tk.Label(content_frame, text="Patient Name", font=("Helvetica", 12), bg='white').pack(pady=5)
    patient_name = tk.StringVar()
    tk.Entry(content_frame, textvariable=patient_name, font=("Helvetica", 12), width=40).pack()
    
    # Report Details Entry
    tk.Label(content_frame, text="Report Details", font=("Helvetica", 12), bg='white').pack(pady=5)
    report = tk.Text(content_frame, height=5, width=40, font=("Helvetica", 12))
    report.pack()
    
    # Image Upload Section
    tk.Label(content_frame, text="Upload Image", font=("Helvetica", 12), bg='white').pack(pady=5)
    image_path = tk.StringVar()
    
    # Image display label
    image_label = tk.Label(content_frame, bg='white')
    image_label.pack(pady=5)
    
    def upload_image():
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            image_path.set(file_path)
            display_image(file_path)
    
    def display_image(file_path):
        try:
            img = Image.open(file_path)
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
    
    tk.Button(content_frame, text="Browse Image", command=upload_image,
              bg="lightblue", font=("Helvetica", 12)).pack(pady=5)
    
    def save_report():
        # Validate patient name
        if not validate_alphabets(patient_name.get()):
            messagebox.showerror("Error", "Patient Name should contain only alphabets and spaces!")
            return
        
        # Validate required fields
        report_text = report.get("1.0", tk.END).strip()
        if not patient_name.get() or not report_text:
            messagebox.showerror("Error", "Patient Name and Report Details are required!")
            return
        
        # Save the report and image path to the database
        try:
            cursor.execute(
                "INSERT INTO lab_reports (patient_name, report, image_path) VALUES (?, ?, ?)",
                (patient_name.get(), report_text, image_path.get())
            )
            conn.commit()
            messagebox.showinfo("Success", "Lab Report Added Successfully")
            lab_window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save report: {e}")
    
    tk.Button(content_frame, text="Save Report", command=save_report,
              bg="lightgreen", font=("Helvetica", 14)).pack(pady=10)

def view_lab_reports():
    win = tk.Toplevel(root)
    win.title("View Lab Reports")
    win.geometry("800x600")
    
    cursor.execute("SELECT * FROM lab_reports")
    reports = cursor.fetchall()
    
    if not reports:
        tk.Label(win, text="No lab reports found", font=("Helvetica", 14)).pack(pady=10)
    else:
        # Create a canvas with scrollbar
        canvas = tk.Canvas(win)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for rep in reports:
            frame = tk.Frame(scrollable_frame, bd=1, relief='solid')
            frame.pack(pady=5, padx=10, fill='x')
            
            info_frame = tk.Frame(frame)
            info_frame.pack(side='left', padx=10)
            tk.Label(info_frame, text=f"ID: {rep[0]}", font=("Helvetica", 12)).pack(anchor='w')
            tk.Label(info_frame, text=f"Patient: {rep[1]}", font=("Helvetica", 12)).pack(anchor='w')
            tk.Label(info_frame, text=f"Report: {rep[2]}", font=("Helvetica", 12)).pack(anchor='w')
            
            if rep[3]:  # If image path exists
                try:
                    img = Image.open(rep[3])
                    img = img.resize((150, 150), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    img_label = tk.Label(frame, image=img_tk)
                    img_label.image = img_tk
                    img_label.pack(side='right', padx=10)
                except Exception as e:
                    tk.Label(frame, text="Image not found", fg='red').pack(side='right')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

def open_patient_dashboard():
    patient_window = tk.Toplevel(root)
    patient_window.title("Patient Dashboard")
    patient_window.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
    
    try:
        patient_bg_image = Image.open(r"C:\Users\raksh\Downloads\paitent background image.webp")
        patient_bg_image = patient_bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), 
                                                    Image.Resampling.LANCZOS)
        patient_bg_image_tk = ImageTk.PhotoImage(patient_bg_image)
        patient_bg_label = tk.Label(patient_window, image=patient_bg_image_tk)
        patient_bg_label.image = patient_bg_image_tk
        patient_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        tk.Label(patient_window, text="Patient Background Image Not Found", fg="red").pack(pady=10)
    
    button_frame = tk.Frame(patient_window, bg='white', bd=2, relief='solid')
    button_frame.place(relx=0.5, rely=0.1, anchor='n')
    
    buttons = [
        ("Book Appointment", book_appointment),
        ("View Appointments", view_appointments),
        ("Book Ambulance", book_ambulance),
        ("View Ambulance Bookings", view_ambulance_bookings),
        ("Add Lab Report", add_lab_report_patient),
        ("View Lab Reports", view_lab_reports)
    ]
    
    for text, command in buttons:
        tk.Button(button_frame, text=text, command=command, 
                 font=("Helvetica", 12), width=20, bg='lightblue').pack(side='left', padx=5, pady=10)

def open_admin_dashboard():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Dashboard")
    admin_window.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
    
    try:
        admin_bg_image = Image.open(r"C:\Users\raksh\Downloads\admin background image 2.webp")
        admin_bg_image = admin_bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), 
                                                Image.Resampling.LANCZOS)
        admin_bg_image_tk = ImageTk.PhotoImage(admin_bg_image)
        admin_bg_label = tk.Label(admin_window, image=admin_bg_image_tk)
        admin_bg_label.image = admin_bg_image_tk
        admin_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        tk.Label(admin_window, text="Admin Background Image Not Found", fg="red").pack(pady=10)
    
    button_frame = tk.Frame(admin_window, bg='white', bd=2, relief='solid')
    button_frame.place(relx=0.5, rely=0.1, anchor='n')
    
    buttons = [
        ("Add Doctor", add_doctor),
        ("View Doctors", view_doctors),
        ("View Appointments", view_appointments),
        ("View Ambulance Bookings", view_ambulance_bookings),
        ("View Lab Reports", view_lab_reports),
        ("Delete Doctor", delete_doctor)
    ]
    
    for text, command in buttons:
        tk.Button(button_frame, text=text, command=command,
                 font=("Helvetica", 12), width=20, bg='lightgreen').pack(side='left', padx=5, pady=10)

# ==================== MAIN WINDOW ====================
root = tk.Tk()
root.title("Hospital Management System")
root.attributes("-fullscreen", True)

try:
    main_image = Image.open(r"C:\Users\raksh\Downloads\back ground image.webp")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    main_image = main_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    main_image_tk = ImageTk.PhotoImage(main_image)
    background_label = tk.Label(root, image=main_image_tk)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
except FileNotFoundError:
    tk.Label(root, text="Main Image Not Found", fg="red").pack(pady=10)

# Display contact numbers
tk.Label(root, text=f"Hospital Contact: {HOSPITAL_CONTACT}", 
         font=("Helvetica", 12), bg="white").place(relx=0.95, y=10, anchor="ne")
tk.Label(root, text=f"Ambulance Contact: {AMBULANCE_CONTACT}", 
         font=("Helvetica", 12), bg="white").place(relx=0.95, y=40, anchor="ne")

# Main buttons
button_frame = tk.Frame(root, bg='white', bd=2, relief='solid')
button_frame.place(relx=0.5, rely=0.5, anchor='center')

tk.Button(button_frame, text="Patient Module", width=20, 
          command=open_patient_dashboard, font=("Helvetica", 14),
          bg='lightblue').pack(pady=10)
tk.Button(button_frame, text="Admin Module", width=20,
          command=open_admin_dashboard, font=("Helvetica", 14),
          bg='lightgreen').pack(pady=10)

# Exit button
exit_button = tk.Button(root, text="Exit", command=root.destroy, 
                       bg="red", fg="white", font=("Helvetica", 12))
exit_button.place(relx=0.5, rely=0.9, anchor="center")

root.mainloop()