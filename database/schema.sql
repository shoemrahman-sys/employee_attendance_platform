USE employee_attendance;

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shifts (
    shift_id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name VARCHAR(50) NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    expected_hours DECIMAL(4,2) NOT NULL,
    late_grace_minutes INT DEFAULT 15,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE  employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    dept_id INT,
    shift_id INT,
    job_title varchar(100),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('employee', 'admin') DEFAULT 'employee',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON DELETE SET NULL,

    FOREIGN KEY (shift_id)
        REFERENCES shifts(shift_id)
        ON DELETE SET NULL
);

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    work_date DATE NOT NULL,
    check_in DATETIME,
    check_out DATETIME,
    working_hours DECIMAL(5,2) DEFAULT 0,
    overtime_hours DECIMAL(5,2) DEFAULT 0,

    status ENUM(
        'Present',
        'Absent',
        'Half Day',
        'Missing checkout'
    ) DEFAULT 'Present',

    is_late BOOLEAN DEFAULT FALSE,
    late_minutes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON DELETE CASCADE,

    UNIQUE (employee_id, work_date)
);
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,

    performed_by INT NULL,
    target_employee_id INT NULL,

    action VARCHAR(100) NOT NULL,
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (performed_by)
        REFERENCES employees(employee_id)
        ON DELETE SET NULL,

    FOREIGN KEY (target_employee_id)
        REFERENCES employees(employee_id)
        ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS leave_requests (
    leave_id INT AUTO_INCREMENT PRIMARY KEY,

    employee_id INT NOT NULL,

    leave_type ENUM('Casual', 'Sick', 'Earned', 'Unpaid') NOT NULL,

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    reason TEXT,

    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',

    reviewed_by INT NULL,
    reviewed_at TIMESTAMP NULL,

    admin_comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON DELETE CASCADE,

    FOREIGN KEY (reviewed_by)
        REFERENCES employees(employee_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS attendance_correction_requests (
    correction_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    attendance_id INT NOT NULL,

    requested_check_in DATETIME NULL,
    requested_check_out DATETIME NULL,
    reason TEXT NOT NULL,

    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',

    reviewed_by INT NULL,
    reviewed_at TIMESTAMP NULL,
    admin_comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (attendance_id) REFERENCES attendance(attendance_id),
    FOREIGN KEY (reviewed_by) REFERENCES employees(employee_id)
);

CREATE INDEX idx_attendance_work_date
ON attendance(work_date);

CREATE INDEX idx_attendance_employee_id
ON attendance(employee_id);

CREATE INDEX idx_attendance_status
ON attendance(status);

CREATE INDEX idx_employees_dept_id
ON employees(dept_id);

CREATE INDEX idx_employees_shift_id
ON employees(shift_id);

INSERT INTO departments (dept_name, location) VALUES
('IT', 'Hyderabad'),
('HR', 'Hyderabad'),
('Finance', 'Hyderabad'),
('Sales', 'Hyderabad'),
('Operations', 'Hyderabad');

INSERT INTO shifts (
    shift_name,
    start_time,
    end_time,
    expected_hours,
    late_grace_minutes
) VALUES
('Morning Shift', '09:00:00', '18:00:00', 8.00, 15),
('Evening Shift', '14:00:00', '23:00:00', 8.00, 15),
('Night Shift', '22:00:00', '06:00:00', 8.00, 15);

CREATE TABLE IF NOT EXISTS attendance_correction_requests (
    correction_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    attendance_id INT NOT NULL,

    requested_check_in DATETIME NULL,
    requested_check_out DATETIME NULL,
    reason TEXT NOT NULL,

    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',

    reviewed_by INT NULL,
    reviewed_at TIMESTAMP NULL,
    admin_comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (attendance_id) REFERENCES attendance(attendance_id),
    FOREIGN KEY (reviewed_by) REFERENCES employees(employee_id)
);

CREATE TABLE login_attempts (
    email VARCHAR(255) PRIMARY KEY,
    failed_attempts INT NOT NULL DEFAULT 0,
    locked_until DATETIME NULL,
    last_attempt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);