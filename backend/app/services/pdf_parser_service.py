import re
import os
from typing import List, Dict, Any, Tuple, Optional
import pdfplumber
from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.app.models.models import Classroom, Building, Department, TimetableEntry, Upload
from backend.app.services.conflict_service import ConflictService

# Days mapping
DAYS_MAP = {
    "mo": "Monday",
    "mon": "Monday",
    "monday": "Monday",
    "tu": "Tuesday",
    "tue": "Tuesday",
    "tuesday": "Tuesday",
    "we": "Wednesday",
    "wed": "Wednesday",
    "wednesday": "Wednesday",
    "th": "Thursday",
    "thu": "Thursday",
    "thursday": "Thursday",
    "fr": "Friday",
    "fri": "Friday",
    "friday": "Friday",
    "sa": "Saturday",
    "sat": "Saturday",
    "saturday": "Saturday"
}

TIME_SLOTS = [
    ("9:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("12:00", "13:00"),
    ("13:00", "14:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
    ("16:00", "17:00")
]

def normalize_room_name(raw_room: str) -> str:
    if not raw_room:
        return "Unknown Room"
    clean = raw_room.strip().replace("\n", " ")
    clean = re.sub(r'\s+', ' ', clean)
    return clean

def get_or_create_classroom(db: Session, raw_room_str: str) -> Optional[Classroom]:
    clean_name = normalize_room_name(raw_room_str)
    if not clean_name or clean_name == "Unknown Room":
        return None

    # Check existing classroom by room_number (case insensitive)
    existing = db.query(Classroom).filter(Classroom.room_number.ilike(clean_name)).first()
    if existing:
        return existing

    # Determine building and floor from name
    building_code = "BLOCK_A"
    building_name = "Academic Block A"
    floor = 0
    floor_label = "Ground Floor"
    room_type = "normal_classroom"

    lower_name = clean_name.lower()
    if "aub" in lower_name:
        floor = -1
        floor_label = "Basement (AUB)"
    elif "usdi" in lower_name or lower_name.startswith("b-") or "block b" in lower_name:
        building_code = "BLOCK_B"
        building_name = "Academic Block B / USDI"
        floor = 0
        floor_label = "Ground Floor"
    elif "block c" in lower_name or lower_name.startswith("c-"):
        building_code = "BLOCK_C"
        building_name = "Academic Block C"
        floor = 0
        floor_label = "Ground Floor"
    else:
        # Extract floor digit from A-101, A-201, A-301, etc.
        m = re.search(r'a-(\d)', lower_name)
        if m:
            floor_digit = int(m.group(1))
            floor = floor_digit
            if floor_digit == 0:
                floor_label = "Ground Floor"
            elif floor_digit == 1:
                floor_label = "1st Floor"
            elif floor_digit == 2:
                floor_label = "2nd Floor"
            elif floor_digit == 3:
                floor_label = "3rd Floor"
            elif floor_digit == 4:
                floor_label = "4th Floor"
            elif floor_digit == 5:
                floor_label = "5th Floor"
            elif floor_digit == 6:
                floor_label = "6th Floor"
            elif floor_digit == 7:
                floor_label = "7th Floor"

    # Room type determination
    if "com lab" in lower_name or "comp lab" in lower_name or "computer" in lower_name:
        room_type = "computer_lab"
    elif "rob lab" in lower_name or "robotics" in lower_name:
        room_type = "robotics_lab"
    elif "mechatronic" in lower_name or "material" in lower_name or "hardware" in lower_name or "iiot lab" in lower_name or "ele.lab" in lower_name:
        room_type = "hardware_lab"
    elif "lec hall" in lower_name or "lecture" in lower_name or "lt" in lower_name:
        room_type = "lecture_theatre"
    elif "lab" in lower_name:
        room_type = "hardware_lab"

    # Ensure building exists
    bldg = db.query(Building).filter(Building.code == building_code).first()
    if not bldg:
        bldg = Building(name=building_name, code=building_code, total_floors=7)
        db.add(bldg)
        db.commit()
        db.refresh(bldg)

    # Create classroom
    new_room = Classroom(
        room_number=clean_name,
        building_id=bldg.id,
        floor=floor,
        floor_label=floor_label,
        room_type=room_type,
        capacity=60 if room_type != "lecture_theatre" else 120,
        amenities=["Projector", "Smart Board", "Air Conditioned", "High-Speed WiFi"] + (["Computers & Dev Environments"] if "lab" in room_type else []),
        is_active=True
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


class PDFParserService:
    @staticmethod
    def parse_header_meta(text: str) -> Dict[str, Any]:
        """
        Extracts Department, Semester, Section from text like 'AIDS-III_B1', 'AIML-V_B2', 'AR-VII'.
        """
        dept = "USAR"
        sem = 3
        sec = "B1"

        # Match Dept-RomanSem_Sec or Dept-RomanSem
        # e.g., AIDS-III_B1, AIML-V_B2, AR-VII, IIOT-III-_B1
        m = re.search(r'(AIDS|AIML|AR|IIOT)[-_ ]*(III|V|VII|I|IV|VI|VIII)[-_ ]*([A-Z0-9_]*)', text, re.IGNORECASE)
        if m:
            d_raw = m.group(1).upper()
            s_raw = m.group(2).upper()
            sec_raw = m.group(3).upper().replace("-", "").replace("_", "")

            dept = d_raw
            roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
            sem = roman_map.get(s_raw, 3)
            sec = sec_raw if sec_raw in ["B1", "B2", "A", "B", "C"] else ("B1" if "B1" in text else "B1")

        return {
            "department": dept,
            "semester": sem,
            "section": sec
        }

    @classmethod
    def parse_cell_text(cls, cell_text: str, default_dept: str, default_sem: int, default_sec: str) -> List[Dict[str, Any]]:
        """
        Parses text within a timetable cell.
        Handles single entry or split-batch entries in a lab cell.
        """
        if not cell_text or not cell_text.strip():
            return []

        lines = [l.strip() for l in cell_text.split("\n") if l.strip()]
        if not lines:
            return []

        # Sometimes a cell contains multiple batches (e.g. Batch A and Batch B for labs)
        # Check if lines have multiple faculty names or room codes
        entries = []

        # Split multiple sub-records if we detect multiple rooms or batch markers
        # E.g.
        # Dalal Dr. Renu / AIDS-III-_B1_A- ARD 253 / ARD253 / A-203-Com Lab
        # Arora Dr. Amar / AIDS-III_B1_B-ARD 255 / ARD255 / AUB-03-Com Lab
        
        # Helper to group lines into sub-records:
        sub_chunks = []
        current_chunk = []
        for line in lines:
            # If line looks like a faculty name (starts with name / Dr. / Prof. / Ms. / Sh.) and current_chunk is not empty
            is_faculty_start = bool(re.search(r'(Dr\.|Prof\.|Ms\.|Sh\.|Mr\.)', line))
            if is_faculty_start and len(current_chunk) >= 3:
                sub_chunks.append(current_chunk)
                current_chunk = [line]
            else:
                current_chunk.append(line)
        if current_chunk:
            sub_chunks.append(current_chunk)

        for chunk in sub_chunks:
            rec = cls._parse_single_chunk(chunk, default_dept, default_sem, default_sec)
            if rec:
                entries.append(rec)

        return entries

    @classmethod
    def _parse_single_chunk(cls, chunk: List[str], default_dept: str, default_sem: int, default_sec: str) -> Optional[Dict[str, Any]]:
        if not chunk:
            return None

        faculty = "Faculty TBA"
        subject_name = ""
        subject_code = ""
        room_raw = ""
        batch = None
        is_lab = False

        # Identify lines
        for i, line in enumerate(chunk):
            # Faculty check
            if re.search(r'(Dr\.|Prof\.|Ms\.|Sh\.|Mr\.)', line) or i == 0:
                if not faculty or faculty == "Faculty TBA":
                    faculty = line

            # Room check (e.g. A-201, A-203-Com Lab, AUB-03, A-406-CR, B-003, USDI-B-002, Block C)
            if re.search(r'([A-C]-\d+|AUB-\d+|USDI|Block [A-C]|CR|Lab|Lec Hall)', line, re.IGNORECASE):
                room_raw = line

            # Subject Code check (e.g., ARD207, ARM-201, ARA253, HSAI307, OAE/ARO479)
            if re.search(r'([A-Z]{2,4}[-_ ]*\d{3}|PCE|OAE|ARM|ARD|ARA|ARI|ARO)', line, re.IGNORECASE):
                if not subject_code:
                    subject_code = line
                elif not subject_name:
                    subject_name = line

            # Batch check (_A-, _B-, Batch A, B1_A)
            batch_m = re.search(r'[_ -]([A-B])[-_ ]', line)
            if batch_m:
                batch = batch_m.group(1).upper()

            if "lab" in line.lower() or "251" in line or "253" in line or "255" in line or "257" in line or "259" in line:
                is_lab = True

        if not subject_name and subject_code:
            subject_name = subject_code
        elif not subject_name:
            subject_name = chunk[1] if len(chunk) > 1 else "Class Session"

        if not room_raw:
            # Last line fallback
            room_raw = chunk[-1]

        return {
            "faculty": faculty,
            "subject_name": subject_name,
            "subject_code": subject_code or subject_name,
            "room_raw": room_raw,
            "batch": batch,
            "is_lab": is_lab
        }

    @classmethod
    def parse_pdf_file(cls, db: Session, file_path: str, upload_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Parses multi-page PDF timetable, records entries in DB under upload_id,
        maps rooms, and runs conflict detection.
        """
        parsed_entries = []
        errors = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    meta = cls.parse_header_meta(page_text)
                    dept = meta["department"]
                    sem = meta["semester"]
                    sec = meta["section"]

                    # Extract table
                    tables = page.extract_tables()
                    if not tables:
                        # Fallback to layout / text extraction if table is not recognized
                        continue

                    table = tables[0]
                    # Find header row with time slots (9:00, 10:00, 11:00...)
                    header_row_idx = None
                    time_col_map = {} # col_idx -> (start_time, end_time)

                    for r_idx, row in enumerate(table):
                        # Clean cells
                        cleaned_row = [c.strip() if c else "" for c in row]
                        for c_idx, cell in enumerate(cleaned_row):
                            for s_start, s_end in TIME_SLOTS:
                                if s_start in cell:
                                    header_row_idx = r_idx
                                    time_col_map[c_idx] = (s_start, s_end)

                    if header_row_idx is None:
                        # If header not found in table text, assign standard columns based on count
                        time_col_map = {i + 1: TIME_SLOTS[i] for i in range(min(8, len(table[0]) - 1))}
                        header_row_idx = 0

                    # Now iterate over day rows
                    for r_idx in range(header_row_idx + 1, len(table)):
                        row = table[r_idx]
                        if not row or not any(row):
                            continue

                        # First cell is typically Day of week (Mo, Tu, We, Th, Fr, Sa)
                        first_cell = (row[0] or "").strip().lower()
                        # Extract 2-letter day
                        day_name = None
                        for d_key, d_val in DAYS_MAP.items():
                            if d_key in first_cell:
                                day_name = d_val
                                break

                        if not day_name:
                            continue

                        # Iterate through time columns
                        for c_idx, (start_time, end_time) in time_col_map.items():
                            if c_idx >= len(row):
                                continue
                            cell_val = row[c_idx]
                            if not cell_val or not cell_val.strip():
                                continue

                            cell_records = cls.parse_cell_text(cell_val, dept, sem, sec)
                            for cr in cell_records:
                                # Map classroom
                                classroom = get_or_create_classroom(db, cr["room_raw"])

                                entry = TimetableEntry(
                                    upload_id=upload_id,
                                    department_code=dept,
                                    course_name=f"B.Tech {dept}",
                                    semester=sem,
                                    section=sec,
                                    batch=cr["batch"],
                                    day_of_week=day_name,
                                    start_time=start_time,
                                    end_time=end_time,
                                    subject_name=cr["subject_name"],
                                    subject_code=cr["subject_code"],
                                    faculty_name=cr["faculty"],
                                    classroom_id=classroom.id if classroom else None,
                                    room_raw_text=cr["room_raw"],
                                    is_lab=cr["is_lab"],
                                    is_approved=False if upload_id else True, # Review required for new uploads
                                    is_deleted=False
                                )
                                db.add(entry)
                                parsed_entries.append(entry)

            db.commit()

            # Detect conflicts
            conflicts = ConflictService.detect_and_record_conflicts(db, upload_id)

            if upload_id:
                upload_rec = db.query(Upload).filter(Upload.id == upload_id).first()
                if upload_rec:
                    upload_rec.status = "REVIEW_REQUIRED"
                    upload_rec.parsed_records_count = len(parsed_entries)
                    upload_rec.error_log = "; ".join(errors) if errors else None
                    db.commit()

            return {
                "success": True,
                "parsed_count": len(parsed_entries),
                "conflicts_count": len(conflicts),
                "errors": errors
            }

        except Exception as ex:
            db.rollback()
            return {
                "success": False,
                "parsed_count": 0,
                "conflicts_count": 0,
                "errors": [str(ex)]
            }
