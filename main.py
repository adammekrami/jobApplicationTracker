#!/usr/bin/env python3
"""
main.py - Job Application Tracker Main Interface

This is the main entry point for the job application tracker.
It handles user interaction, input validation, and calls the appropriate
database functions from db.py.
"""

from datetime import datetime
from tabulate import tabulate
from typing import List
from db import (
    add_application,
    get_all_applications, 
    get_application_by_id,
    update_application_status,
    delete_application,
    search_applications_by_company,
    get_statistics
) 
from models import Application

"""
Display the main menu options.
"""
def display_menu():
   
    print("\n" + "="*60)
    print("🎯 JOB APPLICATION TRACKER - DATABASE VERSION")
    print("="*60)
    print("1. Add new application")
    print("2. View all applications")
    print("3. Update application status")
    print("4. Delete application")
    print("5. Search by company")
    print("6. View statistics")
    print("7. Exit")
    print("-"*60)

"""
Get user input with basic validation.
Args: prompt (str): The input prompt to display
      allow_empty (bool): Whether to allow empty input
Returns: str: Valid user input
"""
def get_valid_input(prompt: str, allow_empty: bool = False) -> str:
   
    while True:
        user_input = input(prompt).strip()
        if user_input or allow_empty:
            return user_input
        print("❌ This field cannot be empty. Please try again.")

"""
Get a valid date from user input.
Args: prompt (str): The input prompt to display
      allow_empty (bool): Whether to allow empty input (defaults to today)
Returns: datetime: Valid datetime object
"""
def get_valid_date(prompt: str, allow_empty: bool = True) -> datetime:
    
    while True:
        date_input = input(prompt).strip()
        if not date_input and allow_empty:
            return datetime.now()
        
        try:
            # Try to parse the date
            return datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format! Please use YYYY-MM-DD format.")

"""
Get a valid integer from user input. 
Args: prompt (str): The input prompt to display
Returns: int: Valid integer
"""
def get_valid_integer(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("❌ Please enter a valid number.")

"""
Format and display applications in a table using tabulate.
Args: applications (List[Application]): List of application objects
"""
def format_applications_table(applications: List[Application]) -> None:
    
    if not applications:
        print("\n📭 No applications found.")
        return
    
    table_data = []
    headers = ["ID", "Company", "Position", "Date Applied", "Status", "Last Updated"]
    
    for app in applications: 
        # Formats dates for display
        date_applied = app.date_applied.strftime("%Y-%m-%d") if app.date_applied else "N/A"
        last_updated = app.last_updated.strftime("%Y-%m-%d %H:%M") if app.last_updated else "N/A"
        
        table_data.append([
            app.id,
            app.company_name,
            app.position_title,
            date_applied,
            app.status,
            last_updated
        ])
    
    print(f"\n--- Applications ({len(applications)} found) ---")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

"""
Handle the process of adding a new job application.
Collects user input and calls the database function.
"""
def handle_add_application():
    print("\n--- Add New Application ---")
    
    #Get info
    company = get_valid_input("Company name: ")
    position = get_valid_input("Position title: ")
    
    print("Date applied (press Enter for today):")
    date_applied = get_valid_date("Date (YYYY-MM-DD): ")
    
    print("\nAvailable statuses: Applied, Interviewing, Phone Screen, Final Round, Offer, Rejected, Withdrawn")
    status = get_valid_input("Status (press Enter for 'Applied'): ", allow_empty=True)
    if not status:
        status = "Applied"
    
    #Add to database
    success = add_application(
        company_name=company,
        position_title=position,
        date_applied=date_applied,
        status=status
    )
    
    if success:
        print("🎉 Application added successfully!")
    else:
        print("❌ Failed to add application. Please try again.")

"""
Handle viewing all applications.
Retrieves data from database and displays in formatted table.
"""
def handle_view_applications():
   
    print("\n--- All Applications ---")
    applications = get_all_applications()
    format_applications_table(applications)

"""
Handle updating an application's status.
Shows current applications, gets user selection, and updates.
"""
def handle_update_status():
    print("\n--- Update Application Status ---")
    
    #Show current apps
    applications = get_all_applications()
    format_applications_table(applications)
    if not applications:
        return
    
    #Get ID and check validity
    app_id = get_valid_integer("\nEnter application ID to update: ")
    application = get_application_by_id(app_id)
    if not application:
        print(f"❌ No application found with ID: {app_id}")
        return
    
    # Show and get status
    print(f"\nCurrent status for {application.company_name} - {application.position_title}: {application.status}")
    print("\nAvailable statuses:")
    statuses = ["Applied", "Interviewing", "Phone Screen", "Final Round", "Offer", "Rejected", "Withdrawn"]
    for i, status in enumerate(statuses, 1):
        print(f"  {i}. {status}")
    print("  Or type a custom status")
    new_status = get_valid_input("New status: ")
    
    #Convert # to status
    if new_status.isdigit() and 1 <= int(new_status) <= len(statuses):
        new_status = statuses[int(new_status) - 1]
    
    success = update_application_status(app_id, new_status)
    if success:
        print("🎉 Status updated successfully!")
    else:
        print("❌ Failed to update status. Please try again.")

"""
Handle deleting an application.
Shows current applications, gets user selection, and confirms deletion.
"""
def handle_delete_application():
    print("\n--- Delete Application ---")

    #Print apps
    applications = get_all_applications()
    format_applications_table(applications)
    if not applications:
        return
    
    #Get ID and check validity
    app_id = get_valid_integer("\nEnter application ID to delete: ")
    application = get_application_by_id(app_id)
    if not application:
        print(f"❌ No application found with ID: {app_id}")
        return
    
    # Show app details to confirm
    print(f"\nApplication to delete:")
    print(f"  Company: {application.company_name}")
    print(f"  Position: {application.position_title}")
    print(f"  Status: {application.status}")
    confirm = input("\nAre you sure you want to delete this application? (y/N): ").lower()
    
    if confirm in ['y', 'yes']:
        success = delete_application(app_id)
        if success:
            print("🎉 Application deleted successfully!")
        else:
            print("❌ Failed to delete application. Please try again.")
    else:
        print("✅ Deletion cancelled.")

"""
Handle searching applications by company name.
Performs case-insensitive partial matching.
"""
def handle_search_by_company():
    print("\n--- Search by Company ---")
    company_search = get_valid_input("Enter company name to search for: ")
    applications = search_applications_by_company(company_search)
    
    if applications:
        print(f"\n🔍 Found {len(applications)} applications for companies matching '{company_search}':")
        format_applications_table(applications)
    else:
        print(f"📭 No applications found for companies matching '{company_search}'.")

"""
Handle displaying application statistics.
Shows summary information about all applications.
"""
def handle_view_statistics():
    print("\n--- Application Statistics ---")
    stats = get_statistics()
    
    if not stats:
        print("❌ Unable to retrieve statistics.")
        return
    
    print(f"\n📊 Total Applications: {stats.get('total_applications', 0)}")
    
    #Table for breakdown
    status_breakdown = stats.get('status_breakdown', {})
    if status_breakdown:
        print("\n📈 Status Breakdown:")
        table_data = [[status, count] for status, count in status_breakdown.items()]
        print(tabulate(table_data, headers=["Status", "Count"], tablefmt="grid"))
    
    #Apps in last 30 days
    applications = get_all_applications()
    if applications:
        recent_applications = [app for app in applications if app.date_applied and 
                             (datetime.now() - app.date_applied).days <= 30]
        print(f"\n📅 Applications in last 30 days: {len(recent_applications)}")

'''
Displays menu, processes user choices, and calls appropriate handlers.
'''
def main():
    print("🎯 Welcome to the Job Application Tracker!")
    print("📊 Database version with SQLAlchemy ORM")
    
    while True:
        try:
            display_menu()
            choice = input("Select an option (1-7): ").strip()
            
            if choice == '1':
                handle_add_application()
            elif choice == '2':
                handle_view_applications()
            elif choice == '3':
                handle_update_status()
            elif choice == '4':
                handle_delete_application()
            elif choice == '5':
                handle_search_by_company()
            elif choice == '6':
                handle_view_statistics()
            elif choice == '7':
                print("\n👋 Thank you for using Job Application Tracker!")
                print("🍀 Good luck with your job search!")
                break
            else:
                print("❌ Invalid option! Please choose 1-7.")
            
            input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()