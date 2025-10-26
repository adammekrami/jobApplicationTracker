"""
models.py - Database Model Definition
This file defines the database schema using SQLAlchemy ORM. 
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

"""
Application model class that maps to the 'applications' table in the database.
Each instance of this class represents a single job application record    
Table Structure:
- id: Primary key, auto-incrementing integer
- company_name: Name of the company (required)
- position_title: Job position title (required)
- date_applied: When the application was submitted
- last_updated: When the record was last modified (auto-updated)
- status: Current status of the application
"""
class Application(Base):

    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    position_title = Column(String(200), nullable=False)
    date_applied = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(String(50), default='Applied')
    
    """
    String representation of the Application object.
    This is what gets printed when you print() an Application instance.
    Returns: str: Human-readable representation of the application
    """
    def __repr__(self):
        return (f"<Application(id={self.id}, "
                f"company='{self.company_name}', "
                f"position='{self.position_title}', "
                f"status='{self.status}')>")
    
    """
    Convert the Application object to a dictionary.
    Returns: dict: Dictionary representation of the application
    """
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'position_title': self.position_title,
            'date_applied': self.date_applied.strftime('%Y-%m-%d %H:%M:%S') if self.date_applied else None,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None,
            'status': self.status
        }