import streamlit as st
import pandas as pd
import plotly.express as px

from repositories.attendance_repository import (
    get_admin_summary,
    get_all_attendance_records
)

from repositories.employee_repository import (
    get_all_employees,
    deactivate_employee,
    activate_employee
)

from services.leave_service import (
    get_leave_requests_for_admin,
    approve_leave,
    reject_leave,
    get_leave_kpis
)

from repositories.audit_repository import get_all_audit_logs
from services.audit_service import log_action


def show_admin_dashboard():
    st.title("Admin Dashboard")

    summary = get_admin_summary()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Employees", summary["total_employees"])
    col2.metric("Present Today", summary["present_today"])
    col3.metric("Late Today", summary["late_today"])
    col4.metric("Avg Hours", summary["avg_working_hours"])

    col5, col6, col7 = st.columns(3)

    col5.metric("Absent Today", summary["absent_today"])
    col6.metric("Half Day Today", summary["half_day_today"])
    col7.metric("Total Overtime", summary["total_overtime"])

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Attendance Analytics",
        "Employees",
        "Leave Requests",
        "Audit Logs"
    ])

    with tab1:
        records = get_all_attendance_records()

        if records:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True)

            if "dept_name" in df.columns:
                dept_df = df.groupby("dept_name")["attendance_id"].count().reset_index()
                fig = px.bar(
                    dept_df,
                    x="dept_name",
                    y="attendance_id",
                    title="Department-wise Attendance Records"
                )
                st.plotly_chart(fig, use_container_width=True)

            if "shift_name" in df.columns:
                shift_df = df.groupby("shift_name")["attendance_id"].count().reset_index()
                fig2 = px.pie(
                    shift_df,
                    names="shift_name",
                    values="attendance_id",
                    title="Shift-wise Attendance Distribution"
                )
                st.plotly_chart(fig2, use_container_width=True)

            if "overtime_hours" in df.columns:
                fig3 = px.bar(
                    df,
                    x="full_name",
                    y="overtime_hours",
                    title="Employee Overtime Hours"
                )
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No attendance records found.")

    with tab2:
        employees = get_all_employees()

        if employees:
            emp_df = pd.DataFrame(employees)

            st.subheader("Employee List")
            st.dataframe(emp_df, use_container_width=True)

            st.divider()
            st.subheader("Manage Employee Status")

            employee_options = {
                f"{emp['full_name']} - {emp['email']} - {'Active' if emp['is_active'] else 'Inactive'}": emp["employee_id"]
                for emp in employees
            }

            selected_employee = st.selectbox(
                "Select Employee",
                list(employee_options.keys())
            )

            selected_employee_id = employee_options[selected_employee]

            selected_emp = next(
                emp for emp in employees
                if emp["employee_id"] == selected_employee_id
            )

            st.info(
                f"Selected Employee: {selected_emp['full_name']} | "
                f"Email: {selected_emp['email']} | "
                f"Role: {selected_emp['role']} | "
                f"Status: {'Active' if selected_emp['is_active'] else 'Inactive'}"
            )

            current_admin_id = st.session_state.get("employee_id")

            if selected_emp["is_active"]:
                st.warning(
                    "This will deactivate the employee. "
                    "They will no longer be able to login, but attendance history remains safe."
                )

                confirm_deactivate = st.checkbox("I confirm deactivation")

                if st.button("Deactivate Employee"):
                    if selected_employee_id == current_admin_id:
                        st.error("You cannot deactivate your own admin account.")
                    elif not confirm_deactivate:
                        st.error("Please confirm before deactivating.")
                    else:
                        deactivate_employee(selected_employee_id)

                        log_action(
                            performed_by=current_admin_id,
                            target_employee_id=selected_employee_id,
                            action="Employee Deactivated",
                            description=f"Admin deactivated employee ID {selected_employee_id}."
                        )

                        st.success("Employee deactivated successfully.")
                        st.rerun()

            else:
                st.success(
                    "This employee is currently inactive. "
                    "You can activate the account again."
                )

                confirm_activate = st.checkbox("I confirm activation")

                if st.button("Activate Employee"):
                    if not confirm_activate:
                        st.error("Please confirm before activating.")
                    else:
                        activate_employee(selected_employee_id)

                        log_action(
                            performed_by=current_admin_id,
                            target_employee_id=selected_employee_id,
                            action="Employee Activated",
                            description=f"Admin activated employee ID {selected_employee_id}."
                        )

                        st.success("Employee activated successfully.")
                        st.rerun()
        else:
            st.info("No employees found.")

    with tab3:
        st.subheader("Leave Requests")
        try:
            leave_summary = get_leave_kpis()

            col_l1, col_l2, col_l3, col_l4, col_l5 = st.columns(5)

            col_l1.metric("Total Leaves", leave_summary["total_leave_requests"] or 0)
            col_l2.metric("Pending", leave_summary["pending_leaves"] or 0)
            col_l3.metric("Approved", leave_summary["approved_leaves"] or 0)
            col_l4.metric("Rejected", leave_summary["rejected_leaves"] or 0)
            col_l5.metric("On Leave Today", leave_summary["employees_on_leave_today"] or 0)

            st.divider()

        except Exception as e:
            st.warning("Leave summary could not be loaded.")

        try:
            leave_requests = get_leave_requests_for_admin()

            if leave_requests:
                leave_df = pd.DataFrame(leave_requests)

                st.subheader("Leave Request Filters")

                col_f1, col_f2 = st.columns(2)

                with col_f1:
                    status_filter = st.selectbox(
                        "Filter by Status",
                        ["All", "Pending", "Approved", "Rejected"]
                    )

                with col_f2:
                    leave_type_filter = st.selectbox(
                        "Filter by Leave Type",
                        ["All", "Casual", "Sick", "Earned", "Unpaid"]
                    )

                filtered_df = leave_df.copy()

                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df["status"] == status_filter]

                if leave_type_filter != "All":
                    filtered_df = filtered_df[filtered_df["leave_type"] == leave_type_filter]

                st.dataframe(filtered_df, use_container_width=True)

                csv = filtered_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Leave Requests CSV",
                    data=csv,
                    file_name="leave_requests.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                st.divider()
                st.subheader("Approve / Reject Leave")

                pending_requests = [
                    leave for leave in leave_requests
                    if leave["status"] == "Pending"
                ]

                if pending_requests:
                    leave_options = {
                        f"Leave ID {leave['leave_id']} - {leave['full_name']} - {leave['leave_type']} - {leave['start_date']} to {leave['end_date']}": leave
                        for leave in pending_requests
                    }

                    selected_leave_label = st.selectbox(
                        "Select Pending Leave Request",
                        list(leave_options.keys())
                    )

                    selected_leave = leave_options[selected_leave_label]

                    st.info(
                        f"Employee: {selected_leave['full_name']} | "
                        f"Email: {selected_leave['email']} | "
                        f"Type: {selected_leave['leave_type']} | "
                        f"Dates: {selected_leave['start_date']} to {selected_leave['end_date']} | "
                        f"Reason: {selected_leave['reason']}"
                    )

                    admin_comment = st.text_area(
                        "Admin Comment",
                        key="leave_admin_comment"
                    )

                    col_approve, col_reject = st.columns(2)

                    admin_id = st.session_state.get("employee_id")

                    with col_approve:
                        if st.button("Approve Leave", use_container_width=True):
                            success, message = approve_leave(
                                leave_id=selected_leave["leave_id"],
                                admin_id=admin_id,
                                employee_id=selected_leave["employee_id"],
                                admin_comment=admin_comment
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                    with col_reject:
                        if st.button("Reject Leave", use_container_width=True):
                            success, message = reject_leave(
                                leave_id=selected_leave["leave_id"],
                                admin_id=admin_id,
                                employee_id=selected_leave["employee_id"],
                                admin_comment=admin_comment
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.info("No pending leave requests.")
            else:
                st.info("No leave requests found.")

        except Exception as e:
            st.error("Leave requests failed to load.")
            st.exception(e)

    with tab4:
        st.subheader("Audit Logs")

        try:
            logs = get_all_audit_logs()

            if logs:
                logs_df = pd.DataFrame(logs)

                st.subheader("Audit Log Filters")

                col_a1, col_a2 = st.columns(2)

                with col_a1:
                    action_options = ["All"] + sorted(logs_df["action"].dropna().unique().tolist())

                    action_filter = st.selectbox(
                        "Filter by Action",
                        action_options
                    )

                with col_a2:
                    search_text = st.text_input(
                        "Search Description / Employee",
                        placeholder="Search audit logs..."
                    )

                filtered_logs = logs_df.copy()

                if action_filter != "All":
                    filtered_logs = filtered_logs[filtered_logs["action"] == action_filter]

                if search_text:
                    search_text = search_text.lower()

                    filtered_logs = filtered_logs[
                        filtered_logs.astype(str)
                        .apply(lambda row: row.str.lower().str.contains(search_text).any(), axis=1)
                    ]

                st.dataframe(filtered_logs, use_container_width=True)

                csv = filtered_logs.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Audit Logs CSV",
                    data=csv,
                    file_name="audit_logs.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            else:
                st.info("No audit logs found.")

        except Exception as e:
            st.error("Audit logs failed to load.")
            st.exception(e)