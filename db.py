"""
db.py - Database Operations and CRUD Functions
This file handles all database interactions using SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Optional
import os
from models import Base, Application

"""
Database Manager class that handles all database operations.
This class encapsulates database connection and provides methods for CRUD operations.
"""
class DatabaseManager:
    
    """
    Initialize the database manager.
    Args: db_path (str): Path to the SQLite database file
    """
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        
        # Create the database engine
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Create a session factory
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        self.create_tables()
    
    """
    Create all tables defined in our models.
    This will create the 'applications' table if it doesn't already exist.
    """
    def create_tables(self):
        try:
            Base.metadata.create_all(bind=self.engine)
            print(f"Database initialized: {self.db_path}")
        except SQLAlchemyError as e:
            print(f"Error creating database tables: {e}")
    
    """
    Create and return a new database session.
    Sessions should be closed after use to free up resources.
    Returns: Session: SQLAlchemy session object
    """
    def get_session(self):
        return self.Session()
    
    """
    Add a new job application to the database.
    Args: company_name (str): Name of the company
          position_title (str): Job position title
          date_applied (datetime, optional): Date applied. Defaults to current time.
          status (str, optional): Application status. Defaults to "Applied".
    Returns: bool: True if successful, False otherwise
    """
    def add_application(self, company_name: str, position_title: str, 
                       date_applied: Optional[datetime] = None, status: str = "Applied") -> bool:
        
        session = self.get_session()
        try:
            #Create app
            new_application = Application(
                company_name=company_name,
                position_title=position_title,
                status=status
            )
            if date_applied:
                new_application.date_applied = date_applied
            
            # Add app to session
            session.add(new_application)
            session.commit()
            
            print(f"✅ Application added successfully with ID: {new_application.id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding application: {e}")
            return False
        finally:
            session.close()
    
    """
    Retrieve all job applications from the database.
    Returns: List[Application]: List of all applications, ordered by ID
    """
    def get_all_applications(self) -> List[Application]:
        session = self.get_session()
        try:
            applications = session.query(Application).order_by(Application.id).all()
            return applications
            
        except SQLAlchemyError as e:
            print(f"Error retrieving applications: {e}")
            return []
        finally:
            session.close()
    """
    Retrieve a specific application by its ID.
    Args: app_id (int): Application ID
    Returns: Optional[Application]: Application object if found, None otherwise
    """ 
    def get_application_by_id(self, app_id: int) -> Optional[Application]:
        session = self.get_session()
        try:
            application = session.query(Application).filter(Application.id == app_id).first()
            return application
            
        except SQLAlchemyError as e:
            print(f"Error retrieving application: {e}")
            return None
        finally:
            session.close()
    
    """
    Update the status of an existing application.
    Args: app_id (int): Application ID
          new_status (str): New status value
    Returns: bool: True if successful, False otherwise
    """
    def update_application_status(self, app_id: int, new_status: str) -> bool:
        session = self.get_session()
        try:
            application = session.query(Application).filter(Application.id == app_id).first()
            if application:
                application.status = new_status
                session.commit()
                print(f"✅ Application {app_id} status updated to: {new_status}")
                return True
            else:
                print(f"No application found with ID: {app_id}")
                return False
                   
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating application: {e}")
            return False
        finally:
            session.close()
    """
    Delete an application from the database.
    Args: app_id (int): Application ID
    Returns: bool: True if successful, False otherwise
    """
    def delete_application(self, app_id: int) -> bool:
        session = self.get_session()
        try:
            application = session.query(Application).filter(Application.id == app_id).first()
            if application:
                session.delete(application)
                session.commit()
                print(f"✅ Application {app_id} deleted successfully.")
                return True
            else:
                print(f"No application found with ID: {app_id}")
                return False
                
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting application: {e}")
            return False
        finally:
            session.close()
        
    """
    Search for applications by company name (case-insensitive partial match).
    Args: company_name (str): Company name to search for
    Returns: List[Application]: List of matching applications
    """
    def search_applications_by_company(self, company_name: str) -> List[Application]:
        session = self.get_session()
        try:
            applications = (session.query(Application)
                          .filter(Application.company_name.ilike(f'%{company_name}%'))
                          .order_by(Application.date_applied.desc())
                          .all())
            return applications
            
        except SQLAlchemyError as e:
            print(f"Error searching applications: {e}")
            return []
        finally:
            session.close()
    
    """
    Get basic statistics about applications.
    Returns: dict: Dictionary containing various statistics
    """
    def get_statistics(self) -> dict:  
        session = self.get_session()
        try:
            # Total count
            total_applications = session.query(Application).count()
            
            # Count by status
            from sqlalchemy import func
            status_counts = (session.query(Application.status, func.count(Application.id))
                           .group_by(Application.status)
                           .all())
            
            # Convert to dictionary
            status_dict = {status: count for status, count in status_counts}
            
            return {
                'total_applications': total_applications,
                'status_breakdown': status_dict
            }
            
        except SQLAlchemyError as e:
            print(f"Error getting statistics: {e}")
            return {}
        finally:
            session.close()

db_manager = DatabaseManager()

def add_application(company_name: str, position_title: str, 
                   date_applied: Optional[datetime] = None, status: str = "Applied") -> bool:
    return db_manager.add_application(company_name, position_title, date_applied, status)

def get_all_applications() -> List[Application]:
    return db_manager.get_all_applications()

def get_application_by_id(app_id: int) -> Optional[Application]:
    return db_manager.get_application_by_id(app_id)

def update_application_status(app_id: int, new_status: str) -> bool:
    return db_manager.update_application_status(app_id, new_status)

def delete_application(app_id: int) -> bool:
    return db_manager.delete_application(app_id)

def search_applications_by_company(company_name: str) -> List[Application]:
    return db_manager.search_applications_by_company(company_name)

def get_statistics() -> dict:
    return db_manager.get_statistics()