create database emp_db;
use emp_db;
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100),
    status ENUM('Active','Inactive')
);

CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(100),
    base_salary INT,
    status ENUM('Active','Inactive')
);

CREATE TABLE employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_name VARCHAR(100),
    job_id INT,
    branch_id INT,
    bonus INT,
    total_salary INT,
    status ENUM('Active','Inactive'),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE salary_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT,
    old_salary INT,
    new_salary INT,
    change_type VARCHAR(50),
    change_date DATETIME,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);


-- -------------------------------------

CREATE TABLE employee_salary_log (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    month_year VARCHAR(7),   -- format: 2025-01
    base_salary INT,
    bonus INT,
    leave_days INT,
    deduction INT,
    final_salary INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);


INSERT INTO jobs (job_title, base_salary, status) VALUES
('B.A.', 15000, 'Active'),
('S.B.A.', 12000, 'Active'),
('T.B.A.', 10000, 'Active'),
('Data Analyst', 65000, 'Active'),
('Clerk', 25000, 'Active'),
('Receptionist', 20000, 'Active'),
('Accountant', 45000, 'Active'),
('Supervisor', 40000, 'Active'),
('HR', 60000, 'Active'),
('Team Lead', 70000, 'Active'),
('Store Manager', 55000, 'Active'),
('Software Engineer', 80000, 'Active'),
('Manager', 100000, 'Active');



INSERT INTO branches (branch_name, status) VALUES
('Rewa', 'Active'),
('Bhopal', 'Active'),
('Indore', 'Active'),
('Delhi', 'Active'),
('Mumbai', 'Active'),
('Pune', 'Active');



use emp_db;
select * from salary_history;
select * from jobs;
select * from branches;
AlTER TABLE employees add phone varchar(12);
AlTER TABLE employees add email varchar(50);
AlTER TABLE employees add location varchar(50);
select * from employees ;
select * from salary_history;
select * from employee_salary_log ;
DESC EMPLOYEES;
alter table employees rename column location to address;
alter table jobs auto_increment=1;

alter table employee_salary_log
add unique key uniq_emp_month (emp_id,month_year);

delete from employees;
delete from jobs;
delete from branches;



set FOREIGN_KEY_CHECKS=0;






INSERT INTO employees
(emp_name, phone, email, address, job_id, branch_id, bonus, total_salary, status)
values

('Amit Sharma','9876543210','amit@gmail.com','Delhi',1,1,2000,32000,'Active'),

('Rohit Verma','9876543211','rohit@gmail.com','Noida',2,1,1500,41500,'Active'),
('Neha Singh','9876543212','neha@gmail.com','Gurgaon',3,2,3000,53000,'Active'),

('Pooja Patel','9876543213','pooja@gmail.com','Ahmedabad',2,3,1000,41000,'Inactive'),

('Vikas Yadav','9876543214','vikas@gmail.com','Indore',1,4,2000,32000,'Active'),

('Ankit Mishra','9876543215','ankit@gmail.com','Bhopal',3,4,2500,52500,'Active'),

('Ravi Kumar','9876543216','ravi@gmail.com','Patna',1,5,1000,31000,'Inactive'),

('Sonal Jain','9876543217','sonal@gmail.com','Ujjain',2,4,1800,41800,'Active'),

('Karan Mehta','9876543218','karan@gmail.com','Mumbai',4,6,5000,75000,'Active'),

('Simran Kaur','9876543219','simran@gmail.com','Pune',3,6,3000,53000,'Active'),


('Deepak Soni','9876543220','deepak@gmail.com','Jaipur',1,3,1200,31200,'Active'),

('Nitin Agarwal','9876543221','nitin@gmail.com','Agra',2,2,1600,41600,'Inactive'),

('Ayesha Khan','9876543222','ayesha@gmail.com','Lucknow',3,5,2800,52800,'Active'),

('Manish Gupta','9876543223','manish@gmail.com','Kanpur',1,5,900,30900,'Active'),

('Ritu Saxena','9876543224','ritu@gmail.com','Gwalior',2,4,1700,41700,'Active'),

('Suresh Pal','9876543225','suresh@gmail.com','Rewa',1,4,1100,31100,'Active'),

('Kavita Rao','9876543226','kavita@gmail.com','Nagpur',3,6,2600,52600,'Inactive'),

('Harsh Tiwari','9876543227','harsh@gmail.com','Satna',10,3,1400,41400,'Active'),
('Nisha Arora','9876543228','nisha@gmail.com','Faridabad',12,1,6000,76000,'Active'),
('Prakash Dubey','9876543229','prakash@gmail.com','Jabalpur',11,4,1300,31300,'Active');







