from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
import datetime

# --- Building & Classroom Schemas ---

class BuildingBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    total_floors: int = 7

class BuildingResponse(BuildingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime.datetime] = None

class ClassroomBase(BaseModel):
    room_number: str
    building_id: int
    floor: int
    floor_label: str
    room_type: str
    capacity: int = 60
    amenities: List[str] = []
    is_active: bool = True
    notes: Optional[str] = None

class ClassroomResponse(ClassroomBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    building_name: Optional[str] = None
    building_code: Optional[str] = None


# --- Timetable Entry Schemas ---

class TimetableEntryBase(BaseModel):
    department_code: str
    course_name: Optional[str] = None
    semester: int
    section: str = "B1"
    batch: Optional[str] = None
    day_of_week: str
    start_time: str
    end_time: str
    subject_name: str
    subject_code: Optional[str] = None
    faculty_name: str
    classroom_id: Optional[int] = None
    room_raw_text: str
    is_lab: bool = False
    is_approved: bool = True
    is_deleted: bool = False

class TimetableEntryCreate(TimetableEntryBase):
    upload_id: Optional[int] = None

class TimetableEntryUpdate(BaseModel):
    department_code: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    batch: Optional[str] = None
    day_of_week: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    faculty_name: Optional[str] = None
    classroom_id: Optional[int] = None
    room_raw_text: Optional[str] = None
    is_lab: Optional[bool] = None
    is_approved: Optional[bool] = None
    is_deleted: Optional[bool] = None

class TimetableEntryResponse(TimetableEntryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    upload_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None


# --- Live Availability & Schedule Schemas ---

class CurrentClassInfo(BaseModel):
    subject: str
    subject_code: Optional[str] = None
    faculty: str
    department: str
    semester: int
    section: str
    batch: Optional[str] = None
    start_time: str
    end_time: str
    is_lab: bool = False

class NextClassInfo(BaseModel):
    subject: str
    subject_code: Optional[str] = None
    faculty: str
    department: str
    semester: int
    section: str
    batch: Optional[str] = None
    start_time: str
    end_time: str
    starts_in_minutes: int
    is_lab: bool = False

class TimelineBlock(BaseModel):
    start_time: str
    end_time: str
    status: str # "OCCUPIED", "AVAILABLE", "BREAK"
    subject: Optional[str] = None
    faculty: Optional[str] = None
    section: Optional[str] = None
    is_lab: bool = False
    is_current: bool = False

class ClassroomAvailabilityResponse(BaseModel):
    classroom_id: int
    room_number: str
    building_name: str
    building_code: str
    floor: int
    floor_label: str
    room_type: str
    capacity: int
    amenities: List[str]
    status: str # "AVAILABLE", "OCCUPIED", "FREE_SOON", "NO_DATA"
    current_time_ist: str
    day_of_week: str
    free_until: Optional[str] = None
    remaining_free_minutes: Optional[int] = None
    occupied_until: Optional[str] = None
    current_class: Optional[CurrentClassInfo] = None
    next_class: Optional[NextClassInfo] = None
    total_free_minutes_today: int
    timeline_blocks: List[TimelineBlock] = []

class LiveAvailabilityOverview(BaseModel):
    current_time_ist: str
    day_of_week: str
    date_ist: str
    is_simulated: bool
    total_classrooms: int
    available_now_count: int
    occupied_count: int
    free_soon_count: int
    classrooms: List[ClassroomAvailabilityResponse]


# --- Search Schemas ---

class SearchRoomsRequest(BaseModel):
    day_of_week: Optional[str] = None
    start_time: str
    end_time: str
    building_code: Optional[str] = None
    floor: Optional[int] = None
    room_type: Optional[str] = None
    min_capacity: Optional[int] = None

class SearchRoomResult(BaseModel):
    classroom_id: int
    room_number: str
    building_name: str
    building_code: str
    floor: int
    floor_label: str
    room_type: str
    capacity: int
    amenities: List[str]
    is_completely_free: bool
    available_window_start: str
    available_window_end: str
    conflicts_count: int = 0
    next_class: Optional[NextClassInfo] = None


# --- Exception Schemas ---

class ExceptionCreate(BaseModel):
    exception_date: str # "YYYY-MM-DD"
    classroom_id: int
    exception_type: str # "HOLIDAY", "CANCELLED_CLASS", "EXTRA_CLASS", "ROOM_CHANGE"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    reason: Optional[str] = None
    alternate_classroom_id: Optional[int] = None

class ExceptionResponse(ExceptionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    room_number: Optional[str] = None
    alternate_room_number: Optional[str] = None
    created_at: Optional[datetime.datetime] = None


# --- Conflict Schemas ---

class ConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    conflict_type: str
    description: str
    entry_ids: List[int]
    severity: str
    resolved: bool
    resolution_notes: Optional[str] = None
    detected_at: Optional[datetime.datetime] = None
    affected_entries: List[TimetableEntryResponse] = []


# --- Upload & Review Schemas ---

class UploadResponse(BaseModel):
    upload_id: int
    filename: str
    status: str
    parsed_records_count: int
    conflicts_detected_count: int
    error_log: Optional[str] = None
    entries: List[TimetableEntryResponse] = []

class TimetableReviewResponse(BaseModel):
    upload: UploadResponse
    entries: List[TimetableEntryResponse]
    conflicts: List[ConflictResponse]
    unmapped_rooms: List[str]
