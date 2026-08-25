import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "BLOCK_A", "BLOCK_B", "BLOCK_C"
    description = Column(String(255), nullable=True)
    total_floors = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    classrooms = relationship("Classroom", back_populates="building", cascade="all, delete-orphan")


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. "A-201", "A-203-Com Lab"
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    floor = Column(Integer, nullable=False) # e.g. -1 for Basement, 0 for Ground, 1 for 1st Floor, etc.
    floor_label = Column(String(50), default="Ground Floor") # "Basement (AUB)", "Ground Floor", "2nd Floor", etc.
    room_type = Column(String(50), default="normal_classroom") # "normal_classroom", "lecture_theatre", "computer_lab", "robotics_lab", "hardware_lab"
    capacity = Column(Integer, default=60)
    amenities = Column(JSON, default=list) # ["Projector", "Smart Board", "Air Conditioned", "High-End PCs"]
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    building = relationship("Building", back_populates="classrooms")
    timetable_entries = relationship("TimetableEntry", back_populates="classroom")
    exceptions = relationship("TimetableException", foreign_keys="[TimetableException.classroom_id]", back_populates="classroom")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True) # "AIDS", "AIML", "AR", "IIOT"
    name = Column(String(100), nullable=False) # "Artificial Intelligence & Data Science", etc.
    description = Column(String(255), nullable=True)


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="REVIEW_REQUIRED") # "PENDING", "PROCESSING", "REVIEW_REQUIRED", "APPROVED", "REJECTED"
    parsed_records_count = Column(Integer, default=0)
    error_log = Column(Text, nullable=True)
    department_code = Column(String(50), nullable=True)
    semester = Column(Integer, nullable=True)
    academic_year = Column(String(50), default="2026-27")

    entries = relationship("TimetableEntry", back_populates="upload", cascade="all, delete-orphan")


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    department_code = Column(String(20), index=True, nullable=False) # e.g. "AIML", "AIDS", "AR", "IIOT"
    course_name = Column(String(100), nullable=True)
    semester = Column(Integer, nullable=False, index=True) # 3, 5, 7
    section = Column(String(10), nullable=False, default="B1") # "B1", "B2"
    batch = Column(String(10), nullable=True) # "A", "B", or None for whole class
    day_of_week = Column(String(20), nullable=False, index=True) # "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
    start_time = Column(String(10), nullable=False, index=True) # "09:00", "10:00", "13:00"
    end_time = Column(String(10), nullable=False, index=True) # "10:00", "11:00", "15:00"
    subject_name = Column(String(200), nullable=False)
    subject_code = Column(String(50), nullable=True) # "ARM-201", "ARD253"
    faculty_name = Column(String(150), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    room_raw_text = Column(String(100), nullable=False) # e.g. "A-201", "AUB-03-Com Lab"
    is_lab = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True) # False during review until approved
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    upload = relationship("Upload", back_populates="entries")
    classroom = relationship("Classroom", back_populates="timetable_entries")


class TimetableException(Base):
    __tablename__ = "timetable_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    exception_date = Column(String(10), nullable=False, index=True) # "YYYY-MM-DD"
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    exception_type = Column(String(50), nullable=False) # "HOLIDAY", "CANCELLED_CLASS", "EXTRA_CLASS", "ROOM_CHANGE"
    start_time = Column(String(10), nullable=True) # "09:00" (or null for full day)
    end_time = Column(String(10), nullable=True) # "17:00"
    reason = Column(String(255), nullable=True) # "Dean's Address", "Maintenance", "Guest Lecture"
    alternate_classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    classroom = relationship("Classroom", foreign_keys=[classroom_id], back_populates="exceptions")
    alternate_classroom = relationship("Classroom", foreign_keys=[alternate_classroom_id])


class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, index=True)
    conflict_type = Column(String(50), nullable=False) # "ROOM_DOUBLE_BOOKING", "FACULTY_CLASH", "DUPLICATE_ENTRY"
    description = Column(Text, nullable=False)
    entry_ids = Column(JSON, default=list) # [entry_id_1, entry_id_2]
    severity = Column(String(20), default="CRITICAL") # "CRITICAL", "WARNING"
    resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)
