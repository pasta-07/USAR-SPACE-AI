import datetime
import pytz
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.app.models.models import Classroom, TimetableEntry, TimetableException, Building
from backend.app.schemas.schemas import (
    ClassroomAvailabilityResponse,
    CurrentClassInfo,
    NextClassInfo,
    TimelineBlock,
    LiveAvailabilityOverview
)

IST_TZ = pytz.timezone("Asia/Kolkata")

def parse_time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' string to total minutes since midnight."""
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def minutes_to_time_str(minutes: int) -> str:
    """Convert total minutes since midnight to 'HH:MM' string."""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def get_current_ist_datetime(simulated_time: Optional[str] = None, simulated_day: Optional[str] = None) -> Tuple[datetime.datetime, str, str, str, bool]:
    """
    Returns (now_dt, time_str 'HH:MM', day_of_week 'Monday', date_str 'YYYY-MM-DD', is_simulated).
    """
    if simulated_time:
        try:
            # Handle ISO string or 'YYYY-MM-DD HH:MM' or 'HH:MM'
            if "T" in simulated_time:
                now_dt = datetime.datetime.fromisoformat(simulated_time)
                if now_dt.tzinfo is None:
                    now_dt = IST_TZ.localize(now_dt)
                else:
                    now_dt = now_dt.astimezone(IST_TZ)
            elif " " in simulated_time:
                now_dt = datetime.datetime.strptime(simulated_time, "%Y-%m-%d %H:%M")
                now_dt = IST_TZ.localize(now_dt)
            elif ":" in simulated_time:
                # Only time provided, use today's date
                today_ist = datetime.datetime.now(IST_TZ)
                h, m = map(int, simulated_time.split(":")[:2])
                now_dt = today_ist.replace(hour=h, minute=m, second=0, microsecond=0)
            else:
                now_dt = datetime.datetime.now(IST_TZ)
            
            day_name = simulated_day if simulated_day else now_dt.strftime("%A")
            return now_dt, now_dt.strftime("%H:%M"), day_name, now_dt.strftime("%Y-%m-%d"), True
        except Exception:
            pass

    now_ist = datetime.datetime.now(IST_TZ)
    day_name = simulated_day if simulated_day else now_ist.strftime("%A")
    return now_ist, now_ist.strftime("%H:%M"), day_name, now_ist.strftime("%Y-%m-%d"), False

class AvailabilityService:
    @staticmethod
    def get_classroom_availability(
        db: Session,
        classroom: Classroom,
        target_dt: datetime.datetime,
        current_time_str: str,
        day_of_week: str,
        date_str: str
    ) -> ClassroomAvailabilityResponse:
        current_minutes = parse_time_to_minutes(current_time_str)

        # 1. Fetch entries for this classroom on this day
        entries = db.query(TimetableEntry).filter(
            TimetableEntry.classroom_id == classroom.id,
            TimetableEntry.day_of_week == day_of_week,
            TimetableEntry.is_approved == True,
            TimetableEntry.is_deleted == False
        ).order_by(TimetableEntry.start_time).all()

        # 2. Fetch exceptions for today
        exceptions = db.query(TimetableException).filter(
            or_(
                TimetableException.classroom_id == classroom.id,
                TimetableException.alternate_classroom_id == classroom.id
            ),
            TimetableException.exception_date == date_str
        ).all()

        # Check if full day holiday
        is_holiday = any(e.exception_type == "HOLIDAY" and (not e.start_time or e.start_time <= "08:00") for e in exceptions)

        # Active scheduled intervals: list of dicts with start_min, end_min, entry
        active_intervals = []
        if not is_holiday:
            for entry in entries:
                start_min = parse_time_to_minutes(entry.start_time)
                end_min = parse_time_to_minutes(entry.end_time)

                # Check if this specific entry is cancelled by an exception
                is_cancelled = any(
                    e.exception_type == "CANCELLED_CLASS" and 
                    e.classroom_id == classroom.id and
                    e.start_time == entry.start_time
                    for e in exceptions
                )
                if is_cancelled:
                    continue

                # Check if moved away to another room
                is_moved_out = any(
                    e.exception_type == "ROOM_CHANGE" and
                    e.classroom_id == classroom.id and
                    e.start_time == entry.start_time
                    for e in exceptions
                )
                if is_moved_out:
                    continue

                active_intervals.append({
                    "start_min": start_min,
                    "end_min": end_min,
                    "start_time": entry.start_time,
                    "end_time": entry.end_time,
                    "entry": entry
                })

            # Add extra classes or room changes moved INTO this classroom
            for exc in exceptions:
                if exc.exception_type in ["EXTRA_CLASS", "ROOM_CHANGE"] and (exc.classroom_id == classroom.id or exc.alternate_classroom_id == classroom.id):
                    if exc.start_time and exc.end_time:
                        s_min = parse_time_to_minutes(exc.start_time)
                        e_min = parse_time_to_minutes(exc.end_time)
                        active_intervals.append({
                            "start_min": s_min,
                            "end_min": e_min,
                            "start_time": exc.start_time,
                            "end_time": exc.end_time,
                            "entry": None,
                            "reason": exc.reason or "Special Scheduled Session"
                        })

        # Sort intervals by start_min
        active_intervals.sort(key=lambda x: x["start_min"])

        # Determine current status
        current_occupied_interval = None
        for item in active_intervals:
            if item["start_min"] <= current_minutes < item["end_min"]:
                current_occupied_interval = item
                break

        # Calculate next class
        next_interval = None
        for item in active_intervals:
            if item["start_min"] > current_minutes:
                next_interval = item
                break

        # Status & free duration calculation
        college_end_minutes = 18 * 60 # 6:00 PM
        status = "AVAILABLE"
        free_until = None
        remaining_free_minutes = None
        occupied_until = None
        current_class_info = None
        next_class_info = None

        if current_occupied_interval:
            status = "OCCUPIED"
            # Find the continuous occupied block (merge consecutive back-to-back classes)
            continuous_end_min = current_occupied_interval["end_min"]
            curr_idx = active_intervals.index(current_occupied_interval)
            for subsequent in active_intervals[curr_idx + 1:]:
                if subsequent["start_min"] <= continuous_end_min:
                    continuous_end_min = max(continuous_end_min, subsequent["end_min"])
                else:
                    break

            occupied_until = minutes_to_time_str(continuous_end_min)
            remaining_free_minutes = 0

            # If class ends within 60 minutes, status indicator can be highlighted as FREE_SOON
            entry_obj = current_occupied_interval.get("entry")
            if entry_obj:
                current_class_info = CurrentClassInfo(
                    subject=entry_obj.subject_name,
                    subject_code=entry_obj.subject_code,
                    faculty=entry_obj.faculty_name,
                    department=entry_obj.department_code,
                    semester=entry_obj.semester,
                    section=entry_obj.section,
                    batch=entry_obj.batch,
                    start_time=entry_obj.start_time,
                    end_time=entry_obj.end_time,
                    is_lab=entry_obj.is_lab
                )
            else:
                current_class_info = CurrentClassInfo(
                    subject=current_occupied_interval.get("reason", "Special Class"),
                    subject_code=None,
                    faculty="Faculty",
                    department="USAR",
                    semester=0,
                    section="All",
                    batch=None,
                    start_time=current_occupied_interval["start_time"],
                    end_time=current_occupied_interval["end_time"],
                    is_lab=False
                )
        else:
            status = "AVAILABLE"
            if next_interval:
                free_until = next_interval["start_time"]
                remaining_free_minutes = max(0, next_interval["start_min"] - current_minutes)
            else:
                if current_minutes < college_end_minutes:
                    free_until = "18:00"
                    remaining_free_minutes = college_end_minutes - current_minutes
                else:
                    free_until = "Tomorrow"
                    remaining_free_minutes = 0

        if next_interval:
            next_entry = next_interval.get("entry")
            if next_entry:
                next_class_info = NextClassInfo(
                    subject=next_entry.subject_name,
                    subject_code=next_entry.subject_code,
                    faculty=next_entry.faculty_name,
                    department=next_entry.department_code,
                    semester=next_entry.semester,
                    section=next_entry.section,
                    batch=next_entry.batch,
                    start_time=next_entry.start_time,
                    end_time=next_entry.end_time,
                    starts_in_minutes=max(0, next_interval["start_min"] - current_minutes),
                    is_lab=next_entry.is_lab
                )
            else:
                next_class_info = NextClassInfo(
                    subject=next_interval.get("reason", "Special Class"),
                    subject_code=None,
                    faculty="Faculty",
                    department="USAR",
                    semester=0,
                    section="All",
                    batch=None,
                    start_time=next_interval["start_time"],
                    end_time=next_interval["end_time"],
                    starts_in_minutes=max(0, next_interval["start_min"] - current_minutes),
                    is_lab=False
                )

        # Timeline blocks construction for today from 08:00 to 18:00
        # Standard hourly slots
        slots = [
            ("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"),
            ("11:00", "12:00"), ("12:00", "13:00"), ("13:00", "14:00"),
            ("14:00", "15:00"), ("15:00", "16:00"), ("16:00", "17:00"),
            ("17:00", "18:00")
        ]
        timeline_blocks = []
        total_free_minutes = 0

        for slot_start, slot_end in slots:
            s_min = parse_time_to_minutes(slot_start)
            e_min = parse_time_to_minutes(slot_end)
            is_cur = s_min <= current_minutes < e_min

            # Check if this slot overlaps with any active interval
            matching_interval = None
            for item in active_intervals:
                if not (item["end_min"] <= s_min or item["start_min"] >= e_min):
                    matching_interval = item
                    break

            if matching_interval:
                entry_ref = matching_interval.get("entry")
                timeline_blocks.append(TimelineBlock(
                    start_time=slot_start,
                    end_time=slot_end,
                    status="OCCUPIED",
                    subject=entry_ref.subject_name if entry_ref else matching_interval.get("reason"),
                    faculty=entry_ref.faculty_name if entry_ref else None,
                    section=f"{entry_ref.department_code}-{entry_ref.semester}{entry_ref.section}" if entry_ref else None,
                    is_lab=entry_ref.is_lab if entry_ref else False,
                    is_current=is_cur
                ))
            else:
                total_free_minutes += 60
                timeline_blocks.append(TimelineBlock(
                    start_time=slot_start,
                    end_time=slot_end,
                    status="AVAILABLE",
                    subject=None,
                    faculty=None,
                    section=None,
                    is_lab=False,
                    is_current=is_cur
                ))

        return ClassroomAvailabilityResponse(
            classroom_id=classroom.id,
            room_number=classroom.room_number,
            building_name=classroom.building.name if classroom.building else "Main Campus",
            building_code=classroom.building.code if classroom.building else "BLOCK_A",
            floor=classroom.floor,
            floor_label=classroom.floor_label,
            room_type=classroom.room_type,
            capacity=classroom.capacity,
            amenities=classroom.amenities or [],
            status=status,
            current_time_ist=current_time_str,
            day_of_week=day_of_week,
            free_until=free_until,
            remaining_free_minutes=remaining_free_minutes,
            occupied_until=occupied_until,
            current_class=current_class_info,
            next_class=next_class_info,
            total_free_minutes_today=total_free_minutes,
            timeline_blocks=timeline_blocks
        )

    @classmethod
    def get_live_overview(
        cls,
        db: Session,
        simulated_time: Optional[str] = None,
        simulated_day: Optional[str] = None,
        building_code: Optional[str] = None,
        floor: Optional[int] = None,
        room_type: Optional[str] = None
    ) -> LiveAvailabilityOverview:
        now_dt, time_str, day_name, date_str, is_simulated = get_current_ist_datetime(simulated_time, simulated_day)

        query = db.query(Classroom).filter(Classroom.is_active == True)
        if building_code:
            query = query.join(Building).filter(Building.code == building_code)
        if floor is not None:
            query = query.filter(Classroom.floor == floor)
        if room_type:
            query = query.filter(Classroom.room_type == room_type)

        classrooms = query.order_by(Classroom.room_number).all()

        classroom_responses = []
        available_count = 0
        occupied_count = 0
        free_soon_count = 0

        current_min = parse_time_to_minutes(time_str)

        for room in classrooms:
            resp = cls.get_classroom_availability(db, room, now_dt, time_str, day_name, date_str)
            classroom_responses.append(resp)

            if resp.status == "AVAILABLE":
                available_count += 1
            elif resp.status == "OCCUPIED":
                occupied_count += 1
                # Check if it becomes free within 60 minutes
                if resp.occupied_until:
                    occ_end = parse_time_to_minutes(resp.occupied_until)
                    if 0 < (occ_end - current_min) <= 60:
                        free_soon_count += 1

        return LiveAvailabilityOverview(
            current_time_ist=time_str,
            day_of_week=day_name,
            date_ist=date_str,
            is_simulated=is_simulated,
            total_classrooms=len(classrooms),
            available_now_count=available_count,
            occupied_count=occupied_count,
            free_soon_count=free_soon_count,
            classrooms=classroom_responses
        )
