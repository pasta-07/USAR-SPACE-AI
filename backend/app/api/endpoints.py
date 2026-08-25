import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.app.database.connection import get_db
from backend.app.models.models import (
    Building, Classroom, Department, Upload, TimetableEntry, TimetableException, Conflict
)
from backend.app.schemas.schemas import (
    BuildingResponse,
    ClassroomResponse,
    ClassroomAvailabilityResponse,
    LiveAvailabilityOverview,
    SearchRoomsRequest,
    SearchRoomResult,
    TimetableEntryResponse,
    TimetableEntryCreate,
    TimetableEntryUpdate,
    ExceptionCreate,
    ExceptionResponse,
    ConflictResponse,
    UploadResponse,
    TimetableReviewResponse
)
from backend.app.services.availability_service import AvailabilityService, get_current_ist_datetime
from backend.app.services.timetable_service import TimetableService
from backend.app.services.conflict_service import ConflictService
from backend.app.services.pdf_parser_service import PDFParserService
from backend.app.database.seed_data import seed_database

router = APIRouter(prefix="/api")

# --- Classrooms & Live Availability ---

@router.get("/classrooms/available-now", response_model=LiveAvailabilityOverview)
def get_available_now(
    simulated_time: Optional[str] = Query(None, description="Simulated ISO or HH:MM time"),
    simulated_day: Optional[str] = Query(None, description="Simulated Day name e.g. Monday, Wednesday"),
    building_code: Optional[str] = Query(None, description="Filter by Building code"),
    floor: Optional[int] = Query(None, description="Filter by floor number"),
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    db: Session = Depends(get_db)
):
    return AvailabilityService.get_live_overview(
        db=db,
        simulated_time=simulated_time,
        simulated_day=simulated_day,
        building_code=building_code,
        floor=floor,
        room_type=room_type
    )

@router.get("/classrooms/{classroom_id}/status", response_model=ClassroomAvailabilityResponse)
def get_classroom_status(
    classroom_id: int,
    simulated_time: Optional[str] = None,
    simulated_day: Optional[str] = None,
    db: Session = Depends(get_db)
):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    now_dt, time_str, day_name, date_str, _ = get_current_ist_datetime(simulated_time, simulated_day)
    return AvailabilityService.get_classroom_availability(
        db=db,
        classroom=classroom,
        target_dt=now_dt,
        current_time_str=time_str,
        day_of_week=day_name,
        date_str=date_str
    )

@router.get("/classrooms/{classroom_id}/schedule")
def get_classroom_schedule(classroom_id: int, db: Session = Depends(get_db)):
    schedule = TimetableService.get_classroom_weekly_schedule(db, classroom_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return schedule

@router.get("/classrooms/search", response_model=List[SearchRoomResult])
def search_classrooms(
    start_time: str = Query(..., description="Start time e.g. 14:00"),
    end_time: str = Query(..., description="End time e.g. 16:00"),
    day_of_week: Optional[str] = Query(None, description="Day of week"),
    building_code: Optional[str] = None,
    floor: Optional[int] = None,
    room_type: Optional[str] = None,
    min_capacity: Optional[int] = None,
    simulated_time: Optional[str] = None,
    simulated_day: Optional[str] = None,
    db: Session = Depends(get_db)
):
    req = SearchRoomsRequest(
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        building_code=building_code,
        floor=floor,
        room_type=room_type,
        min_capacity=min_capacity
    )
    return TimetableService.search_available_classrooms(
        db=db,
        request=req,
        simulated_time=simulated_time,
        simulated_day=simulated_day
    )


# --- Buildings & Campus Map ---

@router.get("/buildings", response_model=List[BuildingResponse])
def get_buildings(db: Session = Depends(get_db)):
    return db.query(Building).all()

@router.get("/buildings/{building_id}/classrooms")
def get_building_classrooms(
    building_id: int,
    simulated_time: Optional[str] = None,
    simulated_day: Optional[str] = None,
    db: Session = Depends(get_db)
):
    bldg = db.query(Building).filter(Building.id == building_id).first()
    if not bldg:
        raise HTTPException(status_code=404, detail="Building not found")

    now_dt, time_str, day_name, date_str, is_sim = get_current_ist_datetime(simulated_time, simulated_day)
    
    # Group classrooms by floor
    classrooms = db.query(Classroom).filter(Classroom.building_id == building_id, Classroom.is_active == True).order_by(Classroom.floor, Classroom.room_number).all()

    floors_map = {}
    for room in classrooms:
        avail = AvailabilityService.get_classroom_availability(db, room, now_dt, time_str, day_name, date_str)
        fl_key = room.floor
        if fl_key not in floors_map:
            floors_map[fl_key] = {
                "floor_number": room.floor,
                "floor_label": room.floor_label,
                "classrooms": []
            }
        floors_map[fl_key]["classrooms"].append(avail)

    sorted_floors = sorted(floors_map.values(), key=lambda x: x["floor_number"])

    return {
        "building_id": bldg.id,
        "building_name": bldg.name,
        "building_code": bldg.code,
        "total_floors": bldg.total_floors,
        "current_time_ist": time_str,
        "day_of_week": day_name,
        "floors": sorted_floors
    }


# --- Admin: PDF Upload & Processing ---

@router.post("/admin/upload-timetable")
async def upload_timetable_pdf(
    file: UploadFile = File(...),
    academic_year: str = Form("2026-27"),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save to temp file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create upload record
    upload_rec = Upload(
        filename=file.filename,
        file_path=file_path,
        status="PROCESSING",
        academic_year=academic_year
    )
    db.add(upload_rec)
    db.commit()
    db.refresh(upload_rec)

    # Run parser
    res = PDFParserService.parse_pdf_file(db, file_path, upload_id=upload_rec.id)

    # Re-fetch upload
    db.refresh(upload_rec)

    return {
        "upload_id": upload_rec.id,
        "filename": upload_rec.filename,
        "status": upload_rec.status,
        "parsed_records_count": res["parsed_count"],
        "conflicts_detected_count": res["conflicts_count"],
        "errors": res["errors"]
    }

@router.get("/admin/timetable-review/{upload_id}", response_model=TimetableReviewResponse)
def get_timetable_review(upload_id: int, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    entries = db.query(TimetableEntry).filter(
        TimetableEntry.upload_id == upload_id,
        TimetableEntry.is_deleted == False
    ).order_by(TimetableEntry.day_of_week, TimetableEntry.start_time).all()

    entry_ids = [e.id for e in entries]
    
    # Conflicts affecting these entries
    conflicts = ConflictService.get_all_conflicts(db, resolved=False)
    # Filter conflicts that touch any of these entries
    rel_conflicts = [c for c in conflicts if any(eid in entry_ids for eid in c.entry_ids)]

    unmapped = [e.room_raw_text for e in entries if not e.classroom_id]
    unmapped = list(set(unmapped))

    return TimetableReviewResponse(
        upload=UploadResponse(
            upload_id=upload.id,
            filename=upload.filename,
            status=upload.status,
            parsed_records_count=len(entries),
            conflicts_detected_count=len(rel_conflicts),
            error_log=upload.error_log,
            entries=[TimetableEntryResponse.from_orm(e) for e in entries]
        ),
        entries=[TimetableEntryResponse.from_orm(e) for e in entries],
        conflicts=rel_conflicts,
        unmapped_rooms=unmapped
    )

@router.post("/admin/approve-upload/{upload_id}")
def approve_upload(upload_id: int, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Mark all entries approved
    db.query(TimetableEntry).filter(
        TimetableEntry.upload_id == upload_id,
        TimetableEntry.is_deleted == False
    ).update({"is_approved": True})

    upload.status = "APPROVED"
    db.commit()

    # Re-run conflict detection
    ConflictService.detect_and_record_conflicts(db)

    return {"message": "Timetable approved and published successfully", "upload_id": upload_id}


# --- Admin: Timetable Entries CRUD ---

@router.post("/admin/timetable-entries", response_model=TimetableEntryResponse)
def create_timetable_entry(entry: TimetableEntryCreate, db: Session = Depends(get_db)):
    # Match classroom
    room = db.query(Classroom).filter(Classroom.room_number.ilike(entry.room_raw_text.strip())).first()
    classroom_id = room.id if room else entry.classroom_id

    new_entry = TimetableEntry(
        upload_id=entry.upload_id,
        department_code=entry.department_code,
        course_name=entry.course_name,
        semester=entry.semester,
        section=entry.section,
        batch=entry.batch,
        day_of_week=entry.day_of_week,
        start_time=entry.start_time,
        end_time=entry.end_time,
        subject_name=entry.subject_name,
        subject_code=entry.subject_code,
        faculty_name=entry.faculty_name,
        classroom_id=classroom_id,
        room_raw_text=entry.room_raw_text,
        is_lab=entry.is_lab,
        is_approved=entry.is_approved,
        is_deleted=False
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    # Check conflicts
    ConflictService.detect_and_record_conflicts(db)
    return new_entry

@router.put("/admin/timetable-entries/{entry_id}", response_model=TimetableEntryResponse)
def update_timetable_entry(entry_id: int, update_data: TimetableEntryUpdate, db: Session = Depends(get_db)):
    entry = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")

    for k, v in update_data.dict(exclude_unset=True).items():
        setattr(entry, k, v)

    if update_data.room_raw_text:
        room = db.query(Classroom).filter(Classroom.room_number.ilike(update_data.room_raw_text.strip())).first()
        if room:
            entry.classroom_id = room.id

    db.commit()
    db.refresh(entry)

    # Re-scan conflicts
    ConflictService.detect_and_record_conflicts(db)
    return entry

@router.delete("/admin/timetable-entries/{entry_id}")
def delete_timetable_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")

    entry.is_deleted = True
    db.commit()

    ConflictService.detect_and_record_conflicts(db)
    return {"message": "Timetable entry deleted successfully", "id": entry_id}


# --- Admin: Conflicts Management ---

@router.get("/admin/conflicts", response_model=List[ConflictResponse])
def get_conflicts(resolved: Optional[bool] = None, db: Session = Depends(get_db)):
    return ConflictService.get_all_conflicts(db, resolved=resolved)

@router.post("/admin/conflicts/{conflict_id}/resolve")
def resolve_conflict(conflict_id: int, notes: Optional[str] = Query(None), db: Session = Depends(get_db)):
    ok = ConflictService.resolve_conflict(db, conflict_id, notes)
    if not ok:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return {"message": "Conflict marked as resolved", "conflict_id": conflict_id}


# --- Admin: Exceptions Management ---

@router.get("/admin/exceptions", response_model=List[ExceptionResponse])
def get_exceptions(db: Session = Depends(get_db)):
    exceptions = db.query(TimetableException).order_by(TimetableException.exception_date.desc()).all()
    res = []
    for exc in exceptions:
        res.append(ExceptionResponse(
            id=exc.id,
            exception_date=exc.exception_date,
            classroom_id=exc.classroom_id,
            exception_type=exc.exception_type,
            start_time=exc.start_time,
            end_time=exc.end_time,
            reason=exc.reason,
            alternate_classroom_id=exc.alternate_classroom_id,
            room_number=exc.classroom.room_number if exc.classroom else None,
            alternate_room_number=exc.alternate_classroom.room_number if exc.alternate_classroom else None,
            created_at=exc.created_at
        ))
    return res

@router.post("/admin/exceptions", response_model=ExceptionResponse)
def create_exception(payload: ExceptionCreate, db: Session = Depends(get_db)):
    room = db.query(Classroom).filter(Classroom.id == payload.classroom_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    new_exc = TimetableException(
        exception_date=payload.exception_date,
        classroom_id=payload.classroom_id,
        exception_type=payload.exception_type,
        start_time=payload.start_time,
        end_time=payload.end_time,
        reason=payload.reason,
        alternate_classroom_id=payload.alternate_classroom_id
    )
    db.add(new_exc)
    db.commit()
    db.refresh(new_exc)

    return ExceptionResponse(
        id=new_exc.id,
        exception_date=new_exc.exception_date,
        classroom_id=new_exc.classroom_id,
        exception_type=new_exc.exception_type,
        start_time=new_exc.start_time,
        end_time=new_exc.end_time,
        reason=new_exc.reason,
        alternate_classroom_id=new_exc.alternate_classroom_id,
        room_number=new_exc.classroom.room_number if new_exc.classroom else None,
        alternate_room_number=new_exc.alternate_classroom.room_number if new_exc.alternate_classroom else None,
        created_at=new_exc.created_at
    )

@router.delete("/admin/exceptions/{exception_id}")
def delete_exception(exception_id: int, db: Session = Depends(get_db)):
    exc = db.query(TimetableException).filter(TimetableException.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    db.delete(exc)
    db.commit()
    return {"message": "Exception deleted successfully", "id": exception_id}


# --- Analytics & Overview Stats ---

@router.get("/stats/overview")
def get_stats_overview(db: Session = Depends(get_db)):
    return TimetableService.get_campus_analytics(db)

@router.post("/seed/reset")
def reset_and_seed(db: Session = Depends(get_db)):
    # Clear and re-seed
    db.query(Conflict).delete()
    db.query(TimetableException).delete()
    db.query(TimetableEntry).delete()
    db.query(Upload).delete()
    db.commit()
    seed_database(db)
    return {"message": "Database reset and re-seeded with complete USAR timetable dataset successfully"}
