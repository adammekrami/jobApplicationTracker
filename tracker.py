#!/usr/bin/env python3
"""
Job Application Tracker
A command-line tool to track job applications stored in a CSV file
"""

import csv
import os
from datetime import datetime
from tabulate import tabulate

# Global constants
CSV_FILE = "applications.csv"
CSV_HEADERS = ["id", "company_name", "position_title", "date_applied", "status"]

def initialize_csv():
    """
    If CSV file does not exist, creates it with
    proper header.
    """
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
        print(f"Created new file: {CSV_FILE}")

def get_next_id():
    """
    Finds the highest ID in the CSV file and returns the next available ID.
    This ensures each application has a unique identifier.
    """
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            max_id = 0
            for row in reader:
                if row['id'].isdigit():  # Check if ID is a valid number
                    max_id = max(max_id, int(row['id']))
            return max_id + 1
    except FileNotFoundError:
        return 1

def add_application():
    """
    Prompts user for application details and adds a new entry to the CSV.
    Uses input validation to ensure data quality.
    """
    print("\n--- Add New Application ---")
    
    # Get user input with validation
    while True:
        company = input("Company name: ").strip()
        if company:
            break
        else:
            print("Company name cannot be empty!")

    while True:
        position = input("Position title: ").strip()
        if position:
            break
        else:
            print("Position title cannot be empty!")
    
    # Date input with default to today
    while True:
        date_input = input("Date applied (YYYY-MM-DD) or press \"Enter\" for today: ").strip()
        if not date_input:
            date_applied = datetime.now().strftime("%Y-%m-%d")
            break
        else:
            try:
                # Validate date format
                datetime.strptime(date_input, "%Y-%m-%d")
                date_applied = date_input
                break
            except ValueError:
                print("Invalid date format! Please use YYYY-MM-DD")
                
    
    # Create new application record
    new_id = get_next_id()
    new_application = [new_id, company, position, date_applied, "Applied"]
    
    # Write to CSV file
    try:
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_application)
        print(f"✅ Application added successfully with ID: {new_id}")
    except Exception as e:
        print(f"Error adding application: {e}")

def view_applications():
    """
    Reads all applications from CSV and displays them in a formatted table.
    Uses tabulate library for clean presentation.
    """
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            applications = list(reader)
        
        if not applications:
            print("\n📭 No applications found.")
            return
        
        print(f"\n--- All Applications ({len(applications)} total) ---")
        
        # Convert to list of lists for tabulate
        table_data = []
        for app in applications:
            table_data.append([
                app['id'],
                app['company_name'],
                app['position_title'],
                app['date_applied'],
                app['status']
            ])
        
        # Display formatted table
        print(tabulate(table_data, headers=CSV_HEADERS, tablefmt="grid"))
        
    except FileNotFoundError:
        print("\n📭 No applications file found. Add your first application!")
    except Exception as e:
        print(f"Error reading applications: {e}")

def update_application_status():
    """
    Updates the status of an existing application by ID.
    Reads all data, modifies the specific record, and rewrites the file.
    """
    print("\n--- Update Application Status ---")
    
    # First, show current applications
    view_applications()
    
    try:
        while True:
            app_id = input("\nEnter application ID to update: ").strip()
            if app_id.isdigit():
                break
            else:
                print("Please enter a valid numeric ID!")

        
        app_id = int(app_id)
        
        # Read all applications
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            applications = list(reader)
        
        # Find the application to update
        found = False
        for app in applications:
            if int(app['id']) == app_id:
                found = True
                print(f"Current status for {app['company_name']} - {app['position_title']}: {app['status']}")
                
                # Get new status
                print("\nAvailable statuses: Applied, Interviewing, Offer, Rejected, Withdrawn")
                while True:
                    new_status = input("Enter new status: ").strip()
                    if new_status:
                        break
                    else:
                        print("Status cannot be empty!")
                
                app['status'] = new_status
                break
        
        if not found:
            print(f"No application found with ID: {app_id}")
            return
        
        # Write all applications back to file
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(applications)
        
        print(f"✅ Application {app_id} status updated to: {new_status}")
        
    except FileNotFoundError:
        print("No applications file found!")
    except Exception as e:
        print(f"Error updating application: {e}")

def delete_application():
    """
    Deletes an application by ID.
    Reads all data, filters out the target record, and rewrites the file.
    """
    print("\n--- Delete Application ---")
    
    # Show current applications
    view_applications()
    
    try:
        while True:
            app_id = input("\nEnter application ID to delete: ").strip()
            if app_id.isdigit():
                break
            else:
                print("Please enter a valid numeric ID!")
        
        app_id = int(app_id)
        
        # Read all applications
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            applications = list(reader)
        
        # Filter out the application to delete
        original_count = len(applications)
        applications = [app for app in applications if int(app['id']) != app_id]
        
        if len(applications) == original_count:
            print(f"No application found with ID: {app_id}")
            return
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete application {app_id}? (Y/N): ").lower()
        if confirm != 'y' and confirm != 'yes':
            print("Deletion cancelled.")
            return
        
        #Updates ids
        if (app_id != original_count): #If not last id
            for app in applications:
                app['id'] = int(app['id']) if int(app['id']) < app_id else int(app['id']) - 1

        # Write remaining applications back to file
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(applications)
        
        print(f"✅ Application {app_id} deleted successfully.")
        
    except FileNotFoundError:
        print("No applications file found!")
    except Exception as e:
        print(f"Error deleting application: {e}")

def display_menu():
    """
    Displays the main menu options.
    Keeps the interface clean and consistent.
    """
    print("\n" + "="*50)
    print("🎯 JOB APPLICATION TRACKER")
    print("="*50)
    print("1. Add new application")
    print("2. View all applications")
    print("3. Update application status")
    print("4. Delete application")
    print("5. Exit")
    print("-"*50)

def main():
    """
    Main program loop.
    Handles user input and calls appropriate functions.
    """
    print("Welcome to the Job Application Tracker!")
    
    # Initialize CSV file if it doesn't exist
    initialize_csv()
    
    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            add_application()
        elif choice == '2':
            view_applications()
        elif choice == '3':
            update_application_status()
        elif choice == '4':
            delete_application()
        elif choice == '5':
            print("\n👋 Thank you for using Job Application Tracker!")
            print("Good luck with your job search! 🍀")
            break
        else:
            print("❌ Invalid option! Please choose 1-5.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

# This is the standard Python idiom for running the main function
# only when the script is executed directly (not imported)
if __name__ == "__main__":
    main()