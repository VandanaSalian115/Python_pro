#Vandana #BMI CALCULATOR
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

from bmi_2_calc import entry_name, graph_frame

BMI_CATEGORIES={  "Severely Underweight":(0,16),
"Underweight":(16,18.5),
"Normal":(18.5,25),
"Overweight" :(25,30),
"Obese": (30,35),
"Severely Obese":(35,float('inf'))
                  }
def calculate_bmi(weight,height):
    try:
       bmi = weight / (height * height)
       return round(bmi,2)
    except ZeroDivisionError:
        return 0

def validate_input(name,age,height,weight):
    try:
        age=int(age)
        weight=float(weight)
        height=float(height)
        if not name or age<=0 or height<=0 or weight<=0:
            raise ValueError
        return name,age,height,weight
    except ValueError:
        messagebox.showerror('Invalid Input','Please enter valid values for name,age,height and weight.')
        return None
def save_data_to_file(name,age,height,weight,bmi,category):
    with open("bmi_data.csv",'a',newline='') as file:
        writer=csv.writer(file)
        writer.writerrow([name,age,height,weight,bmi,category])
def show_bmi_result():

    name=entry_name.get()
    age=entry_age.get()
    height = entry_height.get()
    weight = entry_weight.get()

    valid_data=validate_input(name, age, height, weight)
    if not valid_data:
        return

    name,age,height,weight=valid_data

    bmi=calculate_bmi(weight,height)
    category=get_bmi_category(bmi)

    save_data_to_file(name,age,height,weight,bmi,category)

    result_label.config(text=f"BMI: {bmi}\nCategory: {category}")

def show_graph():
    categories_count={"Severely Underweight":0,"Underweight":0,"Normal":0,"Overweight":0,"Severely Overweight":0,"Obese":0}

    try:
        with open("bmi_data.csv","r")as file:
            for row in reader:
                category=row(7)
                if category in categories_count:
                    categories_count[category] +=1
    except FileNotFoundError:
        messagebox.showerror("No Data","No Data has been saved yet.")
        return

    labels= categories_count.keys()
    sizes= categories_count.values()

    fig, ax= plt.subplots()
    ax.pie(sizes,labels=labels,autopct='%1.1f%%',startangle=90,colors=['Purple','Blue','Green','Pink','Orange','Red'])
    ax.axis('equal')

    canvas= FigureCanvasTkAgg(fig,master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH,expand=True)

root=tk.Tk()
root.title("BMI Calculator")
