import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.connection import Base
from backend.app.models.models import Building, Classroom, Department, TimetableEntry, TimetableException, Conflict
from backend.app.services.availability_service import AvailabilityService, parse_time_to_minutes
from backend.app.services.timetable_service import TimetableService
from backend.app.services.conflict_service import ConflictService
from backend.app.schemas.schemas import SearchRoomsRequest

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed basic building & classroom
    bldg = Building(name="Academic Block A", code="BLOCK_A", total_floors=7)
    session.add(bldg)
    session.commit()

    room1 = Classroom(room_number="A-201", building_id=bldg.id, floor=2, floor_label="2nd Floor", room_type="normal_classroom", capacity=65)
    room2 = Classroom(room_number="A-203-Com Lab", building_id=bldg.id, floor=2, floor_label="2nd Floor", room_type="computer_lab", capacity=60)
    session.add_all([room1, room2])
    session.commit()

    # Add a class in A-201 from 10:00 to 11:00 on Monday
    entry1 = TimetableEntry(
        department_code="AIDS",
        semester=3,
        section="B1",
        day_of_week="Monday",
        start_time="10:00",
        end_time="11:00",
        subject_name="Object Oriented Programming",
        subject_code="ARD207",
        faculty_name="Sehgal Dr. Ruchika",
        classroom_id=room1.id,
        room_raw_text="A-201",
        is_approved=True,
        is_deleted=False
    )
    # Add another class in A-201 from 11:00 to 12:00 on Monday
    entry2 = TimetableEntry(
        department_code="AIDS",
        semester=3,
        section="B1",
        day_of_week="Monday",
        start_time="11:00",
        end_time="12:00",
        subject_name="DBMS",
        subject_code="ARD213",
        faculty_name="Aggarwal Prof. Abha",
        classroom_id=room1.id,
        room_raw_text="A-201",
        is_approved=True,
        is_deleted=False
    )
    session.add_all([entry1, entry2])
    session.commit()

    yield session
    session.close()

def test_availability_occupied(db_session):
    room = db_session.query(Classroom).filter(Classroom.room_number == "A-201").first()
    # Test time Monday 10:30 AM (inside 10:00-11:00 class)
    now_dt = datetime.datetime(2026, 8, 24, 10, 30) # Monday
    avail = AvailabilityService.get_classroom_availability(
        db=db_session,
        classroom=room,
        target_dt=now_dt,
        current_time_str="10:30",
        day_of_week="Monday",
        date_str="2026-08-24"
    )

    assert avail.status == "OCCUPIED"
    # Merged continuous occupied block 10:00-12:00
    assert avail.occupied_until == "12:00"
    assert avail.current_class is not None
    assert avail.current_class.subject == "Object Oriented Programming"

def test_availability_free(db_session):
    room = db_session.query(Classroom).filter(Classroom.room_number == "A-201").first()
    # Test time Monday 09:15 AM (before classes)
    now_dt = datetime.datetime(2026, 8, 24, 9, 15)
    avail = AvailabilityService.get_classroom_availability(
        db=db_session,
        classroom=room,
        target_dt=now_dt,
        current_time_str="09:15",
        day_of_week="Monday",
        date_str="2026-08-24"
    )

    assert avail.status == "AVAILABLE"
    assert avail.free_until == "10:00"
    assert avail.remaining_free_minutes == 45
    assert avail.next_class.start_time == "10:00"

def test_search_rooms(db_session):
    # Search for free room from 14:00 to 16:00 on Monday
    req = SearchRoomsRequest(
        day_of_week="Monday",
        start_time="14:00",
        end_time="16:00"
    )
    results = TimetableService.search_available_classrooms(
        db=db_session,
        request=req
    )
    # Both A-201 and A-203 should be free between 14:00 and 16:00
    room_numbers = [r.room_number for r in results]
    assert "A-201" in room_numbers
    assert "A-203-Com Lab" in room_numbers

def test_conflict_detection(db_session):
    room = db_session.query(Classroom).filter(Classroom.room_number == "A-201").first()
    # Add conflicting class in A-201 on Monday 10:30 - 11:30
    clash_entry = TimetableEntry(
        department_code="AIML",
        semester=3,
        section="B2",
        day_of_week="Monday",
        start_time="10:30",
        end_time="11:30",
        subject_name="AI Foundations",
        subject_code="ARM209",
        faculty_name="Different Prof",
        classroom_id=room.id,
        room_raw_text="A-201",
        is_approved=True,
        is_deleted=False
    )
    db_session.add(clash_entry)
    db_session.commit()

    conflicts = ConflictService.detect_and_record_conflicts(db_session)
    assert len(conflicts) > 0
    assert any(c.conflict_type == "ROOM_DOUBLE_BOOKING" for c in conflicts)
