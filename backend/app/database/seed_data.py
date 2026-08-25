import datetime
from sqlalchemy.orm import Session

from backend.app.models.models import (
    Building, Classroom, Department, TimetableEntry, Upload, Conflict, TimetableException
)
from backend.app.database.connection import Base, engine, SessionLocal
from backend.app.services.conflict_service import ConflictService

def seed_database(db: Session = None):
    if db is None:
        db = SessionLocal()

    # Create tables
    Base.metadata.create_all(bind=engine)

    # 1. Create Buildings
    buildings_data = [
        {"code": "BLOCK_A", "name": "Academic Block A", "description": "Main Academic Tower, Classrooms & Core Tech Labs", "total_floors": 7},
        {"code": "BLOCK_B", "name": "Academic Block B / USDI", "description": "USDI Design & Computing Center", "total_floors": 3},
        {"code": "BLOCK_C", "name": "Academic Block C", "description": "De Novo Innovation Center & Advanced Research", "total_floors": 4},
    ]

    building_map = {}
    for b_data in buildings_data:
        bldg = db.query(Building).filter(Building.code == b_data["code"]).first()
        if not bldg:
            bldg = Building(**b_data)
            db.add(bldg)
            db.commit()
            db.refresh(bldg)
        building_map[b_data["code"]] = bldg

    # 2. Create Departments
    depts_data = [
        {"code": "AIDS", "name": "Artificial Intelligence & Data Science", "description": "Department of AI & Data Science"},
        {"code": "AIML", "name": "Artificial Intelligence & Machine Learning", "description": "Department of AI & Machine Learning"},
        {"code": "AR", "name": "Automation & Robotics", "description": "Department of Automation & Robotics"},
        {"code": "IIOT", "name": "Industrial Internet of Things", "description": "Department of Industrial IoT & Smart Systems"},
    ]
    for d_data in depts_data:
        dept = db.query(Department).filter(Department.code == d_data["code"]).first()
        if not dept:
            dept = Department(**d_data)
            db.add(dept)
    db.commit()

    # 3. Create Classrooms
    classrooms_data = [
        # Block A - Basement
        {"room_number": "AUB-03-Com Lab", "building_code": "BLOCK_A", "floor": -1, "floor_label": "Basement (AUB)", "room_type": "computer_lab", "capacity": 60, "amenities": ["High-End GPU Workstations", "AC", "Smart Board", "Fiber LAN"]},
        {"room_number": "AUB-04-Com Lab", "building_code": "BLOCK_A", "floor": -1, "floor_label": "Basement (AUB)", "room_type": "computer_lab", "capacity": 60, "amenities": ["Development PCs", "AC", "Projector", "Fiber LAN"]},
        {"room_number": "AUB-06-Ele.Lab", "building_code": "BLOCK_A", "floor": -1, "floor_label": "Basement (AUB)", "room_type": "hardware_lab", "capacity": 45, "amenities": ["Oscilloscopes", "Soldering Stations", "Microcontrollers", "AC"]},
        # Block A - Ground Floor
        {"room_number": "A-004 Lec Hall", "building_code": "BLOCK_A", "floor": 0, "floor_label": "Ground Floor", "room_type": "lecture_theatre", "capacity": 120, "amenities": ["Tiered Seating", "Dual Projectors", "Acoustic System", "Central AC"]},
        {"room_number": "A-005 Lec Hall", "building_code": "BLOCK_A", "floor": 0, "floor_label": "Ground Floor", "room_type": "lecture_theatre", "capacity": 120, "amenities": ["Tiered Seating", "Smart Podium", "Surround Sound", "Central AC"]},
        {"room_number": "A-007-Com Lab", "building_code": "BLOCK_A", "floor": 0, "floor_label": "Ground Floor", "room_type": "computer_lab", "capacity": 60, "amenities": ["Linux Dev Workstations", "AC", "Smart Board", "Fiber LAN"]},
        # Block A - 1st Floor
        {"room_number": "A-103-CR", "building_code": "BLOCK_A", "floor": 1, "floor_label": "1st Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "High-Speed WiFi"]},
        {"room_number": "A-104-CR", "building_code": "BLOCK_A", "floor": 1, "floor_label": "1st Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "High-Speed WiFi"]},
        {"room_number": "A-105-CR", "building_code": "BLOCK_A", "floor": 1, "floor_label": "1st Floor", "room_type": "normal_classroom", "capacity": 70, "amenities": ["Projector", "Whiteboard", "AC", "High-Speed WiFi"]},
        {"room_number": "A-106", "building_code": "BLOCK_A", "floor": 1, "floor_label": "1st Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "High-Speed WiFi"]},
        # Block A - 2nd Floor
        {"room_number": "A-201", "building_code": "BLOCK_A", "floor": 2, "floor_label": "2nd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "High-Speed WiFi"]},
        {"room_number": "A-202", "building_code": "BLOCK_A", "floor": 2, "floor_label": "2nd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Whiteboard", "AC", "High-Speed WiFi"]},
        {"room_number": "A-203-Com Lab", "building_code": "BLOCK_A", "floor": 2, "floor_label": "2nd Floor", "room_type": "computer_lab", "capacity": 60, "amenities": ["AI/ML Computing PCs", "AC", "Smart Board", "Gigabit LAN"]},
        {"room_number": "A-204-Com Lab", "building_code": "BLOCK_A", "floor": 2, "floor_label": "2nd Floor", "room_type": "computer_lab", "capacity": 60, "amenities": ["Data Science Lab PCs", "AC", "Smart Board", "Gigabit LAN"]},
        {"room_number": "A-209-CR", "building_code": "BLOCK_A", "floor": 2, "floor_label": "2nd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Whiteboard", "AC", "High-Speed WiFi"]},
        {"room_number": "A-210-CR", "building_code": "BLOCK_A", "floor": 2, "floor_label": "2nd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "High-Speed WiFi"]},
        # Block A - 3rd Floor
        {"room_number": "A-301-Rob Lab", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "robotics_lab", "capacity": 45, "amenities": ["Robotic Arms", "PLC Test Benches", "3D Printers", "AC"]},
        {"room_number": "A-302-Material Lab", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "hardware_lab", "capacity": 40, "amenities": ["Testing Machines", "Metallurgy Kits", "AC"]},
        {"room_number": "A-303", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "normal_classroom", "capacity": 60, "amenities": ["Projector", "Smart Board", "AC"]},
        {"room_number": "A-304-Mechatronic lab", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "hardware_lab", "capacity": 45, "amenities": ["Hydraulic & Pneumatic Kits", "Sensors", "AC"]},
        {"room_number": "A-305", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "normal_classroom", "capacity": 60, "amenities": ["Projector", "Whiteboard", "AC"]},
        {"room_number": "A-306-CR", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-307-CR", "building_code": "BLOCK_A", "floor": 3, "floor_label": "3rd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        # Block A - 4th Floor
        {"room_number": "A-401 CR", "building_code": "BLOCK_A", "floor": 4, "floor_label": "4th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-402-CR", "building_code": "BLOCK_A", "floor": 4, "floor_label": "4th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-403", "building_code": "BLOCK_A", "floor": 4, "floor_label": "4th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-404-CR", "building_code": "BLOCK_A", "floor": 4, "floor_label": "4th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-405-CR", "building_code": "BLOCK_A", "floor": 4, "floor_label": "4th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-406-CR", "building_code": "BLOCK_A", "floor": 4, "floor_label": "4th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        # Block A - 5th Floor
        {"room_number": "A-507-IIOT Lab", "building_code": "BLOCK_A", "floor": 5, "floor_label": "5th Floor", "room_type": "hardware_lab", "capacity": 50, "amenities": ["IoT Gateway Racks", "Sensor Nodes", "Edge Devices", "AC"]},
        {"room_number": "A-508-CR", "building_code": "BLOCK_A", "floor": 5, "floor_label": "5th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC"]},
        # Block A - 6th Floor
        {"room_number": "A-601-CR", "building_code": "BLOCK_A", "floor": 6, "floor_label": "6th Floor", "room_type": "normal_classroom", "capacity": 70, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        {"room_number": "A-602-CR", "building_code": "BLOCK_A", "floor": 6, "floor_label": "6th Floor", "room_type": "normal_classroom", "capacity": 70, "amenities": ["Projector", "Smart Board", "AC", "WiFi"]},
        # Block A - 7th Floor
        {"room_number": "A-701", "building_code": "BLOCK_A", "floor": 7, "floor_label": "7th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC"]},
        {"room_number": "A-702-CR", "building_code": "BLOCK_A", "floor": 7, "floor_label": "7th Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC"]},
        # Block B (USDI)
        {"room_number": "B-003-Lec Hall", "building_code": "BLOCK_B", "floor": 0, "floor_label": "Ground Floor", "room_type": "lecture_theatre", "capacity": 150, "amenities": ["Auditorium Seating", "High-End AV System", "AC"]},
        {"room_number": "USDI-B-002-Comp Lab", "building_code": "BLOCK_B", "floor": 0, "floor_label": "Ground Floor", "room_type": "computer_lab", "capacity": 60, "amenities": ["Design CAD Workstations", "AC", "Smart Board"]},
        # Block C
        {"room_number": "Block C- de Novo Lab", "building_code": "BLOCK_C", "floor": 0, "floor_label": "Ground Floor", "room_type": "hardware_lab", "capacity": 50, "amenities": ["Prototyping Tools", "Rapid Fabrication", "AC"]},
        {"room_number": "C-201", "building_code": "BLOCK_C", "floor": 2, "floor_label": "2nd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC"]},
        {"room_number": "C-305", "building_code": "BLOCK_C", "floor": 3, "floor_label": "3rd Floor", "room_type": "normal_classroom", "capacity": 65, "amenities": ["Projector", "Smart Board", "AC"]},
    ]

    room_lookup = {}
    for r_data in classrooms_data:
        room = db.query(Classroom).filter(Classroom.room_number == r_data["room_number"]).first()
        b_id = building_map[r_data["building_code"]].id
        if not room:
            room = Classroom(
                room_number=r_data["room_number"],
                building_id=b_id,
                floor=r_data["floor"],
                floor_label=r_data["floor_label"],
                room_type=r_data["room_type"],
                capacity=r_data["capacity"],
                amenities=r_data["amenities"],
                is_active=True
            )
            db.add(room)
            db.commit()
            db.refresh(room)
        room_lookup[r_data["room_number"]] = room

    # Clear existing entries if any to ensure fresh full 20-page loading
    db.query(TimetableEntry).delete()
    db.query(Upload).delete()
    db.commit()

    # 4. Create Master Upload Record
    master_upload = Upload(
        filename="USAR_Odd_Semester_2026-27_Master_Timetable.pdf",
        file_path="sample_data/USAR_Timetable_2026-27.pdf",
        status="APPROVED",
        parsed_records_count=350,
        academic_year="2026-27",
        error_log=None
    )
    db.add(master_upload)
    db.commit()
    db.refresh(master_upload)

    # 5. Populate full 20-page USAR Lantiv timetable records
    raw_schedule = [
        # --- Page 1: AIDS-III_B1 ---
        ("AIDS", 3, "B1", None, "Monday", "10:00", "11:00", "Object Oriented Programming (ARD207)", "ARD207", "Sehgal Dr. Ruchika", "A-201", False),
        ("AIDS", 3, "B1", None, "Monday", "11:00", "12:00", "Database Management Systems (ARD213)", "ARD-213", "Aggarwal Prof. Abha", "A-201", False),
        ("AIDS", 3, "B1", "A", "Monday", "13:00", "15:00", "Data Structures & Algorithms Lab", "ARD253", "Dalal Dr. Renu", "A-203-Com Lab", True),
        ("AIDS", 3, "B1", "B", "Monday", "13:00", "15:00", "Computer Networks Lab", "ARD255", "Arora Dr. Amar", "AUB-03-Com Lab", True),
        ("AIDS", 3, "B1", None, "Tuesday", "11:00", "12:00", "Discrete Mathematics (ARD201)", "ARD201", "Ms. Priyanka", "A-601-CR", False),
        ("AIDS", 3, "B1", None, "Tuesday", "12:00", "13:00", "Object Oriented Programming (ARD207)", "ARD207", "Sehgal Dr. Ruchika", "A-601-CR", False),
        ("AIDS", 3, "B1", None, "Tuesday", "14:00", "15:00", "Computer Organization (ARD203)", "ARD203", "Tripathi Dr. Atul", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Tuesday", "15:00", "16:00", "Database Management Systems (ARD213)", "ARD-213", "Aggarwal Prof. Abha", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Tuesday", "16:00", "17:00", "Design and Analysis of Algorithms", "ARD-211", "Jindal Ms. Kanika", "A-406-CR", False),
        ("AIDS", 3, "B1", "A", "Wednesday", "09:00", "11:00", "Computer Networks Lab", "ARD255", "Arora Dr. Amar", "A-203-Com Lab", True),
        ("AIDS", 3, "B1", "B", "Wednesday", "09:00", "11:00", "Digital Electronics Lab", "ARD251", "Tripathi Dr. Atul", "A-007-Com Lab", True),
        ("AIDS", 3, "B1", None, "Wednesday", "11:00", "12:00", "Discrete Mathematics (ARD201)", "ARD201", "Ms. Priyanka", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Wednesday", "12:00", "13:00", "Computer Organization (ARD203)", "ARD203", "Tripathi Dr. Atul", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Wednesday", "14:00", "15:00", "Software Engineering (ARD205)", "ARD205", "Dalal Dr. Renu", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Wednesday", "15:00", "16:00", "Operating Systems (ARD209)", "ARD209", "Arora Dr. Amar", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Thursday", "11:00", "12:00", "Computer Organization (ARD203)", "ARD203", "Tripathi Dr. Atul", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Thursday", "12:00", "13:00", "Discrete Mathematics (ARD201)", "ARD201", "Ms. Priyanka", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Thursday", "14:00", "15:00", "Software Engineering (ARD205)", "ARD205", "Dalal Dr. Renu", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Thursday", "15:00", "16:00", "Operating Systems (ARD209)", "ARD209", "Arora Dr. Amar", "A-406-CR", False),
        ("AIDS", 3, "B1", None, "Thursday", "16:00", "17:00", "Design and Analysis of Algorithms", "ARD-211", "Jindal Ms. Kanika", "A-406-CR", False),
        ("AIDS", 3, "B1", "A", "Friday", "09:00", "11:00", "Digital Electronics Lab", "ARD251", "Tripathi Dr. Atul", "A-007-Com Lab", True),
        ("AIDS", 3, "B1", "B", "Friday", "09:00", "11:00", "Data Structures Lab", "ARD253", "Dalal Dr. Renu", "A-204-Com Lab", True),
        ("AIDS", 3, "B1", None, "Friday", "11:00", "12:00", "Operating Systems (ARD209)", "ARD209", "Arora Dr. Amar", "A-202", False),
        ("AIDS", 3, "B1", None, "Friday", "12:00", "13:00", "Software Engineering (ARD205)", "ARD205", "Dalal Dr. Renu", "A-202", False),
        ("AIDS", 3, "B1", None, "Friday", "14:00", "15:00", "Object Oriented Programming (ARD207)", "ARD207", "Sehgal Dr. Ruchika", "A-406-CR", False),

        # --- Page 2: AIDS-III_B2 ---
        ("AIDS", 3, "B2", "B", "Monday", "11:00", "13:00", "Data Structures Lab", "ARD253", "Kumar Mr. Anuj", "AUB-03-Com Lab", True),
        ("AIDS", 3, "B2", "A", "Monday", "11:00", "13:00", "Computer Networks Lab", "ARD255", "Arora Dr. Amar", "A-007-Com Lab", True),
        ("AIDS", 3, "B2", None, "Monday", "14:00", "15:00", "Design & Analysis of Algorithms", "ARD-211", "Jindal Ms. Kanika", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Monday", "15:00", "16:00", "Computer Organization (ARD203)", "ARD203", "Tripathi Dr. Atul", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Tuesday", "09:00", "10:00", "Computer Organization (ARD203)", "ARD203", "Tripathi Dr. Atul", "A-601-CR", False),
        ("AIDS", 3, "B2", None, "Tuesday", "10:00", "11:00", "Discrete Mathematics (ARD201)", "ARD201", "Priya Dr. Annu", "A-601-CR", False),
        ("AIDS", 3, "B2", "A", "Tuesday", "11:00", "13:00", "Digital Electronics Lab", "ARD251", "Tripathi Dr. Atul", "A-007-Com Lab", True),
        ("AIDS", 3, "B2", "B", "Tuesday", "11:00", "13:00", "Computer Networks Lab", "ARD255", "Arora Dr. Amar", "A-204-Com Lab", True),
        ("AIDS", 3, "B2", None, "Tuesday", "14:00", "15:00", "Operating Systems (ARD209)", "ARD209", "Arora Dr. Amar", "A-210-CR", False),
        ("AIDS", 3, "B2", None, "Tuesday", "15:00", "16:00", "Software Engineering (ARD205)", "ARD205", "Dalal Dr. Renu", "A-210-CR", False),
        ("AIDS", 3, "B2", None, "Wednesday", "09:00", "10:00", "Design & Analysis of Algorithms", "ARD-211", "Jindal Ms. Kanika", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Wednesday", "10:00", "11:00", "Software Engineering (ARD205)", "ARD205", "Dalal Dr. Renu", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Wednesday", "11:00", "12:00", "Discrete Mathematics (ARD201)", "ARD201", "Priya Dr. Annu", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Wednesday", "12:00", "13:00", "Object Oriented Programming (ARD207)", "ARD207", "Sehgal Dr. Ruchika", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Wednesday", "14:00", "15:00", "Operating Systems (ARD209)", "ARD209", "Arora Dr. Amar", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Wednesday", "15:00", "16:00", "Database Management Systems (ARD213)", "ARD-213", "Aggarwal Prof. Abha", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Thursday", "10:00", "11:00", "Software Engineering (ARD205)", "ARD205", "Dalal Dr. Renu", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Thursday", "11:00", "12:00", "Object Oriented Programming (ARD207)", "ARD207", "Sehgal Dr. Ruchika", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Thursday", "12:00", "13:00", "Computer Organization (ARD203)", "ARD203", "Tripathi Dr. Atul", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Thursday", "13:00", "14:00", "Database Management Systems (ARD213)", "ARD-213", "Aggarwal Prof. Abha", "A-404-CR", False),
        ("AIDS", 3, "B2", "A", "Thursday", "15:00", "17:00", "Data Structures Lab", "ARD253", "Dalal Dr. Renu", "A-204-Com Lab", True),
        ("AIDS", 3, "B2", "B", "Thursday", "15:00", "17:00", "Digital Electronics Lab", "ARD251", "Tripathi Dr. Atul", "A-007-Com Lab", True),
        ("AIDS", 3, "B2", None, "Friday", "11:00", "12:00", "Object Oriented Programming (ARD207)", "ARD207", "Sehgal Dr. Ruchika", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Friday", "12:00", "13:00", "Operating Systems (ARD209)", "ARD209", "Arora Dr. Amar", "A-404-CR", False),
        ("AIDS", 3, "B2", None, "Friday", "13:00", "14:00", "Discrete Mathematics (ARD201)", "ARD201", "Priya Dr. Annu", "A-404-CR", False),

        # --- Page 3: AIDS-V_B1 ---
        ("AIDS", 5, "B1", None, "Monday", "10:00", "11:00", "Optimization Techniques (ARO373)", "ARO373", "Singh Dr. Rohit", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Monday", "11:00", "12:00", "Pattern Recognition & Image Processing (ARD315)", "ARD315", "Dua Ms. Disha", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Monday", "12:00", "13:00", "Deep Learning & Applications (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Monday", "14:00", "15:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-103-CR", False),
        ("AIDS", 5, "B1", None, "Monday", "15:00", "17:00", "Deep Learning Lab (ARD353)", "ARD353", "Singh Dr. Sanjay", "A-204-Com Lab", True),
        ("AIDS", 5, "B1", None, "Tuesday", "10:00", "11:00", "Optimization Techniques (ARO373)", "ARO373", "Singh Dr. Rohit", "A-103-CR", False),
        ("AIDS", 5, "B1", None, "Tuesday", "11:00", "12:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-103-CR", False),
        ("AIDS", 5, "B1", None, "Tuesday", "13:00", "14:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-104-CR", False),
        ("AIDS", 5, "B1", None, "Tuesday", "14:00", "15:00", "Deep Learning & Applications (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-104-CR", False),
        ("AIDS", 5, "B1", None, "Tuesday", "15:00", "16:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-104-CR", False),
        ("AIDS", 5, "B1", None, "Tuesday", "16:00", "17:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-104-CR", False),
        ("AIDS", 5, "B1", None, "Wednesday", "10:00", "11:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-406-CR", False),
        ("AIDS", 5, "B1", None, "Wednesday", "11:00", "13:00", "Data Mining & BI Lab (ARD351)", "ARD351", "Joshi Dr. Ashish", "A-204-Com Lab", True),
        ("AIDS", 5, "B1", None, "Wednesday", "14:00", "15:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-201", False),
        ("AIDS", 5, "B1", None, "Wednesday", "15:00", "16:00", "Optimization Techniques (ARO373)", "ARO373", "Singh Dr. Rohit", "A-201", False),
        ("AIDS", 5, "B1", None, "Thursday", "10:00", "11:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Thursday", "11:00", "12:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Thursday", "13:00", "14:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Thursday", "14:00", "15:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Thursday", "15:00", "16:00", "Deep Learning & Applications (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-402-CR", False),
        ("AIDS", 5, "B1", None, "Friday", "09:00", "10:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-406-CR", False),
        ("AIDS", 5, "B1", None, "Friday", "10:00", "11:00", "Deep Learning (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-406-CR", False),
        ("AIDS", 5, "B1", None, "Friday", "11:00", "12:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-406-CR", False),

        # --- Page 4: AIDS-V_B2 ---
        ("AIDS", 5, "B2", None, "Monday", "09:00", "11:00", "Deep Learning Lab (ARD353)", "ARD353", "Singh Dr. Sanjay", "AUB-03-Com Lab", True),
        ("AIDS", 5, "B2", None, "Monday", "11:00", "12:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-702-CR", False),
        ("AIDS", 5, "B2", None, "Monday", "13:00", "14:00", "Optimization Techniques (ARO373)", "ARO373", "Singh Dr. Rohit", "A-702-CR", False),
        ("AIDS", 5, "B2", None, "Monday", "14:00", "15:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-702-CR", False),
        ("AIDS", 5, "B2", None, "Tuesday", "09:00", "10:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-402-CR", False),
        ("AIDS", 5, "B2", None, "Tuesday", "10:00", "11:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-402-CR", False),
        ("AIDS", 5, "B2", None, "Tuesday", "11:00", "12:00", "Deep Learning (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-402-CR", False),
        ("AIDS", 5, "B2", None, "Tuesday", "13:00", "14:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-402-CR", False),
        ("AIDS", 5, "B2", None, "Tuesday", "14:00", "15:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-402-CR", False),
        ("AIDS", 5, "B2", None, "Wednesday", "10:00", "11:00", "Deep Learning (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-401 CR", False),
        ("AIDS", 5, "B2", None, "Wednesday", "11:00", "12:00", "Optimization Techniques (ARO373)", "ARO373", "Singh Dr. Rohit", "A-401 CR", False),
        ("AIDS", 5, "B2", None, "Wednesday", "13:00", "14:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-702-CR", False),
        ("AIDS", 5, "B2", None, "Wednesday", "14:00", "15:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-702-CR", False),
        ("AIDS", 5, "B2", None, "Wednesday", "15:00", "16:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-405-CR", False),
        ("AIDS", 5, "B2", None, "Wednesday", "16:00", "17:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-405-CR", False),
        ("AIDS", 5, "B2", None, "Thursday", "10:00", "11:00", "Deep Learning (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-104-CR", False),
        ("AIDS", 5, "B2", None, "Thursday", "11:00", "12:00", "Optimization Techniques (ARO373)", "ARO373", "Singh Dr. Rohit", "A-104-CR", False),
        ("AIDS", 5, "B2", None, "Thursday", "13:00", "14:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-508-CR", False),
        ("AIDS", 5, "B2", None, "Thursday", "14:00", "15:00", "Pattern Recognition (ARD315)", "ARD315", "Dua Ms. Disha", "A-508-CR", False),
        ("AIDS", 5, "B2", None, "Thursday", "15:00", "16:00", "Big Data Analytics (ARD305)", "ARD305", "Singh Dr. Sanjay", "A-508-CR", False),
        ("AIDS", 5, "B2", None, "Friday", "10:00", "11:00", "Robotics & Automation (ARD301)", "ARD301", "Kalonia Ms. Ritu", "A-105-CR", False),
        ("AIDS", 5, "B2", None, "Friday", "11:00", "12:00", "Deep Learning (ARD303)", "ARD303", "Joshi Dr. Ashish", "A-105-CR", False),
        ("AIDS", 5, "B2", None, "Friday", "13:00", "15:00", "Data Mining & BI Lab (ARD351)", "ARD351", "Joshi Dr. Ashish", "A-007-Com Lab", True),

        # --- Page 5: AIDS-VII ---
        ("AIDS", 7, "B1", None, "Monday", "10:00", "11:00", "Computer Vision & Edge AI (ARD401)", "ARD401", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Monday", "11:00", "12:00", "Reinforcement Learning (ARD413)", "ARD413", "Singh Dr. Rohit", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Monday", "13:00", "14:00", "Generative AI & LLMs (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Monday", "14:00", "15:00", "Cyber Security for AI (ARD403)", "ARD403", "Pal Ms. Geetanshi", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Monday", "15:00", "16:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Tuesday", "10:00", "11:00", "Cyber Security for AI (ARD403)", "ARD403", "Pal Ms. Geetanshi", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Tuesday", "11:00", "12:00", "Computer Vision & Edge AI (ARD401)", "ARD401", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Tuesday", "12:00", "13:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Tuesday", "14:00", "15:00", "Generative AI & LLMs (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Tuesday", "15:00", "16:00", "Reinforcement Learning (ARD413)", "ARD413", "Singh Dr. Rohit", "A-004 Lec Hall", False),
        ("AIDS", 7, "B2", "B2", "Wednesday", "09:00", "11:00", "Major Project / AI Lab (ARD453)", "ARD453", "Pal Ms. Geetanshi", "AUB-03-Com Lab", True),
        ("AIDS", 7, "B1", "B1", "Wednesday", "09:00", "11:00", "Computer Vision Lab (ARD451)", "ARD451", "Jangid Dr. Manisha", "A-204-Com Lab", True),
        ("AIDS", 7, "B1", None, "Wednesday", "11:00", "12:00", "Generative AI (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Wednesday", "12:00", "13:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Wednesday", "14:00", "15:00", "Cyber Security for AI (ARD403)", "ARD403", "Pal Ms. Geetanshi", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Wednesday", "15:00", "17:00", "Social Media Analytics (ARO471)", "ARO471", "Goel Ms. Aarti", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Thursday", "10:00", "11:00", "Cyber Security for AI (ARD403)", "ARD403", "Pal Ms. Geetanshi", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Thursday", "11:00", "12:00", "Computer Vision & Edge AI (ARD401)", "ARD401", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Thursday", "13:00", "14:00", "Generative AI (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Thursday", "14:00", "15:00", "Reinforcement Learning (ARD413)", "ARD413", "Singh Dr. Rohit", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Friday", "10:00", "11:00", "Reinforcement Learning (ARD413)", "ARD413", "Singh Dr. Rohit", "A-004 Lec Hall", False),
        ("AIDS", 7, "B1", None, "Friday", "11:00", "12:00", "Computer Vision & Edge AI (ARD401)", "ARD401", "Jangid Dr. Manisha", "A-004 Lec Hall", False),
        ("AIDS", 7, "B2", "B2", "Friday", "13:00", "15:00", "Computer Vision Lab (ARD451)", "ARD451", "Jangid Dr. Manisha", "AUB-04-Com Lab", True),
        ("AIDS", 7, "B1", "B1", "Friday", "13:00", "15:00", "Major Project / AI Lab (ARD453)", "ARD453", "Pal Ms. Geetanshi", "AUB-03-Com Lab", True),
        ("AIDS", 7, "B1", None, "Friday", "15:00", "16:00", "Social Media Analytics (ARO471)", "ARO471", "Goel Ms. Aarti", "A-004 Lec Hall", False),

        # --- Page 6: AIML-III_B1 ---
        ("AIML", 3, "B1", None, "Monday", "10:00", "11:00", "Discrete Mathematics (ARM-201)", "ARM-201", "Priya Dr. Annu", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Monday", "11:00", "12:00", "Data Structures (ARM-205)", "ARM-205", "Dalal Dr. Renu", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Monday", "12:00", "13:00", "Computer Organization (ARM-203)", "ARM-203", "Singh Dr. Amrit Pal", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Monday", "14:00", "15:00", "Machine Learning Foundations (ARM-209)", "ARM-209", "Singh Mr. Neeraj", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Monday", "15:00", "16:00", "Design & Analysis of Algorithms", "ARM-211", "Jindal Ms. Kanika", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Monday", "16:00", "17:00", "Database Management Systems", "ARM-213", "Aggarwal Prof. Abha", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Tuesday", "10:00", "11:00", "Data Structures (ARM-205)", "ARM-205", "Dalal Dr. Renu", "A-209-CR", False),
        ("AIML", 3, "B1", "B", "Tuesday", "11:00", "13:00", "Data Structures Lab (ARM-253)", "ARM-253", "Kumar Dr. Ashok", "AUB-03-Com Lab", True),
        ("AIML", 3, "B1", "A", "Tuesday", "11:00", "13:00", "Machine Learning Lab (ARM-255)", "ARM-255", "Singh Mr. Neeraj", "AUB-04-Com Lab", True),
        ("AIML", 3, "B1", None, "Tuesday", "14:00", "15:00", "Computer Organization (ARM-203)", "ARM-203", "Singh Dr. Amrit Pal", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Tuesday", "15:00", "16:00", "Machine Learning Foundations (ARM-209)", "ARM-209", "Singh Mr. Neeraj", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Wednesday", "09:00", "10:00", "Object Oriented Programming (ARM-207)", "ARM-207", "Sehgal Dr. Ruchika", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Wednesday", "10:00", "11:00", "Database Management Systems", "ARM-213", "Aggarwal Prof. Abha", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Wednesday", "11:00", "12:00", "Computer Organization (ARM-203)", "ARM-203", "Singh Dr. Amrit Pal", "A-601-CR", False),
        ("AIML", 3, "B1", "A", "Wednesday", "13:00", "15:00", "Data Structures Lab (ARM-253)", "ARM-253", "Singh Dr. Abhishek", "AUB-03-Com Lab", True),
        ("AIML", 3, "B1", "B", "Wednesday", "13:00", "15:00", "Digital Electronics Lab (ARM-251)", "ARM-251", "Singh Dr. Amrit Pal", "A-203-Com Lab", True),
        ("AIML", 3, "B1", None, "Wednesday", "15:00", "16:00", "Data Structures (ARM-205)", "ARM-205", "Dalal Dr. Renu", "A-601-CR", False),
        ("AIML", 3, "B1", "A", "Thursday", "11:00", "13:00", "Digital Electronics Lab (ARM-251)", "ARM-251", "Singh Dr. Amrit Pal", "A-203-Com Lab", True),
        ("AIML", 3, "B1", "B", "Thursday", "11:00", "13:00", "Machine Learning Lab (ARM-255)", "ARM-255", "Singh Mr. Neeraj", "A-007-Com Lab", True),
        ("AIML", 3, "B1", None, "Thursday", "14:00", "15:00", "Design & Analysis of Algorithms", "ARM-211", "Jindal Ms. Kanika", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Thursday", "15:00", "16:00", "Discrete Mathematics (ARM-201)", "ARM-201", "Priya Dr. Annu", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Thursday", "16:00", "17:00", "Object Oriented Programming (ARM-207)", "ARM-207", "Sehgal Dr. Ruchika", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Friday", "11:00", "12:00", "Discrete Mathematics (ARM-201)", "ARM-201", "Priya Dr. Annu", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Friday", "12:00", "13:00", "Machine Learning Foundations (ARM-209)", "ARM-209", "Singh Mr. Neeraj", "A-601-CR", False),
        ("AIML", 3, "B1", None, "Friday", "13:00", "14:00", "Object Oriented Programming (ARM-207)", "ARM-207", "Sehgal Dr. Ruchika", "A-601-CR", False),

        # --- Page 7: AIML-III_B2 (Full Primary Schedule for Room A-602-CR!) ---
        ("AIML", 3, "B2", None, "Monday", "10:00", "11:00", "Machine Learning Foundations (ARM-209)", "ARM-209", "Singh Mr. Neeraj", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Monday", "11:00", "12:00", "Object Oriented Programming (ARM-207)", "ARM-207", "Sehgal Dr. Ruchika", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Monday", "12:00", "13:00", "Discrete Mathematics (ARM-201)", "ARM-201", "Priya Dr. Annu", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Monday", "14:00", "15:00", "Data Structures (ARM-205)", "ARM-205", "Kumar Mr. Anuj", "A-602-CR", False),
        ("AIML", 3, "B2", "B", "Monday", "15:00", "17:00", "Machine Learning Lab (ARM-255)", "ARM-255", "Singh Mr. Neeraj", "A-203-Com Lab", True),
        ("AIML", 3, "B2", "A", "Monday", "15:00", "17:00", "Digital Electronics Lab (ARM-251)", "ARM-251", "Singh Dr. Amrit Pal", "A-007-Com Lab", True),
        
        # Tuesday for AIML-III_B2 in A-602-CR
        ("AIML", 3, "B2", None, "Tuesday", "10:00", "11:00", "Computer Organization (ARM-203)", "ARM-203", "Singh Dr. Amrit Pal", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Tuesday", "11:00", "12:00", "Data Structures (ARM-205)", "ARM-205", "Kumar Mr. Anuj", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Tuesday", "13:00", "14:00", "Object Oriented Programming (ARM-207)", "ARM-207", "Sehgal Dr. Ruchika", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Tuesday", "14:00", "15:00", "Database Management Systems (ARM-213)", "ARM-213", "Aggarwal Prof. Abha", "A-602-CR", False),
        ("AIML", 3, "B2", "B", "Tuesday", "15:00", "17:00", "Digital Electronics Lab (ARM-251)", "ARM-251", "Singh Dr. Amrit Pal", "AUB-03-Com Lab", True),
        
        # Wednesday for AIML-III_B2 in A-602-CR
        ("AIML", 3, "B2", None, "Wednesday", "09:00", "10:00", "Design & Analysis of Algorithms", "ARM-211", "Jindal Ms. Kanika", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Wednesday", "10:00", "11:00", "Machine Learning Foundations (ARM-209)", "ARM-209", "Singh Mr. Neeraj", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Wednesday", "13:00", "14:00", "Data Structures (ARM-205)", "ARM-205", "Kumar Mr. Anuj", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Wednesday", "14:00", "15:00", "Object Oriented Programming (ARM-207)", "ARM-207", "Sehgal Dr. Ruchika", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Wednesday", "15:00", "16:00", "Discrete Mathematics (ARM-201)", "ARM-201", "Priya Dr. Annu", "A-602-CR", False),

        # Thursday for AIML-III_B2 in A-602-CR
        ("AIML", 3, "B2", None, "Thursday", "11:00", "12:00", "Discrete Mathematics (ARM-201)", "ARM-201", "Priya Dr. Annu", "A-602-CR", False),
        ("AIML", 3, "B2", "B", "Thursday", "12:00", "14:00", "Data Structures Lab (ARM-253)", "ARM-253", "Kumar Mr. Anuj", "A-007-Com Lab", True),
        ("AIML", 3, "B2", "A", "Thursday", "12:00", "14:00", "Machine Learning Lab (ARM-255)", "ARM-255", "Singh Mr. Neeraj", "AUB-04-Com Lab", True),
        ("AIML", 3, "B2", None, "Thursday", "14:00", "15:00", "Design & Analysis of Algorithms", "ARM-211", "Jindal Ms. Kanika", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Thursday", "15:00", "16:00", "Computer Organization (ARM-203)", "ARM-203", "Singh Dr. Amrit Pal", "A-602-CR", False),

        # Friday for AIML-III_B2 in A-602-CR
        ("AIML", 3, "B2", None, "Friday", "11:00", "12:00", "Computer Organization (ARM-203)", "ARM-203", "Singh Dr. Amrit Pal", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Friday", "12:00", "13:00", "Database Management Systems (ARM-213)", "ARM-213", "Aggarwal Prof. Abha", "A-602-CR", False),
        ("AIML", 3, "B2", None, "Friday", "14:00", "15:00", "Machine Learning Foundations (ARM-209)", "ARM-209", "Singh Mr. Neeraj", "A-602-CR", False),
        ("AIML", 3, "B2", "A", "Friday", "15:00", "17:00", "Data Structures Lab (ARM-253)", "ARM-253", "Kumar Dr. Ashok", "A-204-Com Lab", True),

        # --- Page 8: AIML-V_B1 ---
        ("AIML", 5, "B1", None, "Monday", "10:00", "11:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-405-CR", False),
        ("AIML", 5, "B1", None, "Monday", "11:00", "13:00", "AI System Design Lab (ARM351)", "ARM351", "Choudhary Dr. Amit", "AUB-04-Com Lab", True),
        ("AIML", 5, "B1", None, "Monday", "14:00", "15:00", "Pattern Recognition & Neural Nets", "ARM305", "Kumar Mr. Arun", "A-403", False),
        ("AIML", 5, "B1", None, "Monday", "15:00", "16:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-403", False),
        ("AIML", 5, "B1", None, "Monday", "16:00", "17:00", "IoT & Embedded AI (ARO 379)", "ARO 379", "Chopra Dr. Khyati", "A-403", False),
        ("AIML", 5, "B1", None, "Tuesday", "09:00", "10:00", "IoT & Embedded AI (ARO 379)", "ARO 379", "Chopra Dr. Khyati", "A-403", False),
        ("AIML", 5, "B1", None, "Tuesday", "10:00", "11:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-403", False),
        ("AIML", 5, "B1", None, "Tuesday", "12:00", "13:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-406-CR", False),
        ("AIML", 5, "B1", None, "Tuesday", "14:00", "15:00", "Pattern Recognition (ARM305)", "ARM305", "Kumar Mr. Arun", "A-403", False),
        ("AIML", 5, "B1", None, "Wednesday", "10:00", "11:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-403", False),
        ("AIML", 5, "B1", None, "Wednesday", "13:00", "14:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-403", False),
        ("AIML", 5, "B1", None, "Wednesday", "14:00", "15:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-403", False),
        ("AIML", 5, "B1", None, "Wednesday", "15:00", "16:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-403", False),
        ("AIML", 5, "B1", None, "Thursday", "10:00", "11:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-403", False),
        ("AIML", 5, "B1", None, "Thursday", "11:00", "13:00", "NLP & Deep Learning Lab (ARM353)", "ARM353", "Joshi Dr. Ashish", "AUB-03-Com Lab", True),
        ("AIML", 5, "B1", None, "Thursday", "14:00", "16:00", "Pattern Recognition (ARM305)", "ARM305", "Kumar Mr. Arun", "A-404-CR", False),
        ("AIML", 5, "B1", None, "Thursday", "16:00", "17:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-404-CR", False),
        ("AIML", 5, "B1", None, "Friday", "09:00", "10:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-403", False),
        ("AIML", 5, "B1", None, "Friday", "10:00", "11:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-403", False),
        ("AIML", 5, "B1", None, "Friday", "11:00", "12:00", "IoT & Embedded AI (ARO 379)", "ARO 379", "Chopra Dr. Khyati", "A-403", False),
        ("AIML", 5, "B1", None, "Friday", "12:00", "13:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-508-CR", False),
        ("AIML", 5, "B1", None, "Friday", "14:00", "15:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-403", False),

        # --- Page 9: AIML-V_B2 ---
        ("AIML", 5, "B2", None, "Monday", "10:00", "11:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-405-CR", False),
        ("AIML", 5, "B2", None, "Monday", "12:00", "13:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-406-CR", False),
        ("AIML", 5, "B2", None, "Monday", "14:00", "15:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-406-CR", False),
        ("AIML", 5, "B2", None, "Monday", "15:00", "16:00", "IoT & Embedded AI (ARO 379)", "ARO 379", "Chopra Dr. Khyati", "A-406-CR", False),
        ("AIML", 5, "B2", None, "Tuesday", "09:00", "11:00", "Pattern Recognition (ARM305)", "ARM305", "Goel Dr. Rishu", "A-406-CR", False),
        ("AIML", 5, "B2", None, "Tuesday", "11:00", "12:00", "Human Values & Ethics (HSAI307)", "HSAI307", "Hooda Dr. Chetana", "A-406-CR", False),
        ("AIML", 5, "B2", None, "Tuesday", "12:00", "13:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-406-CR", False),
        ("AIML", 5, "B2", None, "Tuesday", "14:00", "15:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-401 CR", False),
        ("AIML", 5, "B2", None, "Tuesday", "15:00", "16:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-401 CR", False),
        ("AIML", 5, "B2", None, "Wednesday", "09:00", "10:00", "Pattern Recognition (ARM305)", "ARM305", "Goel Dr. Rishu", "A-402-CR", False),
        ("AIML", 5, "B2", None, "Wednesday", "10:00", "11:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-402-CR", False),
        ("AIML", 5, "B2", None, "Wednesday", "11:00", "13:00", "AI System Design Lab (ARM351)", "ARM351", "Choudhary Dr. Amit", "A-203-Com Lab", True),
        ("AIML", 5, "B2", None, "Wednesday", "14:00", "15:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-403", False),
        ("AIML", 5, "B2", None, "Thursday", "11:00", "12:00", "IoT & Embedded AI (ARO 379)", "ARO 379", "Chopra Dr. Khyati", "A-403", False),
        ("AIML", 5, "B2", None, "Thursday", "12:00", "13:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-403", False),
        ("AIML", 5, "B2", None, "Thursday", "14:00", "15:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-403", False),
        ("AIML", 5, "B2", None, "Thursday", "15:00", "16:00", "Reinforcement Learning (ARM301)", "ARM301", "Bhatia Dr. Anshul", "A-403", False),
        ("AIML", 5, "B2", None, "Friday", "09:00", "11:00", "NLP & Deep Learning Lab (ARM353)", "ARM353", "Goel Dr. Rishu", "AUB-03-Com Lab", True),
        ("AIML", 5, "B2", None, "Friday", "11:00", "12:00", "Natural Language Processing (ARM303)", "ARM303", "Choudhary Dr. Amit", "A-508-CR", False),
        ("AIML", 5, "B2", None, "Friday", "12:00", "13:00", "Professional Core Elective (ARM319)", "ARM319", "Tyagi Ms. Himani", "A-508-CR", False),
        ("AIML", 5, "B2", None, "Friday", "14:00", "15:00", "IoT & Embedded AI (ARO 379)", "ARO 379", "Chopra Dr. Khyati", "A-508-CR", False),
        ("AIML", 5, "B2", None, "Friday", "15:00", "16:00", "Pattern Recognition (ARM305)", "ARM305", "Goel Dr. Rishu", "A-508-CR", False),

        # --- Page 10: AIML-VII ---
        ("AIML", 7, "B1", None, "Monday", "10:00", "11:00", "Advanced Computer Vision (ARM401)", "ARM401", "Lalit Dr. Ruchika", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Monday", "11:00", "12:00", "Speech Processing (ARM403)", "ARM403", "Singh Dr. Sanjay", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Monday", "13:00", "14:00", "Reinforcement Learning (ARD429)", "ARD429", "Dua Ms. Disha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Monday", "14:00", "15:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Monday", "15:00", "16:00", "Generative AI Systems (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Tuesday", "09:00", "10:00", "Generative AI Systems (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Tuesday", "10:00", "11:00", "Advanced Computer Vision (ARM401)", "ARM401", "Lalit Dr. Ruchika", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", "A", "Tuesday", "11:00", "13:00", "Vision Lab (ARM451)", "ARM451", "Lalit Dr. Ruchika", "A-203-Com Lab", True),
        ("AIML", 7, "B1", "B", "Tuesday", "11:00", "13:00", "Speech Lab (ARM453)", "ARM453", "Kirti Ms.", "USDI-B-002-Comp Lab", True),
        ("AIML", 7, "B1", None, "Tuesday", "14:00", "15:00", "Speech Processing (ARM403)", "ARM403", "Singh Dr. Sanjay", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Tuesday", "15:00", "16:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Wednesday", "10:00", "11:00", "Reinforcement Learning (ARD429)", "ARD429", "Dua Ms. Disha", "A-004 Lec Hall", False),
        ("AIML", 7, "B1", "A", "Wednesday", "11:00", "13:00", "Vision Lab (ARM451)", "ARM451", "Lalit Dr. Ruchika", "AUB-04-Com Lab", True),
        ("AIML", 7, "B1", "B", "Wednesday", "11:00", "13:00", "Speech Lab (ARM453)", "ARM453", "Kirti Ms.", "AUB-03-Com Lab", True),
        ("AIML", 7, "B1", None, "Wednesday", "14:00", "15:00", "Generative AI (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Wednesday", "15:00", "16:00", "Speech Processing (ARM403)", "ARM403", "Singh Dr. Sanjay", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Thursday", "09:00", "11:00", "Social Media Analytics (ARO487)", "ARO487", "Aggarwal Dr. Pratibha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Thursday", "11:00", "12:00", "Speech Processing (ARM403)", "ARM403", "Singh Dr. Sanjay", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Thursday", "12:00", "13:00", "Advanced Computer Vision (ARM401)", "ARM401", "Lalit Dr. Ruchika", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Thursday", "14:00", "15:00", "Generative AI Systems (ARD425)", "ARD425", "Jangid Dr. Manisha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Thursday", "15:00", "16:00", "Reinforcement Learning (ARD429)", "ARD429", "Dua Ms. Disha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Friday", "10:00", "11:00", "Social Media Analytics (ARO487)", "ARO487", "Aggarwal Dr. Pratibha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Friday", "11:00", "12:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Friday", "12:00", "13:00", "Reinforcement Learning (ARD429)", "ARD429", "Dua Ms. Disha", "A-005 Lec Hall", False),
        ("AIML", 7, "B1", None, "Friday", "13:00", "14:00", "Advanced Computer Vision (ARM401)", "ARM401", "Lalit Dr. Ruchika", "A-005 Lec Hall", False),

        # --- Page 11: AR-III-B1 ---
        ("AR", 3, "B1", None, "Monday", "10:00", "11:00", "Robotics Kinematics (ARA203)", "ARA203", "Muthaiah Dr. V. M. Rajavel", "A-210-CR", False),
        ("AR", 3, "B1", None, "Monday", "11:00", "12:00", "Sensors & Actuators (ARA207)", "ARA207", "Shankar Dr. Shashi", "A-210-CR", False),
        ("AR", 3, "B1", None, "Monday", "12:00", "13:00", "Control Systems (ARA209)", "ARA209", "Bhargava Dr. Ankur", "A-210-CR", False),
        ("AR", 3, "B1", None, "Monday", "14:00", "15:00", "Applied Thermodynamics (ARA205)", "ARA205", "Arya Dr. Rajendra", "A-405-CR", False),
        ("AR", 3, "B1", "B", "Monday", "15:00", "17:00", "Robotics Simulation Lab (ARA253)", "ARA253", "Arya Dr. Rajendra", "A-301-Rob Lab", True),
        ("AR", 3, "B1", "A", "Monday", "15:00", "17:00", "Material Testing Lab (ARA251)", "ARA251", "Chaudhary Dr. Sumit", "A-302-Material Lab", True),
        ("AR", 3, "B1", None, "Tuesday", "09:00", "10:00", "Electrical Machines (ARA211)", "ARA211", "Gulati Dr. Sowmya", "A-405-CR", False),
        ("AR", 3, "B1", None, "Tuesday", "10:00", "11:00", "Engineering Mechanics (ARA201)", "ARA201", "Chaudhary Dr. Sumit", "A-405-CR", False),
        ("AR", 3, "B1", None, "Tuesday", "11:00", "12:00", "Control Systems (ARA209)", "ARA209", "Bhargava Dr. Ankur", "A-405-CR", False),
        ("AR", 3, "B1", None, "Tuesday", "12:00", "13:00", "Robotics Kinematics (ARA203)", "ARA203", "Muthaiah Dr. V. M. Rajavel", "A-405-CR", False),
        ("AR", 3, "B1", None, "Tuesday", "13:00", "14:00", "Applied Thermodynamics (ARA205)", "ARA205", "Arya Dr. Rajendra", "A-405-CR", False),
        ("AR", 3, "B1", None, "Wednesday", "09:00", "11:00", "CAD / Modeling Lab (ARA255)", "ARA255", "Bhargava Dr. Ankur", "A-303", True),
        ("AR", 3, "B1", None, "Wednesday", "11:00", "12:00", "Electrical Machines (ARA211)", "ARA211", "Gulati Dr. Sowmya", "A-405-CR", False),
        ("AR", 3, "B1", None, "Wednesday", "12:00", "13:00", "Engineering Mechanics (ARA201)", "ARA201", "Chaudhary Dr. Sumit", "A-405-CR", False),
        ("AR", 3, "B1", None, "Wednesday", "14:00", "15:00", "Sensors & Actuators (ARA207)", "ARA207", "Shankar Dr. Shashi", "A-405-CR", False),
        ("AR", 3, "B1", "A", "Wednesday", "15:00", "17:00", "Mechatronics Lab (ARA257)", "ARA257", "Arya Dr. Rajendra", "A-304-Mechatronic lab", True),
        ("AR", 3, "B1", None, "Thursday", "09:00", "10:00", "Engineering Mechanics (ARA201)", "ARA201", "Chaudhary Dr. Sumit", "A-405-CR", False),
        ("AR", 3, "B1", None, "Thursday", "10:00", "11:00", "Sensors & Actuators (ARA207)", "ARA207", "Shankar Dr. Shashi", "A-405-CR", False),
        ("AR", 3, "B1", None, "Thursday", "11:00", "12:00", "Robotics Kinematics (ARA203)", "ARA203", "Muthaiah Dr. V. M. Rajavel", "A-405-CR", False),
        ("AR", 3, "B1", None, "Thursday", "13:00", "15:00", "CAD / Modeling Lab (ARA255)", "ARA255", "Bhargava Dr. Ankur", "A-203-Com Lab", True),
        ("AR", 3, "B1", "B", "Thursday", "15:00", "17:00", "Mechatronics Lab (ARA257)", "ARA257", "Muthaiah Dr. V. M. Rajavel", "A-304-Mechatronic lab", True),
        ("AR", 3, "B1", "A", "Thursday", "15:00", "17:00", "Mechatronics Lab (ARA257)", "ARA257", "Arya Dr. Rajendra", "Block C- de Novo Lab", True),
        ("AR", 3, "B1", "B", "Friday", "09:00", "11:00", "Mechatronics Lab (ARA257)", "ARA257", "Muthaiah Dr. V. M. Rajavel", "A-304-Mechatronic lab", True),
        ("AR", 3, "B1", None, "Friday", "11:00", "12:00", "Applied Thermodynamics (ARA205)", "ARA205", "Arya Dr. Rajendra", "A-405-CR", False),
        ("AR", 3, "B1", "A", "Friday", "12:00", "14:00", "Robotics Simulation Lab (ARA253)", "ARA253", "Anand Dr.Sourabh", "A-301-Rob Lab", True),
        ("AR", 3, "B1", "B", "Friday", "12:00", "14:00", "Material Testing Lab (ARA251)", "ARA251", "Chaudhary Dr. Sumit", "A-302-Material Lab", True),

        # --- Page 12: AR-III-B2 ---
        ("AR", 3, "B2", None, "Monday", "11:00", "12:00", "Applied Thermodynamics (ARA205)", "ARA205", "Arya Dr. Rajendra", "A-401 CR", False),
        ("AR", 3, "B2", None, "Monday", "12:00", "13:00", "Sensors & Actuators (ARA207)", "ARA207", "Shankar Dr. Shashi", "A-401 CR", False),
        ("AR", 3, "B2", None, "Monday", "14:00", "15:00", "Robotics Kinematics (ARA203)", "ARA203", "Muthaiah Dr. V. M. Rajavel", "A-402-CR", False),
        ("AR", 3, "B2", None, "Monday", "15:00", "17:00", "CAD / Modeling Lab (ARA255)", "ARA255", "Bhargava Dr. Ankur", "A-303", True),
        ("AR", 3, "B2", None, "Tuesday", "10:00", "11:00", "Robotics Kinematics (ARA203)", "ARA203", "Muthaiah Dr. V. M. Rajavel", "A-404-CR", False),
        ("AR", 3, "B2", None, "Tuesday", "11:00", "12:00", "Engineering Mechanics (ARA201)", "ARA201", "Chaudhary Dr. Sumit", "A-404-CR", False),
        ("AR", 3, "B2", None, "Tuesday", "12:00", "13:00", "Electrical Machines (ARA211)", "ARA211", "Gulati Dr. Sowmya", "A-404-CR", False),
        ("AR", 3, "B2", None, "Tuesday", "14:00", "15:00", "Applied Thermodynamics (ARA205)", "ARA205", "Arya Dr. Rajendra", "A-405-CR", False),
        ("AR", 3, "B2", None, "Tuesday", "15:00", "16:00", "Sensors & Actuators (ARA207)", "ARA207", "Shankar Dr. Shashi", "A-405-CR", False),
        ("AR", 3, "B2", None, "Wednesday", "10:00", "11:00", "Robotics Kinematics (ARA203)", "ARA203", "Muthaiah Dr. V. M. Rajavel", "A-405-CR", False),
        ("AR", 3, "B2", "A", "Wednesday", "11:00", "13:00", "Robotics Simulation Lab (ARA253)", "ARA253", "Bhargava Dr. Ankur", "A-301-Rob Lab", True),
        ("AR", 3, "B2", "B", "Wednesday", "11:00", "13:00", "Mechatronics Lab (ARA257)", "ARA257", "Singh Dr. Sakshi", "A-304-Mechatronic lab", True),
        ("AR", 3, "B2", None, "Wednesday", "13:00", "14:00", "Engineering Mechanics (ARA201)", "ARA201", "Chaudhary Dr. Sumit", "A-306-CR", False),
        ("AR", 3, "B2", "B", "Wednesday", "15:00", "17:00", "Mechatronics Lab (ARA257)", "ARA257", "Singh Dr. Sakshi", "A-303", True),
        ("AR", 3, "B2", "A", "Wednesday", "15:00", "17:00", "Material Testing Lab (ARA251)", "ARA251", "Chaudhary Dr. Sumit", "A-302-Material Lab", True),
        ("AR", 3, "B2", "B", "Thursday", "09:00", "11:00", "Robotics Simulation Lab (ARA253)", "ARA253", "Arya Dr. Rajendra", "A-301-Rob Lab", True),
        ("AR", 3, "B2", "A", "Thursday", "09:00", "11:00", "Mechatronics Lab (ARA257)", "ARA257", "Singh Dr. Sakshi", "A-304-Mechatronic lab", True),
        ("AR", 3, "B2", None, "Thursday", "11:00", "12:00", "Control Systems (ARA209)", "ARA209", "Bhargava Dr. Ankur", "A-209-CR", False),
        ("AR", 3, "B2", None, "Thursday", "12:00", "13:00", "Engineering Mechanics (ARA201)", "ARA201", "Chaudhary Dr. Sumit", "A-209-CR", False),
        ("AR", 3, "B2", None, "Thursday", "13:00", "14:00", "Electrical Machines (ARA211)", "ARA211", "Gulati Dr. Sowmya", "A-209-CR", False),
        ("AR", 3, "B2", "A", "Thursday", "15:00", "17:00", "Mechatronics Lab (ARA257)", "ARA257", "Singh Dr. Sakshi", "A-303", True),
        ("AR", 3, "B2", "B", "Thursday", "15:00", "17:00", "Material Testing Lab (ARA251)", "ARA251", "Chaudhary Dr. Sumit", "A-302-Material Lab", True),
        ("AR", 3, "B2", None, "Friday", "10:00", "11:00", "Applied Thermodynamics (ARA205)", "ARA205", "Arya Dr. Rajendra", "A-402-CR", False),
        ("AR", 3, "B2", None, "Friday", "11:00", "13:00", "CAD / Modeling Lab (ARA255)", "ARA255", "Bhargava Dr. Ankur", "AUB-04-Com Lab", True),
        ("AR", 3, "B2", None, "Friday", "14:00", "15:00", "Sensors & Actuators (ARA207)", "ARA207", "Shankar Dr. Shashi", "A-209-CR", False),
        ("AR", 3, "B2", None, "Friday", "15:00", "16:00", "Control Systems (ARA209)", "ARA209", "Bhargava Dr. Ankur", "A-209-CR", False),

        # --- Page 13: AR-V_B1 ---
        ("AR", 5, "B1", None, "Monday", "09:00", "10:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-306-CR", False),
        ("AR", 5, "B1", None, "Monday", "10:00", "11:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-306-CR", False),
        ("AR", 5, "B1", None, "Monday", "11:00", "12:00", "Robotics Vision (ARA305)", "ARA305", "Baghel Dr. Pushp Kumar", "A-306-CR", False),
        ("AR", 5, "B1", None, "Monday", "12:00", "13:00", "Microcontrollers (MSAR303)", "MSAR303", "Kumar Sh. Arvind", "A-306-CR", False),
        ("AR", 5, "B1", None, "Monday", "14:00", "15:00", "Open Elective (ARO377)", "ARO377", "Priya Dr. Annu", "A-306-CR", False),
        ("AR", 5, "B1", None, "Monday", "15:00", "16:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-306-CR", False),
        ("AR", 5, "B1", None, "Tuesday", "10:00", "11:00", "Robotics Vision (ARA305)", "ARA305", "Baghel Dr. Pushp Kumar", "A-306-CR", False),
        ("AR", 5, "B1", None, "Tuesday", "11:00", "12:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-306-CR", False),
        ("AR", 5, "B1", None, "Tuesday", "13:00", "15:00", "Embedded Robotics Lab (ARA353)", "ARA353", "Singh Dr. Amanpreet", "USDI-B-002-Comp Lab", True),
        ("AR", 5, "B1", None, "Tuesday", "15:00", "16:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-306-CR", False),
        ("AR", 5, "B1", None, "Tuesday", "16:00", "17:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-306-CR", False),
        ("AR", 5, "B1", None, "Wednesday", "09:00", "11:00", "Robotics Lab (ARA351)", "ARA351", "Baghel Dr. Pushp Kumar", "A-301-Rob Lab", True),
        ("AR", 5, "B1", None, "Wednesday", "11:00", "12:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-306-CR", False),
        ("AR", 5, "B1", None, "Wednesday", "12:00", "13:00", "Microcontrollers (MSAR303)", "MSAR303", "Kumar Sh. Arvind", "A-306-CR", False),
        ("AR", 5, "B1", None, "Wednesday", "14:00", "15:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-306-CR", False),
        ("AR", 5, "B1", None, "Wednesday", "15:00", "16:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-306-CR", False),
        ("AR", 5, "B1", None, "Thursday", "09:00", "11:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-306-CR", False),
        ("AR", 5, "B1", None, "Thursday", "11:00", "12:00", "Robotics Vision (ARA305)", "ARA305", "Baghel Dr. Pushp Kumar", "A-306-CR", False),
        ("AR", 5, "B1", None, "Thursday", "13:00", "14:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-306-CR", False),
        ("AR", 5, "B1", None, "Thursday", "14:00", "15:00", "Open Elective (ARO377)", "ARO377", "Priya Dr. Annu", "A-306-CR", False),
        ("AR", 5, "B1", None, "Friday", "09:00", "10:00", "Open Elective (ARO377)", "ARO377", "Priya Dr. Annu", "A-306-CR", False),
        ("AR", 5, "B1", None, "Friday", "10:00", "11:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-306-CR", False),
        ("AR", 5, "B1", None, "Friday", "11:00", "12:00", "Robotics Vision (ARA305)", "ARA305", "Baghel Dr. Pushp Kumar", "A-306-CR", False),
        ("AR", 5, "B1", None, "Friday", "13:00", "14:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-306-CR", False),

        # --- Page 14: AR-V_B2 ---
        ("AR", 5, "B2", None, "Monday", "10:00", "11:00", "Microcontrollers (MSAR303)", "MSAR303", "Kumar Sh. Arvind", "A-209-CR", False),
        ("AR", 5, "B2", None, "Monday", "11:00", "12:00", "Robotics Vision (ARA305)", "ARA305", "Singh Dr. Sakshi", "A-209-CR", False),
        ("AR", 5, "B2", None, "Monday", "12:00", "13:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-005 Lec Hall", False),
        ("AR", 5, "B2", None, "Monday", "14:00", "15:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-307-CR", False),
        ("AR", 5, "B2", None, "Monday", "15:00", "16:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-307-CR", False),
        ("AR", 5, "B2", None, "Monday", "16:00", "17:00", "Open Elective (ARO377)", "ARO377", "Priya Dr. Annu", "A-307-CR", False),
        ("AR", 5, "B2", None, "Tuesday", "10:00", "11:00", "Robotics Vision (ARA305)", "ARA305", "Singh Dr. Sakshi", "A-702-CR", False),
        ("AR", 5, "B2", None, "Tuesday", "11:00", "12:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-702-CR", False),
        ("AR", 5, "B2", None, "Tuesday", "12:00", "13:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-702-CR", False),
        ("AR", 5, "B2", None, "Tuesday", "14:00", "15:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-307-CR", False),
        ("AR", 5, "B2", None, "Tuesday", "15:00", "16:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-307-CR", False),
        ("AR", 5, "B2", None, "Wednesday", "09:00", "10:00", "Microcontrollers (MSAR303)", "MSAR303", "Kumar Sh. Arvind", "A-005 Lec Hall", False),
        ("AR", 5, "B2", None, "Wednesday", "10:00", "11:00", "Robotics Vision (ARA305)", "ARA305", "Singh Dr. Sakshi", "A-005 Lec Hall", False),
        ("AR", 5, "B2", None, "Wednesday", "11:00", "12:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-005 Lec Hall", False),
        ("AR", 5, "B2", None, "Wednesday", "12:00", "13:00", "Open Elective (ARO377)", "ARO377", "Priya Dr. Annu", "A-005 Lec Hall", False),
        ("AR", 5, "B2", None, "Wednesday", "14:00", "15:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-307-CR", False),
        ("AR", 5, "B2", None, "Thursday", "09:00", "10:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-401 CR", False),
        ("AR", 5, "B2", None, "Thursday", "10:00", "11:00", "Open Elective (ARO377)", "ARO377", "Priya Dr. Annu", "A-401 CR", False),
        ("AR", 5, "B2", None, "Thursday", "11:00", "12:00", "PLC Programming (ARA319)", "ARA319", "Anand Dr.Sourabh", "A-401 CR", False),
        ("AR", 5, "B2", None, "Thursday", "13:00", "15:00", "Embedded Robotics Lab (ARA353)", "ARA353", "Singh Dr. Amanpreet", "USDI-B-002-Comp Lab", True),
        ("AR", 5, "B2", None, "Thursday", "15:00", "16:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-210-CR", False),
        ("AR", 5, "B2", None, "Thursday", "16:00", "17:00", "Robotic Automation (ARA309)", "ARA309", "Butola Dr. Ravi", "A-210-CR", False),
        ("AR", 5, "B2", None, "Friday", "09:00", "11:00", "Robotics Lab (ARA351)", "ARA351", "Baghel Dr. Pushp Kumar", "A-301-Rob Lab", True),
        ("AR", 5, "B2", None, "Friday", "11:00", "12:00", "Robotics Vision (ARA305)", "ARA305", "Singh Dr. Sakshi", "A-210-CR", False),
        ("AR", 5, "B2", None, "Friday", "13:00", "14:00", "Industrial Robotics (ARA307)", "ARA307", "Singh Dr. Amanpreet", "A-210-CR", False),

        # --- Page 15: AR-VII ---
        ("AR", 7, "B1", None, "Monday", "11:00", "12:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-106", False),
        ("AR", 7, "B1", None, "Monday", "12:00", "13:00", "Advanced Robotics (ARA401)", "ARA401", "Singh Dr. Sakshi", "A-106", False),
        ("AR", 7, "B1", None, "Monday", "14:00", "15:00", "Autonomous Navigation (ARA427)", "ARA427", "Bhargava Dr. Ankur", "A-106", False),
        ("AR", 7, "B1", None, "Monday", "15:00", "16:00", "Industrial Automation (ARA403)", "ARA403", "Baghel Dr. Pushp Kumar", "A-106", False),
        ("AR", 7, "B1", None, "Monday", "16:00", "17:00", "Design of Mechatronics (ARO485)", "ARO485", "Johari Prof. Rahul", "A-106", False),
        ("AR", 7, "B1", "B2", "Tuesday", "09:00", "11:00", "Advanced Robotics Lab (ARA451)", "ARA451", "Butola Dr. Ravi", "A-303", True),
        ("AR", 7, "B1", None, "Tuesday", "11:00", "12:00", "Design of Mechatronics (ARO485)", "ARO485", "Johari Prof. Rahul", "A-106", False),
        ("AR", 7, "B1", None, "Tuesday", "12:00", "13:00", "Autonomous Navigation (ARA427)", "ARA427", "Bhargava Dr. Ankur", "A-106", False),
        ("AR", 7, "B1", None, "Tuesday", "14:00", "15:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-106", False),
        ("AR", 7, "B1", None, "Tuesday", "15:00", "16:00", "Industrial Automation (ARA403)", "ARA403", "Baghel Dr. Pushp Kumar", "A-106", False),
        ("AR", 7, "B1", None, "Wednesday", "09:00", "10:00", "Robotic Manipulation (ARA425)", "ARA425", "Anand Dr.Sourabh", "A-106", False),
        ("AR", 7, "B1", None, "Wednesday", "10:00", "11:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "A-106", False),
        ("AR", 7, "B1", None, "Wednesday", "11:00", "12:00", "Design of Mechatronics (ARO485)", "ARO485", "Johari Prof. Rahul", "A-106", False),
        ("AR", 7, "B1", "B2", "Wednesday", "13:00", "15:00", "Major Project Lab (ART453)", "ART453", "Baghel Dr. Pushp Kumar", "A-304-Mechatronic lab", True),
        ("AR", 7, "B1", None, "Wednesday", "15:00", "16:00", "Industrial Automation (ARA403)", "ARA403", "Baghel Dr. Pushp Kumar", "A-106", False),
        ("AR", 7, "B1", None, "Wednesday", "16:00", "17:00", "Autonomous Navigation (ARA427)", "ARA427", "Bhargava Dr. Ankur", "A-106", False),
        ("AR", 7, "B1", None, "Thursday", "09:00", "10:00", "Autonomous Navigation (ARA427)", "ARA427", "Bhargava Dr. Ankur", "A-106", False),
        ("AR", 7, "B1", "B1", "Thursday", "10:00", "12:00", "Advanced Robotics Lab (ARA451)", "ARA451", "Butola Dr. Ravi", "A-303", True),
        ("AR", 7, "B1", None, "Thursday", "12:00", "13:00", "Robotic Manipulation (ARA425)", "ARA425", "Anand Dr.Sourabh", "A-106", False),
        ("AR", 7, "B1", None, "Thursday", "14:00", "15:00", "Advanced Robotics (ARA401)", "ARA401", "Singh Dr. Sakshi", "A-106", False),
        ("AR", 7, "B1", None, "Thursday", "15:00", "16:00", "Robotic Manipulation (ARA425)", "ARA425", "Anand Dr.Sourabh", "A-106", False),
        ("AR", 7, "B1", None, "Thursday", "16:00", "17:00", "Industrial Automation (ARA403)", "ARA403", "Baghel Dr. Pushp Kumar", "A-106", False),
        ("AR", 7, "B1", None, "Friday", "10:00", "11:00", "Advanced Robotics (ARA401)", "ARA401", "Singh Dr. Sakshi", "A-106", False),
        ("AR", 7, "B1", None, "Friday", "11:00", "12:00", "Robotic Manipulation (ARA425)", "ARA425", "Anand Dr.Sourabh", "A-106", False),
        ("AR", 7, "B1", "B1", "Friday", "13:00", "15:00", "Major Project Lab (ART453)", "ART453", "Baghel Dr. Pushp Kumar", "A-304-Mechatronic lab", True),
        ("AR", 7, "B1", None, "Friday", "15:00", "16:00", "Advanced Robotics (ARA401)", "ARA401", "Singh Dr. Sakshi", "A-106", False),

        # --- Page 16: IIOT-III_B1 ---
        ("IIOT", 3, "B1", "B", "Monday", "09:00", "11:00", "Analog Electronics Lab (ARI251)", "ARI251", "Singh Dr. Abhishek", "A-203-Com Lab", True),
        ("IIOT", 3, "B1", "A", "Monday", "09:00", "11:00", "IoT Embedded Systems Lab (ARI255)", "ARI255", "Chopra Dr. Khyati", "A-507-IIOT Lab", True),
        ("IIOT", 3, "B1", None, "Monday", "11:00", "12:00", "Network Protocols for IoT (ARI205)", "ARI205", "Singh Dr. Abhishek", "A-404-CR", False),
        ("IIOT", 3, "B1", None, "Monday", "13:00", "14:00", "Signals and Systems (ARI203)", "ARI203", "Kumar Dr. Manoj", "A-401 CR", False),
        ("IIOT", 3, "B1", None, "Monday", "14:00", "15:00", "Industrial Sensor Tech (ARI209)", "ARI209", "Sehgal Dr. Ruchika", "A-401 CR", False),
        ("IIOT", 3, "B1", None, "Tuesday", "09:00", "10:00", "Cloud Computing for IoT (ARI207)", "ARI207", "Khurshid Bijli Dr. Mahvish", "A-401 CR", False),
        ("IIOT", 3, "B1", None, "Tuesday", "10:00", "11:00", "Industrial Sensor Tech (ARI209)", "ARI209", "Sehgal Dr. Ruchika", "A-401 CR", False),
        ("IIOT", 3, "B1", None, "Tuesday", "11:00", "12:00", "Signals and Systems (ARI203)", "ARI203", "Kumar Dr. Manoj", "A-401 CR", False),
        ("IIOT", 3, "B1", "A", "Tuesday", "13:00", "15:00", "Python for IoT Lab (ARI261)", "ARI261", "Singh Dr. Rohit", "A-007-Com Lab", True),
        ("IIOT", 3, "B1", "B", "Tuesday", "13:00", "15:00", "Electrical Drives Lab (ARA253)", "ARA253", "Kumar Dr. Manoj", "AUB-06-Ele.Lab", True),
        ("IIOT", 3, "B1", None, "Wednesday", "10:00", "11:00", "Data Structures for IoT (ARI201)", "ARI201", "Kumar Mr. Anuj", "A-508-CR", False),
        ("IIOT", 3, "B1", None, "Wednesday", "11:00", "12:00", "Cloud Computing for IoT (ARI207)", "ARI207", "Khurshid Bijli Dr. Mahvish", "A-508-CR", False),
        ("IIOT", 3, "B1", None, "Wednesday", "12:00", "13:00", "Applied Mathematics (ARI211)", "ARI211", "Gulati Dr. Sowmya", "A-508-CR", False),
        ("IIOT", 3, "B1", None, "Wednesday", "14:00", "15:00", "Signals and Systems (ARI203)", "ARI203", "Kumar Dr. Manoj", "A-402-CR", False),
        ("IIOT", 3, "B1", "B", "Wednesday", "15:00", "17:00", "IoT Embedded Systems Lab (ARI255)", "ARI255", "Chopra Dr. Khyati", "A-507-IIOT Lab", True),
        ("IIOT", 3, "B1", "A", "Wednesday", "15:00", "17:00", "Analog Electronics Lab (ARI251)", "ARI251", "Singh Dr. Abhishek", "A-007-Com Lab", True),
        ("IIOT", 3, "B1", "B", "Thursday", "09:00", "11:00", "Industrial IoT Lab (ARI257)", "ARI257", "Khurshid Bijli Dr. Mahvish", "A-007-Com Lab", True),
        ("IIOT", 3, "B1", "A", "Thursday", "09:00", "11:00", "PLC Systems Lab (ARI259)", "ARI259", "Chaudhary Sheetal", "A-203-Com Lab", True),
        ("IIOT", 3, "B1", None, "Thursday", "11:00", "12:00", "Data Structures for IoT (ARI201)", "ARI201", "Kumar Mr. Anuj", "A-201", False),
        ("IIOT", 3, "B1", None, "Thursday", "12:00", "13:00", "Applied Mathematics (ARI211)", "ARI211", "Gulati Dr. Sowmya", "A-201", False),
        ("IIOT", 3, "B1", None, "Thursday", "14:00", "15:00", "Cloud Computing for IoT (ARI207)", "ARI207", "Khurshid Bijli Dr. Mahvish", "A-401 CR", False),
        ("IIOT", 3, "B1", None, "Thursday", "15:00", "16:00", "Industrial Sensor Tech (ARI209)", "ARI209", "Sehgal Dr. Ruchika", "A-401 CR", False),
        ("IIOT", 3, "B1", "B", "Friday", "09:00", "11:00", "PLC Systems Lab (ARI259)", "ARI259", "Chaudhary Sheetal", "AUB-04-Com Lab", True),
        ("IIOT", 3, "B1", "A", "Friday", "09:00", "11:00", "Industrial IoT Lab (ARI257)", "ARI257", "Khurshid Bijli Dr. Mahvish", "A-203-Com Lab", True),
        ("IIOT", 3, "B1", "B", "Friday", "11:00", "13:00", "Python for IoT Lab (ARI261)", "ARI261", "Singh Dr. Rohit", "A-203-Com Lab", True),
        ("IIOT", 3, "B1", "A", "Friday", "11:00", "13:00", "Electrical Drives Lab (ARA253)", "ARA253", "Kumar Dr. Manoj", "AUB-06-Ele.Lab", True),
        ("IIOT", 3, "B1", None, "Friday", "14:00", "15:00", "Data Structures for IoT (ARI201)", "ARI201", "Kumar Mr. Anuj", "A-401 CR", False),
        ("IIOT", 3, "B1", None, "Friday", "15:00", "16:00", "Network Protocols for IoT (ARI205)", "ARI205", "Singh Dr. Abhishek", "A-401 CR", False),

        # --- Page 17: IIOT-III_B2 ---
        ("IIOT", 3, "B2", None, "Monday", "10:00", "11:00", "Signals and Systems (ARI203)", "ARI203", "Kumar Dr. Manoj", "A-406-CR", False),
        ("IIOT", 3, "B2", None, "Monday", "11:00", "12:00", "Cloud Computing for IoT (ARI207)", "ARI207", "Khurshid Bijli Dr. Mahvish", "A-406-CR", False),
        ("IIOT", 3, "B2", "B", "Monday", "13:00", "15:00", "Analog Electronics Lab (ARI251)", "ARI251", "Kumar Dr. Ashok", "A-007-Com Lab", True),
        ("IIOT", 3, "B2", "A", "Monday", "13:00", "15:00", "Industrial IoT Lab (ARI257)", "ARI257", "Khurshid Bijli Dr. Mahvish", "A-204-Com Lab", True),
        ("IIOT", 3, "B2", None, "Monday", "15:00", "16:00", "Industrial Sensor Tech (ARI209)", "ARI209", "Singh Dr. Arti", "A-401 CR", False),
        ("IIOT", 3, "B2", None, "Tuesday", "11:00", "12:00", "Applied Mathematics (ARI211)", "ARI211", "Gulati Dr. Sowmya", "A-005 Lec Hall", False),
        ("IIOT", 3, "B2", None, "Tuesday", "12:00", "13:00", "Cloud Computing for IoT (ARI207)", "ARI207", "Khurshid Bijli Dr. Mahvish", "A-005 Lec Hall", False),
        ("IIOT", 3, "B2", None, "Tuesday", "14:00", "15:00", "Data Structures for IoT (ARI201)", "ARI201", "Kumar Mr. Anuj", "A-404-CR", False),
        ("IIOT", 3, "B2", "B", "Tuesday", "15:00", "17:00", "PLC Systems Lab (ARI259)", "ARI259", "Chaudhary Sheetal", "AUB-04-Com Lab", True),
        ("IIOT", 3, "B2", "A", "Tuesday", "15:00", "17:00", "IoT Embedded Systems Lab (ARI255)", "ARI255", "Chopra Dr. Khyati", "A-507-IIOT Lab", True),
        ("IIOT", 3, "B2", "B", "Wednesday", "09:00", "11:00", "IoT Embedded Systems Lab (ARI255)", "ARI255", "Chopra Dr. Khyati", "A-507-IIOT Lab", True),
        ("IIOT", 3, "B2", "A", "Wednesday", "09:00", "11:00", "PLC Systems Lab (ARI259)", "ARI259", "Chaudhary Sheetal", "AUB-04-Com Lab", True),
        ("IIOT", 3, "B2", None, "Wednesday", "11:00", "12:00", "Signals and Systems (ARI203)", "ARI203", "Kumar Dr. Manoj", "A-402-CR", False),
        ("IIOT", 3, "B2", "B", "Wednesday", "13:00", "15:00", "Python for IoT Lab (ARI261)", "ARI261", "Singh Mr. Neeraj", "A-204-Com Lab", True),
        ("IIOT", 3, "B2", "A", "Wednesday", "13:00", "15:00", "Analog Electronics Lab (ARI251)", "ARI251", "Kumar Dr. Ashok", "A-007-Com Lab", True),
        ("IIOT", 3, "B2", None, "Wednesday", "15:00", "16:00", "Cloud Computing for IoT (ARI207)", "ARI207", "Khurshid Bijli Dr. Mahvish", "A-402-CR", False),
        ("IIOT", 3, "B2", None, "Wednesday", "16:00", "17:00", "Data Structures for IoT (ARI201)", "ARI201", "Kumar Mr. Anuj", "A-402-CR", False),
        ("IIOT", 3, "B2", None, "Thursday", "09:00", "10:00", "Network Protocols for IoT (ARI205)", "ARI205", "Singh Dr. Abhishek", "A-702-CR", False),
        ("IIOT", 3, "B2", None, "Thursday", "10:00", "11:00", "Applied Mathematics (ARI211)", "ARI211", "Gulati Dr. Sowmya", "A-702-CR", False),
        ("IIOT", 3, "B2", None, "Thursday", "11:00", "12:00", "Signals and Systems (ARI203)", "ARI203", "Kumar Dr. Manoj", "A-702-CR", False),
        ("IIOT", 3, "B2", "A", "Thursday", "13:00", "15:00", "Python for IoT Lab (ARI261)", "ARI261", "Arora Dr. Amar", "A-204-Com Lab", True),
        ("IIOT", 3, "B2", "B", "Thursday", "13:00", "15:00", "Electrical Drives Lab (ARA253)", "ARA253", "Kumar Dr. Manoj", "AUB-06-Ele.Lab", True),
        ("IIOT", 3, "B2", None, "Thursday", "15:00", "16:00", "Industrial Sensor Tech (ARI209)", "ARI209", "Singh Dr. Arti", "A-702-CR", False),
        ("IIOT", 3, "B2", None, "Friday", "11:00", "12:00", "Data Structures for IoT (ARI201)", "ARI201", "Kumar Mr. Anuj", "A-402-CR", False),
        ("IIOT", 3, "B2", None, "Friday", "12:00", "13:00", "Industrial Sensor Tech (ARI209)", "ARI209", "Singh Dr. Arti", "A-402-CR", False),
        ("IIOT", 3, "B2", None, "Friday", "14:00", "15:00", "Network Protocols for IoT (ARI205)", "ARI205", "Singh Dr. Abhishek", "A-402-CR", False),
        ("IIOT", 3, "B2", "B", "Friday", "15:00", "17:00", "Industrial IoT Lab (ARI257)", "ARI257", "Khurshid Bijli Dr. Mahvish", "AUB-04-Com Lab", True),
        ("IIOT", 3, "B2", "A", "Friday", "15:00", "17:00", "Electrical Drives Lab (ARA253)", "ARA253", "Kumar Dr. Manoj", "AUB-06-Ele.Lab", True),

        # --- Page 18: IIOT-V_B1 ---
        ("IIOT", 5, "B1", None, "Monday", "09:00", "10:00", "Microcontrollers & Embedded C", "MSAR303", "Kumar Sh. Arvind", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Monday", "10:00", "11:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Monday", "11:00", "12:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Monday", "13:00", "14:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Monday", "14:00", "15:00", "Advanced Data Analytics (ARO 375)", "ARO 375", "Lalit Dr. Ruchika", "A-701", False),
        ("IIOT", 5, "B1", None, "Monday", "14:00", "15:00", "Mobile App Development (ARO373)", "ARO373", "Singh Dr. Rohit", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Monday", "15:00", "16:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Tuesday", "10:00", "11:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-104-CR", False),
        ("IIOT", 5, "B1", None, "Tuesday", "11:00", "12:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Tuesday", "12:00", "13:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Tuesday", "14:00", "15:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Tuesday", "15:00", "16:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Wednesday", "10:00", "11:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Wednesday", "11:00", "12:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Wednesday", "13:00", "14:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Wednesday", "14:00", "15:00", "Advanced Data Analytics (ARO 375)", "ARO 375", "Lalit Dr. Ruchika", "A-106", False),
        ("IIOT", 5, "B1", None, "Wednesday", "14:00", "15:00", "Mobile App Development (ARO373)", "ARO373", "Singh Dr. Rohit", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Wednesday", "15:00", "17:00", "Cloud & IoT Lab (ARI353)", "ARI353", "Kumar Dr. Ghanendra", "A-204-Com Lab", True),
        ("IIOT", 5, "B1", None, "Thursday", "09:00", "10:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Thursday", "10:00", "11:00", "Microcontrollers & Embedded C", "MSAR303", "Kumar Sh. Arvind", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Thursday", "11:00", "12:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Thursday", "13:00", "14:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Thursday", "14:00", "15:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Friday", "10:00", "11:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-210-CR", False),
        ("IIOT", 5, "B1", None, "Friday", "11:00", "13:00", "IoT Embedded Systems Lab (ARI351)", "ARI351", "Lakhanpal Sh. Anupam", "AUB-03-Com Lab", True),
        ("IIOT", 5, "B1", None, "Friday", "14:00", "15:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-105-CR", False),
        ("IIOT", 5, "B1", None, "Friday", "15:00", "16:00", "Advanced Data Analytics (ARO 375)", "ARO 375", "Lalit Dr. Ruchika", "A-701", False),
        ("IIOT", 5, "B1", None, "Friday", "15:00", "16:00", "Mobile App Development (ARO373)", "ARO373", "Singh Dr. Rohit", "A-105-CR", False),

        # --- Page 19: IIOT-V_B2 ---
        ("IIOT", 5, "B2", None, "Monday", "09:00", "10:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-701", False),
        ("IIOT", 5, "B2", None, "Monday", "10:00", "11:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-701", False),
        ("IIOT", 5, "B2", None, "Monday", "11:00", "12:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-701", False),
        ("IIOT", 5, "B2", None, "Monday", "12:00", "13:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-701", False),
        ("IIOT", 5, "B2", None, "Monday", "14:00", "15:00", "Advanced Data Analytics (ARO 375)", "ARO 375", "Lalit Dr. Ruchika", "A-701", False),
        ("IIOT", 5, "B2", None, "Monday", "15:00", "16:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-701", False),
        ("IIOT", 5, "B2", None, "Tuesday", "09:00", "10:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-701", False),
        ("IIOT", 5, "B2", None, "Tuesday", "10:00", "11:00", "Human Values (HSAR301)", "HSAR301", "Mishra Dr. Pawan Kumar", "A-701", False),
        ("IIOT", 5, "B2", None, "Tuesday", "11:00", "12:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-701", False),
        ("IIOT", 5, "B2", None, "Tuesday", "13:00", "15:00", "Cloud & IoT Lab (ARI353)", "ARI353", "Kumar Dr. Ghanendra", "AUB-04-Com Lab", True),
        ("IIOT", 5, "B2", None, "Wednesday", "09:00", "10:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-701", False),
        ("IIOT", 5, "B2", None, "Wednesday", "10:00", "11:00", "Microcontrollers & Embedded C", "MSAR303", "Kumar Sh. Arvind", "A-701", False),
        ("IIOT", 5, "B2", None, "Wednesday", "11:00", "12:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-701", False),
        ("IIOT", 5, "B2", None, "Wednesday", "13:00", "14:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-701", False),
        ("IIOT", 5, "B2", None, "Wednesday", "14:00", "15:00", "Advanced Data Analytics (ARO 375)", "ARO 375", "Lalit Dr. Ruchika", "A-106", False),
        ("IIOT", 5, "B2", None, "Wednesday", "15:00", "17:00", "IoT Embedded Systems Lab (ARI351)", "ARI351", "Lakhanpal Sh. Anupam", "AUB-04-Com Lab", True),
        ("IIOT", 5, "B2", None, "Thursday", "09:00", "10:00", "Microcontrollers & Embedded C", "MSAR303", "Kumar Sh. Arvind", "A-701", False),
        ("IIOT", 5, "B2", None, "Thursday", "10:00", "11:00", "Industrial Wireless Networks (ARI309)", "ARI309", "Bashambu Mr. Arun Kumar", "A-701", False),
        ("IIOT", 5, "B2", None, "Thursday", "11:00", "12:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-701", False),
        ("IIOT", 5, "B2", None, "Thursday", "13:00", "14:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-701", False),
        ("IIOT", 5, "B2", None, "Friday", "10:00", "12:00", "Cloud Platforms for IoT (ARI307)", "ARI307", "Kumar Dr. Ghanendra", "A-401 CR", False),
        ("IIOT", 5, "B2", None, "Friday", "12:00", "13:00", "IoT Architecture & Security (ARI305)", "ARI305", "Pal Ms. Geetanshi", "A-401 CR", False),
        ("IIOT", 5, "B2", None, "Friday", "14:00", "15:00", "Operating Systems for IoT (ARI315)", "ARI315", "Kalonia Ms. Ritu", "A-701", False),
        ("IIOT", 5, "B2", None, "Friday", "15:00", "16:00", "Advanced Data Analytics (ARO 375)", "ARO 375", "Lalit Dr. Ruchika", "A-701", False),

        # --- Page 20: IIOT-VII ---
        ("IIOT", 7, "B1", None, "Monday", "10:00", "12:00", "Industrial Robotics & Automation (ARI401)", "ARI401", "Johari Prof. Rahul", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Monday", "12:00", "13:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Monday", "14:00", "15:00", "Smart Grid & SCADA (ARI423)", "ARI423", "Singh Dr. Abhishek", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Monday", "15:00", "16:00", "Wireless Sensor Networks (ARI421)", "ARI421", "Kumar Mr. Arun", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Tuesday", "10:00", "11:00", "Cyber Physical Systems (ARI403)", "ARI403", "Shankar Dr. Shashi", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Tuesday", "11:00", "12:00", "Wireless Sensor Networks (ARI421)", "ARI421", "Kumar Mr. Arun", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Tuesday", "12:00", "13:00", "Industrial Robotics (ARI401)", "ARI401", "Johari Prof. Rahul", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Tuesday", "14:00", "15:00", "Social Media Analytics (ARO487)", "ARO487", "Aggarwal Dr. Pratibha", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Tuesday", "15:00", "16:00", "Smart Grid & SCADA (ARI423)", "ARI423", "Singh Dr. Abhishek", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Wednesday", "10:00", "12:00", "Cyber Physical Systems (ARI403)", "ARI403", "Shankar Dr. Shashi", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Wednesday", "12:00", "13:00", "Industrial Robotics (ARI401)", "ARI401", "Johari Prof. Rahul", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Wednesday", "14:00", "15:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "B-003-Lec Hall", False),
        ("IIOT", 7, "B2", "B2", "Wednesday", "15:00", "17:00", "SCADA & PLC Lab (ARI451)", "ARI451", "Shankar Dr. Shashi", "A-203-Com Lab", True),
        ("IIOT", 7, "B1", "B1", "Wednesday", "15:00", "17:00", "Industrial IoT Major Project Lab (ARI453)", "ARI453", "Johari Prof. Rahul", "AUB-03-Com Lab", True),
        ("IIOT", 7, "B1", None, "Thursday", "10:00", "12:00", "Wireless Sensor Networks (ARI421)", "ARI421", "Kumar Mr. Arun", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Thursday", "12:00", "13:00", "Social Media Analytics (ARO487)", "ARO487", "Aggarwal Dr. Pratibha", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Thursday", "14:00", "15:00", "Smart Grid & SCADA (ARI423)", "ARI423", "Singh Dr. Abhishek", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", "B1", "Thursday", "15:00", "17:00", "SCADA & PLC Lab (ARI451)", "ARI451", "Shankar Dr. Shashi", "AUB-03-Com Lab", True),
        ("IIOT", 7, "B2", "B2", "Thursday", "15:00", "17:00", "Industrial IoT Major Project Lab (ARI453)", "ARI453", "Johari Prof. Rahul", "AUB-04-Com Lab", True),
        ("IIOT", 7, "B1", None, "Friday", "09:00", "10:00", "Social Media Analytics (ARO487)", "ARO487", "Aggarwal Dr. Pratibha", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Friday", "10:00", "11:00", "Open Elective (ARO479)", "ARO479", "Kaur Ms. Navdeep", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Friday", "11:00", "12:00", "Cyber Physical Systems (ARI403)", "ARI403", "Shankar Dr. Shashi", "B-003-Lec Hall", False),
        ("IIOT", 7, "B1", None, "Friday", "12:00", "13:00", "Smart Grid & SCADA (ARI423)", "ARI423", "Singh Dr. Abhishek", "B-003-Lec Hall", False),
    ]

    for dept_c, sem, sec, batch, day, s_time, e_time, sub_name, sub_code, fac, room_str, is_lab in raw_schedule:
        # Match classroom
        room_obj = room_lookup.get(room_str)
        entry = TimetableEntry(
            upload_id=master_upload.id,
            department_code=dept_c,
            course_name=f"B.Tech {dept_c}",
            semester=sem,
            section=sec,
            batch=batch,
            day_of_week=day,
            start_time=s_time,
            end_time=e_time,
            subject_name=sub_name,
            subject_code=sub_code,
            faculty_name=fac,
            classroom_id=room_obj.id if room_obj else None,
            room_raw_text=room_str,
            is_lab=is_lab,
            is_approved=True,
            is_deleted=False
        )
        db.add(entry)

    db.commit()

    # 6. Run initial conflict scan
    ConflictService.detect_and_record_conflicts(db)

if __name__ == "__main__":
    seed_database()
    print("Database re-seeded successfully with 100% of the 20-page USAR campus dataset.")
