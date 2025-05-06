import mysql.connector
import random

# Function to create a new user and store their information in the database
def new_user():
    print("Welcome! Please provide the following details to register:")
    user_id = input("Enter your user ID: ")
    phone_number = input("Enter your phone number: ")
    passkey = input("Create a passkey: ")

    # Insert user information into the database
    cursor.execute("INSERT INTO users (user_id, phone_number, passkey) VALUES (%s, %s, %s)", (user_id, phone_number, passkey))
    conn.commit()
    print("Registration successful! You can now log in.")

# Function to log in an existing user
def existing_user():
    print("Welcome back! Please log in with your credentials.")
    user_id = input("Enter your user ID: ")
    passkey = input("Enter your passkey: ")

    # Check if user ID and passkey match records in the database
    cursor.execute("SELECT * FROM users WHERE user_id=%s AND passkey=%s", (user_id, passkey))
    user = cursor.fetchone()
    if user:
        print("Login successful! You can proceed with banking transactions.")
        return True
    else:
        print("Invalid user ID or passkey. Please try again.")
        return False

# Function to generate OTP for payments
def generate_otp():
    otp = random.randint(100000, 999999)
    return otp

# Main function
def main():
    # Connect to MySQL database
    global conn, cursor
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="banking_system"
    )
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (user_id VARCHAR(50) PRIMARY KEY,
                    phone_number VARCHAR(15),
                    passkey VARCHAR(50))''')
    
    # Display options for new or existing user
    print("Welcome to the Banking System!")
    print("Select an option:")
    print("1. New user")
    print("2. Existing user")
    option = input("Enter your choice: ")

    if option == '1':
        new_user()
    elif option == '2':
        if existing_user():
            # Simulate a payment process with OTP generation
            print("Initiating payment process...")
            amount = float(input("Enter the amount to be paid: "))
            print("Payment amount:", amount)
            otp = generate_otp()
            print("OTP for transaction:", otp)
            user_otp = int(input("Enter OTP received on your registered phone: "))
            if user_otp == otp:
                print("Payment successful!")
            else:
                print("Invalid OTP. Payment failed.")
    else:
        print("Invalid option. Please select either '1' or '2'.")

    # Close database connection
    conn.close()

# Entry point of the program
if __name__ == "__main__":
    main()