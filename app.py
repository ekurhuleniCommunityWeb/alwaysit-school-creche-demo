import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse

# Page Configuration
st.set_page_config(page_title="School & Crèche Management System", layout="wide")

st.title("🏫 Independent School & Crèche Operations Portal")
st.caption("ALWAYS IT | Smarter Systems, Better Business")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("school_creche.db")
    cursor = conn.cursor()
    
    # Student & Family Records Table (POPIA Compliant Structure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            grade_class TEXT NOT NULL,
            dob TEXT NOT NULL,
            parent_name TEXT NOT NULL,
            parent_phone TEXT NOT NULL,
            monthly_fee REAL NOT NULL,
            fee_status TEXT DEFAULT 'Unpaid',
            special_needs TEXT,
            academic_notes TEXT
        )
    """)
    
    # Pre-populate sample data if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ("Amohelang Kabe", "Grade R", "2021-04-12", "Isaac Kabe", "27840580413", 1200.0, "Paid", "None", "Excellent progress in phonics and numbers."),
            ("Lerato Mokoena", "Toddlers (2-3 yrs)", "2023-08-19", "Thabo Mokoena", "27825751266", 950.0, "Unpaid", "Lactose Intolerant", "Adapting well to group play routines."),
            ("Ethan Smith", "Grade 1", "2020-01-15", "Sarah Smith", "27731112233", 1500.0, "Partial", "Asthma", "Needs mild encouragement in reading aloud.")
        ]
        cursor.executemany("""
            INSERT INTO students (student_name, grade_class, dob, parent_name, parent_phone, monthly_fee, fee_status, special_needs, academic_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_students)
        
    conn.commit()
    conn.close()

init_db()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("logo.png", width=140) if st.sidebar.button("ALWAYS IT Home") else None
st.sidebar.title("School Operations")
menu = st.sidebar.radio("Navigate", [
    "📋 Admissions & Paperwork", 
    "💳 Fee Tracking & Parent Alerts", 
    "🔒 Secure Student & Family Records",
    "📝 Report Cards & Special Needs"
])

# Module 1: Admissions & Digitize Paperwork
if menu == "📋 Admissions & Paperwork":
    st.header("Digitize Your Admissions Paperwork")
    st.info("Quickly admit new learners into independent schools, crèches, daycares, or nurseries.")
    
    with st.form("admission_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Learner Full Name")
            grade_class = st.selectbox("Grade / Class Group", ["Nursery (0-2 yrs)", "Toddlers (2-3 yrs)", "Grade 000 / R", "Grade 1 - 3", "Grade 4 - 7"])
            dob = st.date_input("Date of Birth")
            monthly_fee = st.number_input("Monthly Tuition Fee (R)", value=1200.0, step=100.0)
        with col2:
            parent_name = st.text_input("Parent / Guardian Name")
            parent_phone = st.text_input("Parent WhatsApp Contact (e.g., 27840580413)")
            special_needs = st.text_input("Allergies / Special Needs", value="None")
            academic_notes = st.text_area("Initial Academic / Behavioral Notes", value="New Enrolment")
            
        if st.form_submit_button("Complete Digital Admission"):
            if student_name and parent_phone:
                conn = sqlite3.connect("school_creche.db")
                c = conn.cursor()
                c.execute("""
                    INSERT INTO students (student_name, grade_class, dob, parent_name, parent_phone, monthly_fee, special_needs, academic_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_name, grade_class, str(dob), parent_name, parent_phone, monthly_fee, special_needs, academic_notes))
                conn.commit()
                conn.close()
                st.success(f"Successfully admitted {student_name} to {grade_class}!")
            else:
                st.warning("Please provide Learner Name and Parent Contact.")

# Module 2: Fee Tracking & Automated Notifications
elif menu == "💳 Fee Tracking & Parent Alerts":
    st.header("Automated Fee Tracking & Parent Notifications")
    
    conn = sqlite3.connect("school_creche.db")
    df = pd.read_sql_query("SELECT id, student_name, grade_class, parent_name, parent_phone, monthly_fee, fee_status FROM students", conn)
    
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Update Tuition Status")
        student_id = st.selectbox("Select Student ID", df["id"].tolist() if not df.empty else [None])
        new_status = st.selectbox("Fee Status", ["Paid", "Unpaid", "Partial"])
        
        if st.button("Save Fee Status"):
            if student_id:
                c = conn.cursor()
                c.execute("UPDATE students SET fee_status = ? WHERE id = ?", (new_status, student_id))
                conn.commit()
                st.success("Fee status updated!")
                st.rerun()

    with col2:
        st.subheader("📲 Send 1-Click WhatsApp Fee Alert")
        if student_id:
            s_row = df[df["id"] == student_id].iloc[0]
            phone = str(s_row["parent_phone"]).replace("+", "").strip()
            
            if s_row["fee_status"] != "Paid":
                msg = f"Dear {s_row['parent_name']}, this is a friendly reminder regarding the monthly school fee of R{s_row['monthly_fee']} for {s_row['student_name']} ({s_row['grade_class']}). Please settle at your earliest convenience."
                btn_color = "#FF9800"
                btn_text = "📲 Send Fee Reminder Notice"
            else:
                msg = f"Dear {s_row['parent_name']}, thank you! Payment of R{s_row['monthly_fee']} for {s_row['student_name']} has been received."
                btn_color = "#25D366"
                btn_text = "✅ Send Payment Receipt Confirmation"
                
            whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:{btn_color};color:white;border:none;padding:10px 18px;border-radius:5px;font-weight:bold;cursor:pointer;">{btn_text}</button></a>', unsafe_allow_html=True)
    conn.close()

# Module 3: Secure Student & Family Records (POPIA)
elif menu == "🔒 Secure Student & Family Records":
    st.header("POPIA-Compliant Family & Student Records")
    
    conn = sqlite3.connect("school_creche.db")
    df = pd.read_sql_query("SELECT id, student_name, grade_class, dob, parent_name, parent_phone, special_needs FROM students", conn)
    
    search_query = st.text_input("🔍 Search Record by Student Name or Class:")
    if search_query:
        df = df[df["student_name"].str.contains(search_query, case=False) | df["grade_class"].str.contains(search_query, case=False)]
        
    st.dataframe(df, use_container_width=True)
    conn.close()

# Module 4: Report Cards & Special Needs
elif menu == "📝 Report Cards & Special Needs":
    st.header("Academic Progress & Special Needs Tracking")
    
    conn = sqlite3.connect("school_creche.db")
    df = pd.read_sql_query("SELECT id, student_name, grade_class, special_needs, academic_notes FROM students", conn)
    
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Update Teacher Remarks / Report Card Notes")
    selected_s = st.selectbox("Select Student", df["id"].tolist() if not df.empty else [None])
    
    if selected_s:
        current_row = df[df["id"] == selected_s].iloc[0]
        st.write(f"**Student:** {current_row['student_name']} ({current_row['grade_class']})")
        
        with st.form("notes_form"):
            new_needs = st.text_input("Allergies / Medical / Special Needs", value=current_row["special_needs"])
            new_notes = st.text_area("Teacher Remarks / Term Progress", value=current_row["academic_notes"])
            
            if st.form_submit_button("Save Remarks"):
                c = conn.cursor()
                c.execute("UPDATE students SET special_needs = ?, academic_notes = ? WHERE id = ?", (new_needs, new_notes, selected_s))
                conn.commit()
                st.success("Report records updated!")
                st.rerun()
    conn.close()