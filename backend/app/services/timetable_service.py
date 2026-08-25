import datetime
import pytz
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.app.models.models import Classroom, TimetableEntry, Building, Department, TimetableException
from backend.app.schemas.schemas import (
    SearchRoomsRequest,
    SearchRoomResult,
    NextClassInfo,
    TimetableEntryResponse
)
from backend.app.services.availability_service import (
    parse_time_to_minutes,
    minutes_to_time_str,
    get_current_ist_datetime,
    IST_TZ
)

class TimetableService:
    @staticmethod
    def search_available_classrooms(
        db: Session,
        request: SearchRoomsRequest,
        simulated_time: Optional[str] = None,
        simulated_day: Optional[str] = None
    ) -> List[SearchRoomResult]:
        """
        Finds all classrooms that are completely free during [start_time, end_time] on day_of_week.
        """
        now_dt, time_str, default_day, date_str, is_sim = get_current_ist_datetime(simulated_time, simulated_day)
        day_of_week = request.day_of_week if request.day_of_week else default_day

        req_start_min = parse_time_to_minutes(request.start_time)
        req_end_min = parse_time_to_minutes(request.end_time)

        # Base query for classrooms
        query = db.query(Classroom).filter(Classroom.is_active == True)
        if request.building_code:
            query = query.join(Building).filter(Building.code == request.building_code)
        if request.floor is not None:
            query = query.filter(Classroom.floor == request.floor)
        if request.room_type:
            query = query.filter(Classroom.room_type == request.room_type)
        if request.min_capacity:
            query = query.filter(Classroom.capacity >= request.min_capacity)

        classrooms = query.all()
        results = []

        for room in classrooms:
            # 1. Fetch entries for this room on this day
            entries = db.query(TimetableEntry).filter(
                TimetableEntry.classroom_id == room.id,
                TimetableEntry.day_of_week == day_of_week,
                TimetableEntry.is_approved == True,
                TimetableEntry.is_deleted == False
            ).order_by(TimetableEntry.start_time).all()

            # 2. Fetch exceptions for today's date
            exceptions = db.query(TimetableException).filter(
                or_(
                    TimetableException.classroom_id == room.id,
                    TimetableException.alternate_classroom_id == room.id
                ),
                TimetableException.exception_date == date_str
            ).all()

            # Check full holiday
            is_holiday = any(e.exception_type == "HOLIDAY" and (not e.start_time or e.start_time <= "08:00") for e in exceptions)

            # Build list of active occupied ranges
            occupied_ranges = []
            if not is_holiday:
                for entry in entries:
                    # Check cancellation
                    if any(e.exception_type == "CANCELLED_CLASS" and e.start_time == entry.start_time for e in exceptions):
                        continue
                    # Check room change away
                    if any(e.exception_type == "ROOM_CHANGE" and e.classroom_id == room.id and e.start_time == entry.start_time for e in exceptions):
                        continue

                    occupied_ranges.append({
                        "start_min": parse_time_to_minutes(entry.start_time),
                        "end_min": parse_time_to_minutes(entry.end_time),
                        "entry": entry
                    })

                # Check extra classes / incoming room changes
                for exc in exceptions:
                    if exc.exception_type in ["EXTRA_CLASS", "ROOM_CHANGE"] and (exc.classroom_id == room.id or exc.alternate_classroom_id == room.id):
                        if exc.start_time and exc.end_time:
                            occupied_ranges.append({
                                "start_min": parse_time_to_minutes(exc.start_time),
                                "end_min": parse_time_to_minutes(exc.end_time),
                                "entry": None
                            })

            occupied_ranges.sort(key=lambda x: x["start_min"])

            # Check if any occupied range overlaps with the requested interval [req_start_min, req_end_min]
            clash = False
            for r in occupied_ranges:
                if not (r["end_min"] <= req_start_min or r["start_min"] >= req_end_min):
                    clash = True
                    break

            if not clash:
                # Find available window boundary
                # Window start: latest end_time of preceding class before req_start_min (or 08:00)
                window_start_min = 8 * 60 # 08:00
                for r in occupied_ranges:
                    if r["end_min"] <= req_start_min:
                        window_start_min = max(window_start_min, r["end_min"])

                # Window end: earliest start_time of subsequent class after req_end_min (or 18:00)
                window_end_min = 18 * 60 # 18:00
                next_class_after_req = None
                for r in occupied_ranges:
                    if r["start_min"] >= req_end_min:
                        window_end_min = min(window_end_min, r["start_min"])
                        if not next_class_after_req:
                            next_class_after_req = r
                        break

                next_class_info = None
                if next_class_after_req and next_class_after_req.get("entry"):
                    e = next_class_after_req["entry"]
                    next_class_info = NextClassInfo(
                        subject=e.subject_name,
                        subject_code=e.subject_code,
                        faculty=e.faculty_name,
                        department=e.department_code,
                        semester=e.semester,
                        section=e.section,
                        batch=e.batch,
                        start_time=e.start_time,
                        end_time=e.end_time,
                        starts_in_minutes=max(0, next_class_after_req["start_min"] - req_start_min),
                        is_lab=e.is_lab
                    )

                results.append(SearchRoomResult(
                    classroom_id=room.id,
                    room_number=room.room_number,
                    building_name=room.building.name if room.building else "Block A",
                    building_code=room.building.code if room.building else "BLOCK_A",
                    floor=room.floor,
                    floor_label=room.floor_label,
                    room_type=room.room_type,
                    capacity=room.capacity,
                    amenities=room.amenities or [],
                    is_completely_free=True,
                    available_window_start=minutes_to_time_str(window_start_min),
                    available_window_end=minutes_to_time_str(window_end_min),
                    conflicts_count=0,
                    next_class=next_class_info
                ))

        # Sort by room_number
        results.sort(key=lambda x: x.room_number)
        return results

    @staticmethod
    def get_classroom_weekly_schedule(db: Session, classroom_id: int) -> Dict[str, Any]:
        """
        Returns complete weekly matrix (Monday-Friday) for a given classroom.
        """
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if not classroom:
            return {}

        entries = db.query(TimetableEntry).filter(
            TimetableEntry.classroom_id == classroom_id,
            TimetableEntry.is_approved == True,
            TimetableEntry.is_deleted == False
        ).order_by(TimetableEntry.start_time).all()

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        weekly_data = {d: [] for d in days}

        for entry in entries:
            if entry.day_of_week in weekly_data:
                weekly_data[entry.day_of_week].append({
                    "id": entry.id,
                    "department_code": entry.department_code,
                    "semester": entry.semester,
                    "section": entry.section,
                    "batch": entry.batch,
                    "subject_name": entry.subject_name,
                    "subject_code": entry.subject_code,
                    "faculty_name": entry.faculty_name,
                    "start_time": entry.start_time,
                    "end_time": entry.end_time,
                    "is_lab": entry.is_lab
                })

        return {
            "classroom_id": classroom.id,
            "room_number": classroom.room_number,
            "building": classroom.building.name if classroom.building else "Block A",
            "floor": classroom.floor_label,
            "room_type": classroom.room_type,
            "capacity": classroom.capacity,
            "amenities": classroom.amenities or [],
            "weekly_schedule": weekly_data
        }

    @staticmethod
    def get_campus_analytics(db: Session) -> Dict[str, Any]:
        """
        Returns campus occupancy stats, busiest hours, and branch utilization.
        """
        total_rooms = db.query(Classroom).filter(Classroom.is_active == True).count()
        total_entries = db.query(TimetableEntry).filter(
            TimetableEntry.is_approved == True,
            TimetableEntry.is_deleted == False
        ).count()

        # Department distribution
        depts = db.query(Department).all()
        dept_stats = []
        for d in depts:
            cnt = db.query(TimetableEntry).filter(
                TimetableEntry.department_code == d.code,
                TimetableEntry.is_approved == True,
                TimetableEntry.is_deleted == False
            ).count()
            dept_stats.append({
                "code": d.code,
                "name": d.name,
                "classes_count": cnt
            })

        # Room types count
        rooms = db.query(Classroom).filter(Classroom.is_active == True).all()
        type_counts = {}
        for r in rooms:
            type_counts[r.room_type] = type_counts.get(r.room_type, 0) + 1

        # Peak hours analysis (09:00 to 17:00)
        time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        slot_occupancy = {}
        for slot in time_slots:
            slot_min = parse_time_to_minutes(slot)
            # Find how many entries span this slot across all days
            count = 0
            for entry in db.query(TimetableEntry).filter(TimetableEntry.is_approved == True, TimetableEntry.is_deleted == False).all():
                s = parse_time_to_minutes(entry.start_time)
                e = parse_time_to_minutes(entry.end_time)
                if s <= slot_min < e:
                    count += 1
            # Avg per day (5 days)
            slot_occupancy[slot] = round(count / 5.0, 1)

        return {
            "total_classrooms": total_rooms,
            "total_scheduled_classes": total_entries,
            "departments": dept_stats,
            "room_types_breakdown": type_counts,
            "hourly_average_occupied_rooms": slot_occupancy
        }
