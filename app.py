import streamlit as st
from services.auth_service import login_user, register_user ,reset_password
from repositories.department_repository import get_active_departments
from repositories.shift_repository import get_active_shifts
from dashboard.employee_dashboard import show_employee_dashboard
from dashboard.admin_dashboard import show_admin_dashboard
from services.audit_service import log_action

st.set_page_config(
    page_title="Employee Attendance Analytics Platform",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}
.login-card {
    background-color: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
h1, h2, h3 {
    color: #1f2937;
}
</style>
""", unsafe_allow_html=True)

def init_session():
    defaults = {
        "logged_in": False,
        "employee_id": None,
        "full_name": None,
        "email": None,
        "role": None,
        "dept_id": None,
        "shift_id": None,
        "job_title": None,
        "page": "Login"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def logout():
    employee_id = st.session_state.get("employee_id")
    full_name = st.session_state.get("full_name")

    if employee_id:
        log_action(
            performed_by=employee_id,
            target_employee_id=employee_id,
            action="Logout",
            description=f"{full_name} logged out."
        )

    st.session_state.clear()
    st.rerun()

def login_page():
    st.title("Employee Attendance Analytics Platform")
    st.subheader("Secure Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.error("Please enter both email and password.")
                return

            employee = login_user(email, password)

            if employee:
                st.session_state["logged_in"] = True
                st.session_state["employee_id"] = employee["employee_id"]
                st.session_state["full_name"] = employee["full_name"]
                st.session_state["email"] = employee["email"]
                st.session_state["role"] = employee["role"]
                st.session_state["dept_id"] = employee["dept_id"]
                st.session_state["shift_id"] = employee["shift_id"]
                st.session_state["job_title"] = employee["job_title"]

                log_action(
                    performed_by=employee["employee_id"],
                    target_employee_id=employee["employee_id"],
                    action="Login",
                    description=f"{employee['full_name']} logged in successfully."
                )

                st.success("Login successful")
                st.rerun()
            else:
                log_action(
                    performed_by=None,
                    target_employee_id=None,
                    action="Failed Login",
                    description=f"Failed login attempt for email: {email}"
                )

                st.error("Invalid email or password")



    with col2:
        if st.button("Create Account", use_container_width=True):
            st.session_state["page"] = "Register"
            st.rerun()

    with st.expander("Forgot Password?"):
        reset_email = st.text_input("Registered Email", key="reset_email")
        new_password = st.text_input(
            "New Password",
            type="password",
            key="new_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button("Reset Password", use_container_width=True):
            if not reset_email or not new_password or not confirm_password:
                st.error("Please fill all password reset fields.")
                return

            success, message = reset_password(
                reset_email,
                new_password,
                confirm_password
            )

            if success:
                log_action(
                    performed_by=None,
                    target_employee_id=None,
                    action="Password Reset",
                    description=f"Password reset successful for email: {reset_email}"
                )

                st.success(message)
            else:
                st.error(message)

def register_page():
    st.title("Employee Registration")

    departments = get_active_departments()
    shifts = get_active_shifts()

    if not departments or not shifts:
        st.error("Departments or shifts are missing. Please run schema.sql first.")
        return

    dept_options = {dept["dept_name"]: dept["dept_id"] for dept in departments}
    shift_options = {shift["shift_name"]: shift["shift_id"] for shift in shifts}

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    job_title = st.text_input("Job Title")
    department_name = st.selectbox("Department", list(dept_options.keys()))
    shift_name = st.selectbox("Shift", list(shift_options.keys()))
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Register", use_container_width=True):
            if not full_name or not email or not phone or not job_title or not password:
                st.error("Please fill all required fields.")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            success, message = register_user(
                full_name=full_name,
                email=email,
                phone=phone,
                dept_id=dept_options[department_name],
                shift_id=shift_options[shift_name],
                job_title=job_title,
                password=password
            )

            if success:
                st.success(message)
                st.session_state["page"] = "Login"
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button("Back to Login", use_container_width=True):
            st.session_state["page"] = "Login"
            st.rerun()

init_session()

if not st.session_state["logged_in"]:
    if st.session_state["page"] == "Register":
        register_page()
    else:
        login_page()
else:
    st.sidebar.title("Navigation")
    st.sidebar.write(f"User: {st.session_state['full_name']}")
    st.sidebar.write(f"Role: {st.session_state['role']}")
    st.sidebar.write(f"Designation: {st.session_state['job_title']}")

    if st.sidebar.button("Logout"):
        logout()

    if st.session_state["role"] == "admin":
        show_admin_dashboard()
    else:
        show_employee_dashboard()