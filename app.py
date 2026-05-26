import streamlit as st
from repositories.employee_repository import create_employee, get_employee_by_email
from utils.password_utils import hash_password, verify_password
from services.attendance_service import check_in_employee, check_out_employee

st.set_page_config(
    page_title="Employee Attendance System",
    page_icon="🕒",
    layout="wide"
)

if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

if "employee_id" not in st.session_state:
    st.session_state["employee_id"] = None

if "full_name" not in st.session_state:
    st.session_state["full_name"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None


st.title("Employee Attendance Management System")

if st.session_state["is_logged_in"]:
    page = st.sidebar.radio("Go to", ["Employee Dashboard", "Logout"])
else:
    page = st.sidebar.radio("Go to", ["Login", "Register"])


if page == "Register":
    st.subheader("Employee Registration")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    department = st.selectbox("Department", ["HR", "IT", "Finance", "Sales", "Marketing"])
    password = st.text_input("Create Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
        elif full_name == "" or email == "" or password == "":
            st.error("Full name, email, and password are required")
        else:
            hashed_password = hash_password(password)
            create_employee(full_name, email, phone, department, hashed_password)
            st.success("Employee registered successfully")


elif page == "Login":
    st.subheader("Employee Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        employee = get_employee_by_email(email)

        if employee is None:
            st.error("Invalid email or password")
        elif verify_password(password, employee["password_hash"]):
            st.session_state["is_logged_in"] = True
            st.session_state["employee_id"] = employee["employee_id"]
            st.session_state["full_name"] = employee["full_name"]
            st.session_state["role"] = employee["role"]

            st.success(f"Welcome {employee['full_name']}")
            st.rerun()
        else:
            st.error("Invalid email or password")


elif page == "Employee Dashboard":
    st.subheader("Employee Dashboard")
    st.success(f"Welcome, {st.session_state['full_name']}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check In"):
            success, message = check_in_employee(st.session_state["employee_id"])
            if success:
                st.success(message)
            else:
                st.warning(message)

    with col2:
        if st.button("Check Out"):
            success, message = check_out_employee(st.session_state["employee_id"])
            if success:
                st.success(message)
            else:
                st.warning(message)


elif page == "Logout":
    st.session_state["is_logged_in"] = False
    st.session_state["employee_id"] = None
    st.session_state["full_name"] = None
    st.session_state["role"] = None

    st.success("Logged out successfully")
    st.rerun()