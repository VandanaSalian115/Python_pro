import csv
import sqlite3
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#DATABASE MANAGER CLASS
class DatabaseManager:
    def __init__(self,db_name="credit_calculator.db"):
        self.db_name=db_name
        self.conn=sqlite3.connect(self.db_name)
        self.cursor=self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""DROP TABLE IF EXISTS credit_accounts;""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit_accounts
            (account_number TEXT PRIMARY KEY,
            name TEXT,
            credit_limit REAL,
            amount_used REAL,
            unused_credit REAL,
            balance REAL,
            last_updated TEXT)""")
        self.conn.commit()

    def insert_or_update(self,account_number,name,credit_limit,amount_used ):
        unused_credit=credit_limit-amount_used
        balance=amount_used+unused_credit
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        #to check if the account exists
        self.cursor.execute('SELECT * FROM credit_accounts WHERE account_number=?',(account_number,))
        data=self.cursor.fetchone()

        if data:
            self.cursor.execute("""
                UPDATE credit_accounts SET name=?,credit_limit=?,amount_used=?,
                unused_credit=?,balance=?,last_updated=?WHERE account_number=?
                """,(name,credit_limit,amount_used,unused_credit,balance,last_updated,
                account_number))
        else:
            self.cursor.execute("""
            INSERT INTO credit_accounts(account_number,name,credit_limit,amount_used,
            unused_credit,balance,last_updated)VALUES(?,?,?,?,?,?,?)""",(account_number,name,credit_limit,
            amount_used,unused_credit,balance,last_updated))
        self.conn.commit()
        self.write_to_csv(account_number,name,credit_limit,amount_used,unused_credit,balance,last_updated)

    def fetch_account(self,account_number):
        self.cursor.execute('SELECT * FROM credit_accounts WHERE account_number=?',(account_number,))
        return self.cursor.fetchone()
    def write_to_csv(self,account_number,name,credit_limit,amount_used,unused_credit,balance,last_updated):
        with open("credit_accounts.csv",mode="a",newline="") as file:
            writer=csv.writer(file)
            writer.writerow([account_number,name,credit_limit,amount_used,unused_credit,balance,last_updated])

    def read_from_csv(self):
        accounts=[]
        try:
            with open("credit_accounts.csv",mode="r") as file:
                reader= csv.reader(file)
                for row in reader:
                    accounts.append(row)
        except FileNotFoundError:
            return []
        return accounts

#-INTEREST CALCULATOR CLASS-
class InterestCalculator:
    def __init__(self,annual_used_rate=0.01,annual_unused_rate=0.0025):
        self.annual_used_rate=annual_used_rate
        self.annual_unused_rate=annual_unused_rate

       #CONVERT ANNUAL INTEREST RATE TO DAILY RATE
    def calculate_daily_interest(self,amount,is_used=True):
        daily_rate=self.annual_used_rate/365 if is_used else self.annual_unused_rate/365
        daily_interest=amount*daily_rate
        return daily_interest

#-GRAPH PLOTTER CLASS-
class GraphPlotter:
    @staticmethod
    def plot_balance(used_credit,unused_credit):
        #PLOTTING USED VS UNUSED CREDIT
       labels=['Used Credit','Unused Credit']
       sizes=[used_credit, unused_credit]
       fig, ax = plt.subplots()
       ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
       ax.axis('equal')
       plt.title("Credit Usage Distribution")
       plt.show()

#-CREDIT ACCOUNT CLASS-
class CreditAccount:
    def __init__(self, account_number, name, credit_limit, amount_used):
        self.account_number=account_number
        self.name=name
        self.credit_limit=credit_limit
        self.amount_used=amount_used
        self.unused_credit=credit_limit-amount_used
        self.balance=amount_used + self.unused_credit
        self.last_updated=datetime.now().strftime('%Y-%m-%d  %H:%M:%S')

    def update_balance(self, new_amount_used):
        self.amount_used=new_amount_used
        self.unused_credit=self.credit_limit-new_amount_used
        self.balance=self.amount_used + self.unused_credit

#-CREDIT CALCULATOR APPLICATION CLASS-
class CreditCalculatorApp:
    def __init__(self,master):
        self.master  = master
        self.master.title("Line of Credit Calculator")

        #Initialize classes
        self.db_manager=DatabaseManager()
        self.interest_calculator=InterestCalculator()

        #UI components
        self.create_widgets()

    def create_widgets(self):
        #Labels and entry field for account details
        self.label_account_number=tk.Label(self.master,text="Account Number")
        self.label_account_number.grid(row=0,column=0)
        self.entry_account_number=tk.Entry(self.master)
        self.entry_account_number.grid(row=0,column=1)

        self.label_name=tk.Label(self.master,text="Name")
        self.label_name.grid(row=1,column=0)
        self.entry_name=tk.Entry(self.master)
        self.entry_name.grid(row=1,column=1)

        self.label_credit_limit=tk.Label(self.master,text="Credit Limit")
        self.label_credit_limit.grid(row=2,column=0)
        self.entry_credit_limit=tk.Entry(self.master)
        self.entry_credit_limit.grid(row=2,column=1)

        self.label_amount_used=tk.Label(self.master,text="Amount Used")
        self.label_amount_used.grid(row=3,column=0)
        self.entry_amount_used=tk.Entry(self.master)
        self.entry_amount_used.grid(row=3,column=1)

        #Calculate Button
        self.button_calculate=tk.Button(self.master,text="Calculate",command=self.calculate)
        self.button_calculate.grid(row=4,column=0,columnspan=2)

        #Graph Button
        self.button_graph=tk.Button(self.master,text="Show Graph",command=self.show_graph)
        self.button_graph.grid(row=5,column=0,columnspan=2)

        #Account View Button
        self.button_view_account=tk.Button(self.master,text="View Account", command=self.view_account)
        self.button_view_account.grid(row=6,column=0,columnspan=2)

        #Account Details Display Label
        self.label_account_details=tk.Label(self.master,text="")
        self.label_account_details.grid(row=7,column=0,columnspan=2)

        #View CSV File Button
        self.button_view_csv=tk.Button(self.master,text="View All Accounts",command=self.view_all_accounts)
        self.button_view_csv.grid(row=8,column=0,columnspan=2)

    def calculate(self):
        try:
            #Gathering Inputs
           account_number=self.entry_account_number.get()
           name=self.entry_name.get()
           credit_limit=float(self.entry_credit_limit.get())
           amount_used=float(self.entry_amount_used.get())

           if credit_limit<amount_used:
              raise ValueError("Amount used cannot exceed the credit limit.")

           #CreditAccount object
           account=CreditAccount(account_number,name,credit_limit,amount_used)

           #Updating Database with new data
           self.db_manager.insert_or_update(account_number,name,credit_limit,amount_used)

           messagebox.showinfo("Success","Credit details updated successfully!")
        except ValueError as e:
            messagebox.showerror("Input Error",str(e))

    def show_graph(self):
        #Fetching Account details from Database
        account_number=self.entry_account_number.get()
        account_data=self.db_manager.fetch_account(account_number)

        if account_data:
          #Extracting used and unused credit
          used_credit=account_data[3]
          unused_credit=account_data[4]

          #Plotting the graph
          GraphPlotter.plot_balance(used_credit,unused_credit)
        else:
          messagebox.showerror("Account Not Found","Account Number not found in Database.")

    def view_account(self):
       account_number=self.entry_account_number.get() #for fetching account number from input.
       account_data=self.db_manager.fetch_account(account_number) #for fetching account details from database.

       if account_data:

           account_number=account_data[0]
           name=account_data[1]
           credit_limit=account_data[2]
           amount_used=account_data[3]
           unused_credit=account_data[4]
           balance=account_data[5]
           last_updated=account_data[6]

           used_interest=self.interest_calculator.calculate_daily_interest(amount_used, is_used=True)
           unused_interest=self.interest_calculator.calculate_daily_interest(unused_credit, is_used=False)

           account_details=f"Account Number: {account_number}\n"\
                           f"Name:{name}\n" \
                           f"Credit Limit: {credit_limit}\n" \
                           f"Amount Used: {amount_used}\n" \
                           f"Unused Credit: {unused_credit}\n" \
                           f"Balance: {balance}\n" \
                           f"Last Updated: {last_updated}\n\n"\
                           f"Daily Interest (Used Credit):{used_interest:.2f}\n"\
                           f"Daily Interest (Unused Credit):{unused_interest:.2f}"

           #displaying account details in label
           self.label_account_details.config(text=account_details)
       else:
           messagebox.showerror("Account Not Found!","Account Number is not found in Database.")
            
    def view_all_accounts(self):
        accounts=self.db_manager.read_from_csv()
        if accounts:
            account_str="\n".join([", ".join(account)for account in accounts])
            messagebox.showinfo("All Accounts", account_str)
        else:
            messagebox.showinfo("No Accounts","No accounts found in the CSV.")
 #__Application Run__
if __name__=="__main__":
    root=tk.Tk()
    app=CreditCalculatorApp(root)
    root.mainloop()
