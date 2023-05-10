import mysql.connector
from tkinter import *
from tkinter import ttk


# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Kiran@2505",
  database="rrs",
  auth_plugin='mysql_native_password'
)


# Define function to retrieve booked trains by passenger name
def get_booked_trains(first_name, last_name):
    mycursor = mydb.cursor()
    query = f"select t.train_name from train t join booked b on b.train_number = t.train_number join passenger p on p.ssn = b.passanger_ssn where p.first_name = '{first_name}' and p.last_name = '{last_name}'"
    mycursor.execute(query)
    results = mycursor.fetchall()
    booked_trains = [result[0] for result in results]
    if not booked_trains:
        return "No trains found"
    return ", ".join(booked_trains)

# Define function to retrieve passengers with confirmed tickets on a given date
def get_confirmed_passengers(travel_date):
    mycursor = mydb.cursor()
    query = f"SELECT p.Last_Name, p.First_Name FROM Passenger p JOIN Booked b ON p.ssn = b.passanger_ssn join train t on t.train_number = b.train_number join train_status ts on ts.train_name = t.train_name WHERE ts.train_Date = '{travel_date}' AND b.Status = 'booked'"
    mycursor.execute(query)
    results = mycursor.fetchall()
    confirmed_passengers = [f"{result[0]} {result[1]}" for result in results]
    if not confirmed_passengers:
        return "No confirmed passengers found"
    return "\n".join(confirmed_passengers)

# Define function to retrieve passengers and train information by age range
def get_passengers_by_age(age):
    mycursor = mydb.cursor()
    query = f"SELECT t.train_number, t.train_name, t.source_station, t.destination_station, p.first_name, p.last_name, p.address, b.status FROM Passenger p JOIN Booked b ON p.ssn = b.passanger_ssn JOIN train t on t.train_number = b.train_number WHERE TIMESTAMPDIFF(YEAR, p.bdate, CURDATE()) = {age};"
    mycursor.execute(query)
    results = mycursor.fetchall()
    if not results:
        return "No passengers found in this age range"
    data = ""
    for row in results:
        data += f"\nTrain Number: {row[0]},\t Train Name: {row[1]},\t Source: {row[2]},\t Destination: {row[3]},\t Name: {row[4]} {row[5]},\t Address: {row[6]},\t Ticket Status: {row[7]}\t"
    return data

# Define function to retrieve train names with count of passengers
def get_train_passenger_count():
    mycursor = mydb.cursor()
    query = "select t.train_name, count(p.ssn) from train t join booked b on t.train_number = b.train_number join passenger p on b.Passanger_ssn = p.ssn where b.status = 'booked' GROUP BY t.train_number;"
    mycursor.execute(query)
    results = mycursor.fetchall()
    train_passenger_count = [f"{result[0]}: {result[1]}" for result in results]
    if not train_passenger_count:
        return "No trains found"
    return "\n".join(train_passenger_count)

# Define function to retrieve all passengers with confirmed status on a given train
def get_confirmed_passengers_on_train(train_name):
    mycursor = mydb.cursor()
    query = f"SELECT t.train_name,count(*) FROM passenger p JOIN booked b ON p.ssn = b.passanger_ssn JOIN train t ON b.train_number = t.train_number WHERE t.train_name = '{train_name}' AND b.status = 'booked';"
    mycursor.execute(query)
    results = mycursor.fetchall()
    passengers = []
    for result in results:
        passenger_info = f"{result[0]} {result[1]}"
        passengers.append(passenger_info)
    if not passengers:
        return "No confirmed passengers found"
    return "\n".join(passengers)

def get_cancel_train_ticket(train_name, passengers_ssn, ticket_type):
    mycursor = mydb.cursor()
    delete_query = f'''DELETE b FROM Booked b
                        JOIN Passenger p ON p.ssn = b.Passanger_ssn 
                        JOIN Train t ON b.train_number = t.train_number 
                        WHERE t.train_name = '{train_name}' AND p.ssn = '{passengers_ssn}' AND b.status = 'booked';'''
    mycursor.execute(delete_query)
    print("Record deleted")
    
    update_query = f'''UPDATE Booked b 
                        SET b.status = 'Booked'
                        where b.passanger_ssn = (select p.ssn from passenger p, train t
                        where b.passanger_ssn = p.ssn 
                        and t.train_number = b.train_number 
                        and t.train_name = '{train_name}' 
                        and b.Ticket_Type = '{ticket_type}'
                        and b.status = 'WaitL'
                        ORDER BY b.passanger_ssn) LIMIT 1;'''
    mycursor.execute(update_query)
    print("Record updated")
    
    select_query = f'''select * from booked 
                    where train_number = (select train_number 
                                            from train where train_name = '{train_name}') 
                    and status = 'booked';'''
    mycursor.execute(select_query)
    results = mycursor.fetchall()
    booked = []
    for result in results:
        booked_info = f"{result}"
        booked.append(booked_info)
    if not booked:
        return "No confirmed passengers found"
    return "\n".join(booked)

# Define function to handle the first query and display the result on the GUI
def show_booked_trains():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    booked_trains = get_booked_trains(first_name, last_name)
    result_label.config(text=f"Booked trains: {booked_trains}")

# Define function to handle the second query and display the result on the GUI
def show_confirmed_passengers():
    travel_date = travel_date_entry.get()
    confirmed_passengers = get_confirmed_passengers(travel_date)
    result_label.config(text=f"Confirmed passengers on {travel_date}:\n{confirmed_passengers}")

# Define function to handle the third query and display the result on the GUI
def show_passengers_by_age():
    age = int(age_entry.get())
    passenger_data = get_passengers_by_age(age)
    result_label.config(text=passenger_data)
    
# Define function to handle the fou query and display the result on the GUI
def show_train_passenger_count():
    train_passenger_count = get_train_passenger_count()
    result_label.config(text=f"Train passenger count:\n{train_passenger_count}")
    
# Define function to handle the third query and display the result on the GUI
def show_confirmed_passengers_on_train():
    train_name = train_name_entry.get()
    confirmed_passengers = get_confirmed_passengers_on_train(train_name)
    result_label.config(text=f"Confirmed passengers on train {train_name}:\n{confirmed_passengers}")

def show_cancel_train_ticket():
    train_name = train_name_entry.get()
    passengers = passenger_name_entry.get()
    ticket_type = ticket_type_entry.get()
    confirmed_passengers = get_cancel_train_ticket(train_name,passengers, ticket_type)
    result_label.config(text=f"Confirmed passengers on train {train_name}:\n{confirmed_passengers}")

root = Tk()
root.title("Train Booking System")
root.config(padx=20, pady=20)

# First query section
first_query_label = Label(root, text="Query 1: Find booked trains",font=("Arial", 10))
first_query_label.grid(row=0, column=0, columnspan=2, sticky=W, padx=10, pady=10)

first_name_label = Label(root, text="First Name:",font=("Arial", 10))
first_name_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
first_name_entry = Entry(root, width=30)
first_name_entry.grid(row=1, column=1, padx=5, pady=5)

last_name_label = Label(root, text="Last Name:",font=("Arial", 10))
last_name_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
last_name_entry = Entry(root, width=30)
last_name_entry.grid(row=2, column=1, padx=5, pady=5)

booked_trains_button = Button(root, text="Find Booked Trains",command = show_booked_trains)
booked_trains_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Second query section
second_query_label = Label(root, text="Query 2: Find confirmed passengers by travel date",font=("Arial", 10))
second_query_label.grid(row=4, column=0, columnspan=2, sticky=W, padx=10, pady=10)

travel_date_label = Label(root, text="Travel Date (yyyy-mm-dd):",font=("Arial", 10))
travel_date_label.grid(row=5, column=0, sticky=W, padx=5, pady=5)
travel_date_entry = Entry(root, width=30)
travel_date_entry.grid(row=5, column=1, padx=5, pady=5)

confirmed_passengers_button = Button(root, text="Find Confirmed Passengers",command = show_confirmed_passengers)
confirmed_passengers_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Third query section
third_query_label = Label(root, text="Query 3: Find passengers by age",font=("Arial", 10))
third_query_label.grid(row=7, column=0, columnspan=2, sticky=W, padx=10, pady=10)

age_label = Label(root, text="Age:",font=("Arial", 10))
age_label.grid(row=8, column=0, sticky=W, padx=5, pady=5)
age_entry = Entry(root, width=30)
age_entry.grid(row=8, column=1, padx=5, pady=5)

passengers_by_age_range_button = Button(root, text="Find Passengers by Age",command = show_passengers_by_age)
passengers_by_age_range_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

# Fourth query section
fourth_query_label = Label(root, text="Query 4: Find passenger count by train",font=("Arial", 10))
fourth_query_label.grid(row=10, column=0, columnspan=2, sticky=W, padx=10, pady=10)

train_passenger_count_button = Button(root, text="Find Passenger Count by Train",command = show_train_passenger_count)
train_passenger_count_button.grid(row=12, column=0, columnspan=2, padx=10, pady=10)

# Fifth query section
fifth_query_label = Label(root, text="Query 5: Find confirmed passengers by train",font=("Arial", 10))
fifth_query_label.grid(row=13, column=0, columnspan=2, sticky=W, padx=10, pady=10)

train_name_label = Label(root, text="Train Name:",font=("Arial", 10))
train_name_label.grid(row=14, column=0, sticky=W, padx=5, pady=5)
train_name_entry = Entry(root, width=30)
train_name_entry.grid(row=14, column=1, padx=5, pady=5)

train_passenger_count_button = Button(root, text="Find confirmed passengers by train",command = show_confirmed_passengers_on_train)
train_passenger_count_button.grid(row=15, column=0, columnspan=2, padx=10, pady=10)

# Fifth query section
sixth_query_label = Label(root, text="Query 6: Cancel and update ticket",font=("Arial", 10))
sixth_query_label.grid(row=16, column=0, columnspan=2, sticky=W, padx=10, pady=10)

train_name_label = Label(root, text="Train Name:",font=("Arial", 10))
train_name_label.grid(row=17, column=0, sticky=W, padx=5, pady=5)
train_name_entry = Entry(root, width=30)
train_name_entry.grid(row=17, column=1, padx=5, pady=5)

passenger_name_label = Label(root, text="SSN:",font=("Arial", 10))
passenger_name_label.grid(row=18, column=0, sticky=W, padx=5, pady=5)
passenger_name_entry = Entry(root, width=30)
passenger_name_entry.grid(row=18, column=1, padx=5, pady=5)

ticket_type_label = Label(root, text="Ticket Type:",font=("Arial", 10))
ticket_type_label.grid(row=19, column=0, sticky=W, padx=5, pady=5)
ticket_type_entry = Entry(root, width=30)
ticket_type_entry.grid(row=19, column=1, padx=5, pady=5)

Cancel_button = Button(root, text="Cancel Ticket",command = show_cancel_train_ticket)
Cancel_button.grid(row=20, column=0, columnspan=2, padx=10, pady=10)

# Add result label
result_label = Label(root, text="",font = ('Arial', 12))
result_label.grid(row=21, column=0, columnspan=2, padx=10, pady=10)

# Run the
root.mainloop()