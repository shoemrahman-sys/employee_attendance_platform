import streamlit as st
import pandas as pd
from services.attendance_service import check_in_employee, check_out_employee
from repositories.attendance_repository import get_today_attendance, get_employee_attendance_history
from services.leave_service import apply_leave, get_my_leave_history , get_my_leave_kpis
from services.audit_service import log_action
from datetime import date
from services.leave_service import is_employee_on_leave

def show_employee_dashboard():
    st.title("Employee Dashboard")

    employee_id = st.session_state.get("employee_id")

    if not employee_id:
        st.error("Employee ID missing. Please logout and login again.")
        return

    st.markdown(f"### Welcome, {st.session_state.get('full_name', 'Employee')}")
    st.write(f"Designation: {st.session_state.get('job_title', 'N/A')}")
    on_leave_today = is_employee_on_leave(employee_id, date.today())
    tab1, tab2 = st.tabs(["Attendance", "Leave Management"])

    with tab1:
        try:
            today = get_today_attendance(employee_id)

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
                                st.success(message)
                            else:
                                st.warning(message)

                            st.rerun()

            st.divider()

            st.subheader("Attendance History")

            history = get_employee_attendance_history(employee_id)

            if history:
                df = pd.DataFrame(history)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No attendance history found.")

        except Exception as e:
            st.error("Employee dashboard failed to load.")
            st.exception(e)

    with tab2:
        try:
            leave_summary = get_my_leave_kpis(employee_id)

            col_l1, col_l2, col_l3, col_l4 = st.columns(4)

            col_l1.metric("Total Requests", leave_summary["total_leave_requests"] or 0)
            col_l2.metric("Pending", leave_summary["pending_leaves"] or 0)
            col_l3.metric("Approved", leave_summary["approved_leaves"] or 0)
            col_l4.metric("Rejected", leave_summary["rejected_leaves"] or 0)

            st.divider()

        except Exception:
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
                st.success(message)
                st.rerun()
            else:
                st.error(message)

        st.divider()

        st.subheader("My Leave History")

        try:
            leave_history = get_my_leave_history(employee_id)

            if leave_history:
                leave_df = pd.DataFrame(leave_history)
                st.dataframe(leave_df, use_container_width=True)
            else:
                st.info("No leave requests found.")

        except Exception as e:
            st.error("Leave history failed to load.")
            st.exception(e)