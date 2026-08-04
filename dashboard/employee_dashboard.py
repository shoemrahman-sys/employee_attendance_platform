import streamlit as st
import pandas as pd
from services.attendance_service import check_in_employee, check_out_employee
from repositories.attendance_repository import get_today_attendance, get_employee_attendance_history
from services.leave_service import apply_leave, get_my_leave_history , get_my_leave_kpis
from services.audit_service import log_action
from datetime import date
from services.leave_service import is_employee_on_leave
from services.correction_service import (
    submit_correction_request,
    get_my_correction_requests
)

@st.cache_data(ttl=60)
def load_today_attendance(employee_id):
    return get_today_attendance(employee_id)


@st.cache_data(ttl=60)
def load_attendance_history(employee_id):
    return get_employee_attendance_history(employee_id)


@st.cache_data(ttl=60)
def load_my_leave_history(employee_id):
    return get_my_leave_history(employee_id)


@st.cache_data(ttl=60)
def load_my_leave_kpis(employee_id):
    return get_my_leave_kpis(employee_id)


@st.cache_data(ttl=60)
def load_my_correction_requests(employee_id):
    return get_my_correction_requests(employee_id)

@st.cache_data(ttl=60)
def load_leave_status(employee_id):
    return is_employee_on_leave(employee_id, date.today())

@st.cache_data
def attendance_dataframe(history):
    return pd.DataFrame(history)


@st.cache_data
def leave_dataframe(history):
    return pd.DataFrame(history)


@st.cache_data
def correction_dataframe(history):
    return pd.DataFrame(history)

def show_employee_dashboard():
    st.title("Employee Dashboard")

    employee_id = st.session_state.get("employee_id")

    if not employee_id:
        st.error("Employee ID missing. Please logout and login again.")
        return
    attendance_history = load_attendance_history(employee_id)

    st.markdown(f"### Welcome, {st.session_state.get('full_name', 'Employee')}")
    st.write(f"Designation: {st.session_state.get('job_title', 'N/A')}")
    on_leave_today = load_leave_status(employee_id)
    tab1, tab2, tab3 = st.tabs(["Attendance", "Leave Management", "Attendance Correction"])

    with tab1:
        try:
            today = load_today_attendance(employee_id)
            if on_leave_today:
                status = "On Leave"
            else:
                status = today["status"] if today else "Not Checked In"
            working_hours = today["working_hours"] if today else 0
            overtime_hours = today["overtime_hours"] if today else 0
            late_minutes = today["late_minutes"] if today else 0

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Today's Status", status)
            col2.metric("Working Hours", working_hours)
            col3.metric("Overtime Hours", overtime_hours)
            col4.metric("Late Minutes", late_minutes)

            st.divider()

            col5, col6 = st.columns(2)

            with col5:
                if on_leave_today:
                    st.info("You are on approved leave today. Check-in and check-out are disabled.")
                else:
                    col5, col6 = st.columns(2)

                    with col5:
                        if st.button("Check In", use_container_width=True):
                            success, message = check_in_employee(employee_id)

                            if success:
                                log_action(
                                    performed_by=employee_id,
                                    target_employee_id=employee_id,
                                    action="Check In",
                                    description=f"Employee ID {employee_id} checked in."
                                )
                                load_today_attendance.clear()
                                load_attendance_history.clear()
                                load_leave_status.clear()
                                st.success(message)
                            else:
                                st.warning(message)

                            st.rerun()

                    with col6:
                        if st.button("Check Out", use_container_width=True):
                            success, message = check_out_employee(employee_id)

                            if success:
                                log_action(
                                    performed_by=employee_id,
                                    target_employee_id=employee_id,
                                    action="Check Out",
                                    description=f"Employee ID {employee_id} checked out."
                                )
                                load_today_attendance.clear()
                                load_attendance_history.clear()
                                st.success(message)
                            else:
                                st.warning(message)

                            st.rerun()

            st.divider()

            st.subheader("Attendance History")

            history = attendance_history

            if history:
                st.dataframe(
                    attendance_dataframe(history),
                    use_container_width=True
                )
            else:
                st.info("No attendance history found.")

        except Exception as e:
            st.error("Employee dashboard failed to load.")
            st.exception(e)

    with tab2:
        try:
            leave_summary = load_my_leave_kpis(employee_id)

            col_l1, col_l2, col_l3, col_l4 = st.columns(4)

            col_l1.metric("Total Requests", leave_summary["total_leave_requests"] or 0)
            col_l2.metric("Pending", leave_summary["pending_leaves"] or 0)
            col_l3.metric("Approved", leave_summary["approved_leaves"] or 0)
            col_l4.metric("Rejected", leave_summary["rejected_leaves"] or 0)

            st.divider()

        except Exception :
            st.warning("Leave summary could not be loaded.")
        st.subheader("Apply Leave")

        leave_type = st.selectbox(
            "Leave Type",
            ["Casual", "Sick", "Earned", "Unpaid"]
        )

        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        reason = st.text_area("Reason for Leave")

        if st.button("Submit Leave Request"):
            success, message = apply_leave(
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )

            if success:
                load_my_leave_history.clear()
                load_my_leave_kpis.clear()
                load_leave_status.clear()
                st.success(message)
                st.rerun()
            else:
                st.error(message)

        st.divider()

        st.subheader("My Leave History")

        try:
            leave_history = load_my_leave_history(employee_id)

            if leave_history:
                st.dataframe(
                    leave_dataframe(leave_history),
                    use_container_width=True
                )
            else:
                st.info("No leave requests found.")

        except Exception as e:
            st.error("Leave history failed to load.")
            st.exception(e)

    with tab3:
        st.subheader("Request Attendance Correction")

        history = attendance_history

        if history:
            attendance_options = {
                f"ID {row['attendance_id']} | {row['work_date']} | {row['check_in']} - {row['check_out']}": row[
                    "attendance_id"]
                for row in history
            }

            selected_attendance = st.selectbox(
                "Select Attendance Record",
                list(attendance_options.keys())
            )

            attendance_id = attendance_options[selected_attendance]

            requested_check_in = st.text_input(
                "Requested Check-In DateTime",
                placeholder="YYYY-MM-DD HH:MM:SS"
            )

            requested_check_out = st.text_input(
                "Requested Check-Out DateTime",
                placeholder="YYYY-MM-DD HH:MM:SS"
            )

            reason = st.text_area("Reason for Correction")

            if st.button("Submit Correction Request"):
                success, message = submit_correction_request(
                    employee_id=employee_id,
                    attendance_id=attendance_id,
                    requested_check_in=requested_check_in if requested_check_in else None,
                    requested_check_out=requested_check_out if requested_check_out else None,
                    reason=reason
                )

                if success:
                    load_my_correction_requests.clear()
                    load_attendance_history.clear()
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("No attendance records available for correction.")

        st.divider()

        st.subheader("My Correction Requests")

        correction_history = load_my_correction_requests(employee_id)

        if correction_history:
            st.dataframe(
                correction_dataframe(correction_history),
                use_container_width=True
            )
        else:
            st.info("No correction requests found.")