import streamlit as st
import mysql.connector
import pandas as pd
import re
from datetime import datetime

st.sidebar.title("Manu")
page =st.sidebar.radio("Go to",["Employee management","Filter Table","Salary management"])



if page == "Employee management":

# =================================================================================
# connect with mysql database -----------


    conn= mysql.connector.connect(host="localhost",user="shiv",password="1234",database="emp_db")

    if conn.is_connected():
        print("Connected to emp_db successfully")


    st.title("Epmloyee Management System")
    st.write("Select the branch")

# =========================================================
# branch fetchinhg------------------

    cursor =conn.cursor()
    cursor.execute("select branch_id, branch_name from branches WHERE status='Active'")
    branches = cursor.fetchall()
    branch_name=[b[1] for b in branches]
    selected_branch= st. selectbox("select branch",branch_name)

    branch_dict={b[1]: b[0] for b in branches} 
    selected_branch_id = branch_dict[selected_branch]


    # job fetching

    job_cursor =conn.cursor()
    job_cursor.execute("Select job_id, job_title,base_salary from jobs where status = 'Active'")
    jobs=job_cursor.fetchall()

    job_dict={j[1]: (j[0],j[2]) for j in jobs}
    job_name= list(job_dict.keys())


    # employees fetching

    emp_cursor= conn.cursor()
    emp_cursor.execute("""select e.emp_id, e.emp_name, j.base_salary,e.status from
                        employees e join jobs j on e.job_id=j.job_id WHERE e.branch_id = %s order by emp_id desc limit 3""", (selected_branch_id,))
    employees= emp_cursor.fetchall()


    st.markdown("---")
    st.subheader("Employees detail")

    if employees:
        df=pd.DataFrame(employees, columns=["ID","Name","Base Salary","Status"])
        df["Base Salary"]= df["Base Salary"].apply(lambda x:f"₹ {x}")
        def status_color(val):
            color= "green" if val =="Active" else "red"
            return f"color:{color}"
        st.dataframe(df.reset_index(drop=True).style.applymap(status_color,subset=["Status"]),use_container_width=True)

    else:
        st.info("no employee found for this branch.")




# --------------------------------------------- edit and update -------------------------------------------------



    st.markdown("---")
    st.subheader("Edit/Update employee")
    edit_cursor=conn.cursor()
    edit_cursor.execute("select emp_id,emp_name from employees where branch_id=%s order by emp_id desc",(selected_branch_id,))
    edit_emp= edit_cursor.fetchall()



    if edit_emp:
        
        emp_edit_dict={f"{e[0]}|{e[1]}":e[0] for e in edit_emp}
        emp_edit_options= list(emp_edit_dict.keys())

        selected_emp_edit=st.selectbox("Select employee to edit", emp_edit_options)

        selected_emp_edit_id = emp_edit_dict[selected_emp_edit]

        deatil_cursor= conn.cursor()
        deatil_cursor.execute("select emp_name, job_id, address, status from employees where emp_id = %s",(selected_emp_edit_id,))
        emp_detail= deatil_cursor.fetchone() 

        if  not emp_detail: 
            st.warning("employee data not found")
            st.stop()


        current_name,current_job_id, current_address, current_status= emp_detail
            

        job_reverse= {v[0]:k for k,v in job_dict.items()}
        current_job_name= job_reverse[current_job_id]


        st.markdown('### update details')
        
        col1,col2=st.columns(2)
        with col1:
            new_name = st.text_input("Edit Name",value=current_name)
            new_job=st.selectbox('change job',job_name,index=job_name.index(current_job_name))
        with col2:
            new_address = st.text_input("change Address", value= current_address)
            new_status = st.selectbox("change status",["Active","Inactive"],index=0 if current_status == "Active"else 1)

        new_job_id, new_base_salary =job_dict[new_job]
        
        st.info(f"updated new salary:{new_base_salary}")


        col1,col2=st.columns(2)
        with col1:
            update_btn=st.button("Update employee")
        with col2:
            delete_btn=st.button("Delete employee")

        if update_btn:
            update_cursor=conn.cursor()
            update_cursor.execute("update employees set emp_name=%s, job_id=%s,address=%s,status=%s where emp_id=%s",
            (new_name,new_job_id,new_address,new_status,selected_emp_edit_id))
            conn.commit()
            st.success("employee update successfully !")
            st.rerun()

        
        if delete_btn:
            delete_cursor=conn.cursor()
            delete_cursor.execute("delete from employees where emp_id = %s",(selected_emp_edit_id,))
            conn.commit()
            st.success("Employee deleted successfully !")
            st.rerun()
            
      
    else:
        st.info("No employees available to edit in this branch.")


# ====================================== Add emp ========================================

    st.markdown("---")
    st.subheader("Add New Employee")
    st.markdown("---")
    
    selected_job= st.selectbox("Select job",job_name)

    job_id,base_salary=job_dict[selected_job]
    st.info(f"Base salary:{base_salary}")


    # form for page one:-

    with st.form("add_employee_form"):
        col1,col2,col3=st.columns(3)
        with col1:
            emp_name= st.text_input("Employee name")
            phone =st.text_input('Phone')
        with col2:
            email=st.text_input("email id")
            Address=st.text_input("Address")
        with col3:
            
            status= st.selectbox("Status",["Active","Inactive"])
            
            submit=st.form_submit_button("Add Employee")
            



        if submit:
            if emp_name.strip()=="":
                st.error("Name is not be empty ")
                st.stop()
                
            if not re.match(r"[^@]+@[^@]+\.[^@]+",email): 
                st.error("Email formate is wrong")

            if phone.strip()==""or len(phone)<10:
                st.error("Invalid phone number")
                st.stop()    

            total_salary= base_salary 
            
            insert_cursor= conn.cursor()
            insert_cursor.execute("""insert into employees(emp_name, job_id, branch_id,status,phone,email,Address)
                                values(%s,%s,%s,%s,%s,%s,%s,%s)""",(emp_name,job_id,selected_branch_id,status,phone,email,Address))
            conn.commit()
            st.success("Employee added succesfully !")
            st.rerun()



# ======================================================================================================================= #
#                                     2.  SEARCH AND FILTER PAGE                                                                 
# ======================================================================================================================= #







elif page== "Filter Table":
    st.title("Filter")
    st.write("Search and filter employees")
    conn= mysql.connector.connect(host="localhost",user="shiv",password="1234",database="emp_db")


    if "view_more" not in st.session_state:
        st.session_state.view_more=False
    if "page_no" not in st.session_state:
        st.session_state.page_no= 1

    
    search_type= st.selectbox("search by",["Employee ID","Name","Phone","Email"])
    col1,col2=st.columns(2)
    with col1:
        search_text= st.text_input("Enter search value")
    with col2:                          
        status_filter= st.selectbox("Select status",["All","Active","Inactive"])


    col3,col4=st.columns(2)

    job_cursor=conn.cursor()
    job_cursor.execute("Select job_title from jobs where status='Active'")
    jobs= job_cursor.fetchall()

    job_list=['All']+[j[0] for j in jobs]
    with col3:
        selected_job=st.selectbox("Select job",job_list)

    branch_cursor = conn.cursor()
    branch_cursor.execute("select branch_id, branch_name from branches where status='Active'")
    branches= branch_cursor.fetchall()
    branch_dict={b[1]:b[0]for b in branches}
    branch_list=["All"]+ list(branch_dict.keys())
    with col4:
       selected_branch= st.selectbox("select branch",branch_list)



    
    

# -----------------------------------------------------------------




    st.markdown("---")

    st.subheader("select columns")
    all_columns={
        "Employee ID":"emp_id",
        "Name":"emp_name",
        "Address":"address",
        "Phone":"phone",
        "Email":"email",
        "Job":"job_title",
        "Base Salary":"base_salary",
        "Branch":"branch_name",
        "status":"status"
    }       
    selected_columns= st.multiselect("choose column to show",
                                options= list(all_columns.keys()),
                                default=["Employee ID","Name","Address","Phone","Email","Job","Base Salary"])

    
        

    null_filter= st.radio("show data option",["All record","Blank/Null Records"], horizontal=True)
# ================================================


    search_btn= st.button("Search")

    

    if search_btn:
        query= """select e.emp_id, e.emp_name,e.phone,e.email,e.address,e.job_id,j.job_title,j.base_salary,
                    e.branch_id,b.branch_name,e.status from employees e join jobs j on e.job_id=j.job_id join branches b 
                     on e.branch_id=b.branch_id"""
        condition=[]
        values=[]
        if search_text.strip() !="":
            if search_type == "Employee ID":
                condition.append("e.emp_id = %s")
                values.append(int(search_text))

            elif search_type == "Name":
                condition.append("e.emp_name like %s")
                values.append(f"%{search_text}%")

            elif search_type == "Phone":
                condition.append("e.phone like %s")
                values.append(f"%{search_text}%")

            elif search_type == "Email":
                condition.append("e.email like %s")
                values.append(f"%{search_text}%")

           

        if status_filter != "All":
            condition.append("e.status =%s")
            values.append(status_filter) 

        if selected_job !="All":  
            condition.append("j.job_title =%s")
            values.append(selected_job)

        if selected_branch !="All":
            condition.append("e.branch_id =%s")
            values.append(branch_dict[selected_branch])
            
        if condition:
            query +=" WHERE " + " AND ".join(condition)

        query +=" ORDER BY e.emp_id DESC"
      
        
        count_query = "select count(*) from (" + query + ") as total"
        count_values =values.copy()
        count_cursor=conn.cursor()
        count_cursor.execute(count_query,tuple(count_values))
        total_count= count_cursor.fetchone()[0]

        

        data_cursor=conn.cursor()
        data_cursor.execute(query,tuple(values))
        result= data_cursor.fetchall()

             

        st.markdown("---")

  

        if result:
            df =pd.DataFrame(
                result,columns=["emp_id","emp_name","phone","email","address","job_id","job_title","base_salary",
                                "branch_id","branch_name","status"]
            )  

            final_cols = [all_columns[col] for col in selected_columns]
            df = df[final_cols]

            if null_filter == "Blank/Null Records":
                    mask=False
                    for col in final_cols:
                        mask=mask | df[col].isna() | (df[col].astype(str).str.strip()== "")
                    df=df[mask]    


                
           
            df.insert(0,"S.no",range(1,len(df)+1))  

            for col in ["base_salary"]:
                if col in df.columns:
                    df[col]= df[col].apply(lambda x:f"₹ {x}")

            st.dataframe(df,use_container_width=True)

            st.markdown(
                f"<div style='text-align:right; font-size:13px; color:gray;'>"
                f"Total employees found: <b>{total_count}</b></div>",
                unsafe_allow_html=True)

            
            st.markdown("### export report") 
            csv= df.to_csv(index=False).encode("utf-8")
            st.download_button(label="Download CSV",data=csv,file_name="employee_report.csv",mime="text/csv")

            
        else:
            st.info("No data found")






# ======================================================================================================================= #
#                                      3. SALARY MANAGMENT PAGE                                                                
# ======================================================================================================================= #


elif page == "Salary management":
    st.title("Salary management")

    tab1,tab2,tab3=st.tabs([
        "Employee salary managment",
        "Job salary policy","Salary report"
        
    ])
  
    conn= mysql.connector.connect(host="localhost",user="shiv",password="1234",database="emp_db")
    
    


    
    with tab1:
        st.subheader("Manage Employee Salary")
        emp_cursor =conn.cursor()
        emp_cursor.execute(""" select  e.emp_id, e.emp_name,
                                j.base_salary from employees e 
                                join jobs j on e.job_id = j.job_id""")

        current_year= datetime.now().year
        selected_year= st.selectbox("select year",options=[current_year-1,current_year,current_year+1])
        month_dict= {"January": 1, "February": 2, "March": 3,
                "April": 4, "May": 5, "June": 6,
                "July": 7, "August": 8, "September": 9,
                "October": 10, "November": 11, "December": 12}
        
        selected_month_name= st.selectbox("select month ",options=list(month_dict.keys()))
        selected_month= month_dict[selected_month_name]
        month_year= f"{selected_year}-{selected_month:02d}"

        employees = emp_cursor.fetchall()
        emp_dict = {f"{e[0]}-{e[1]}":(e[0],e[2]) for e in employees}
        emp_list =list(emp_dict.keys())
        selected_emp= st.selectbox("Salect Employee",emp_list)
        emp_id,base_salary=emp_dict[selected_emp]

        base_salary= base_salary or 0
        st.info(f"current salary: ₹{base_salary}")

        bonus= st.number_input("month incentive / bonus",min_value=0,step=500)
        
        leave_days= st.number_input("leave days (0.5 = half day)",min_value=0.0,step=0.5,format="%.1f")
        daily_salary =base_salary/30 
        salary_deduction= daily_salary * leave_days
        final_salary= base_salary + bonus - salary_deduction
        st.warning(f"""
                    Salary Breakdown:
                    |• Bonus: ₹{int(bonus)}
                    |• Leave Deduction: ₹{int(salary_deduction)}
                    |➡ Final Salary: ₹{int(final_salary)}
                                    """)
        
        if st.button("save monthly salary"):
            cursor=conn.cursor()
            cursor.execute( """
                    INSERT INTO employee_salary_log
                    (emp_id, month_year, base_salary, bonus, leave_days, deduction, final_salary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,(emp_id,month_year,base_salary,bonus,leave_days,int(salary_deduction),int(final_salary)))
            conn.commit()
            st.success("Leave impact applied to salary")





# ---------------------------------------------------------------------------------------------------



    with tab2:
        st.subheader("Change job base salary")

        job_cursor=conn.cursor()
        job_cursor.execute("Select job_id, job_title, base_salary from jobs where status='Active'")
        jobs= job_cursor.fetchall()
        job_dict={j[1]:(j[0],j[2]) for j in jobs}
        job_names = list(job_dict.keys())

        selected_job= st.selectbox("select the job",job_names)
        job_id,current_salary = job_dict[selected_job]
        st.info(f"Current base Salary:₹{current_salary}")

        new_salary = st.number_input("New base salary",min_value=0,value=int(current_salary),
                                    step=1000)
        if st.button("Update job salary"):
            update_cursor= conn.cursor()
            update_cursor.execute("update jobs set base_salary=%s where job_id=%s",(new_salary,job_id))
            conn.commit()
            st.success("job base salary updated succesfully")

 

    with tab3 :
        st.subheader("Monthly salary report")

        current_year= datetime.now().year

        col1,col2,col3,col4=st.columns(4)
        with col1:
           year= st.selectbox("Select year",options=[current_year-1,current_year,current_year+1])

        
        month_dict= {"January": 1, "February": 2, "March": 3,
                "April": 4, "May": 5, "June": 6,
                "July": 7, "August": 8, "September": 9,
                "October": 10, "November": 11, "December": 12}
        with col2:
            selected_month_name=st.selectbox("Select month",options=(month_dict.keys()))
        
        selected_month= month_dict[selected_month_name]
        month_year= f"{year}-{selected_month:02d}"


        job_cursor=conn.cursor()
        job_cursor.execute("select job_id, job_title from jobs where status='Active'")
        jobs=job_cursor.fetchall()
        job_dict={j[1]: j[0] for j in jobs}
        job_list=["All"] +list(job_dict.keys())
        with col3:
           selected_job= st.selectbox("select job",job_list)

        branch_cursor=conn.cursor()
        branch_cursor.execute("select branch_id, branch_name from branches where status='Active'")
        branches= branch_cursor.fetchall()
        branch_dict={b[1]:b[0] for b in branches}
        branch_list=["All"]+list(branch_dict.keys())
        with col4:
           selected_branch= st.selectbox("select branch",branch_list)
        


        st.markdown("---")
        st.subheader("select columns")

        all_columns={
        "Employee ID": "emp_id",
        "Employee Name": "emp_name",
        "Job": "job_title",
        "Branch": "branch_name",
        "Month": "month_year",
        "Base Salary": "base_salary",
        "Bonus": "bonus",
        "Leave Days": "leave_days",
        "Deduction": "deduction",
        "Final Salary": "final_salary"
                                        }
        
        selected_columns=st.multiselect("choose columns",options=list(all_columns.keys()),
                                        default=["Employee ID",'Employee Name','Month','Leave Days','Final Salary'])
        if not selected_columns:
            st.info("Please select at least one column to view reoprt")
            st.stop()





        query=""" select 
        e.emp_id,
        e.emp_name,
        j.job_title,
        b.branch_name,
        s.month_year,
        s.base_salary,
        s.bonus,
        s.leave_days,
        s.deduction,
        s.final_salary
        
                    from employee_salary_log s join employees e on s.emp_id = e.emp_id
                    join jobs j on e.job_id=j.job_id
                    join branches b on e.branch_id= b.branch_id where s.month_year =%s"""
        values=[month_year]

        if selected_job != "All":
            query+=" And j.job_id = %s"
            values.append(job_dict[selected_job])
        if selected_branch !="All":
            query+=" And b.branch_id=%s" 
            values.append(branch_dict[selected_branch])

        cursor=conn.cursor()
        cursor.execute(query,tuple(values)) 
        result= cursor.fetchall()


        if result:
            df=pd.DataFrame(result,columns=["emp_id","emp_name","job_title","branch_name","month_year",
                                            "base_salary","bonus","leave_days","deduction","final_salary"])
            final_cols=[all_columns[col] for col in selected_columns]
            df=df[final_cols]

            for col in ["base_salary",'bonus','deduction','final_salary']:
                if col in df.columns:
                    df[col]= df[col].apply(lambda x:f"₹ {x}")

            st.dataframe(df,use_container_width=True)

            csv=df.to_csv(index=False).encode("utf-8")
            st.download_button(label="Download monthly salary report(csv)",data=csv,
                        file_name=f"monthly_salary_report_{month_year}.csv",mime='text/csv')
        else:
            st.info("no salary data found for selected filters")



             


        












     
  







