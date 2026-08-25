from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.app.models.models import TimetableEntry, Conflict, Classroom
from backend.app.schemas.schemas import ConflictResponse, TimetableEntryResponse

def time_overlaps(s1: str, e1: str, s2: str, e2: str) -> bool:
    """Returns True if interval (s1, e1) overlaps with (s2, e2)."""
    return not (e1 <= s2 or s1 >= e2)

class ConflictService:
    @staticmethod
    def detect_and_record_conflicts(db: Session, upload_id: int = None) -> List[Conflict]:
        """
        Scans approved/pending timetable entries and detects:
        1. Classroom Double Booking
        2. Faculty Clashes
        3. Duplicate Records
        """
        # Fetch entries to inspect
        query = db.query(TimetableEntry).filter(TimetableEntry.is_deleted == False)
        if upload_id:
            query = query.filter(or_(TimetableEntry.upload_id == upload_id, TimetableEntry.is_approved == True))
        entries = query.all()

        detected_conflicts = []
        n = len(entries)

        # Clear existing un-resolved auto-detected conflicts if scanning all
        if not upload_id:
            db.query(Conflict).filter(Conflict.resolved == False).delete()
            db.commit()

        # Compare pair-wise
        for i in range(n):
            e1 = entries[i]
            for j in range(i + 1, n):
                e2 = entries[j]

                # Must be on the same day
                if e1.day_of_week != e2.day_of_week:
                    continue

                # Must overlap in time
                if not time_overlaps(e1.start_time, e1.end_time, e2.start_time, e2.end_time):
                    continue

                # 1. Check Exact Duplicate
                if (
                    e1.department_code == e2.department_code and
                    e1.semester == e2.semester and
                    e1.section == e2.section and
                    e1.subject_code == e2.subject_code and
                    e1.start_time == e2.start_time and
                    e1.room_raw_text == e2.room_raw_text
                ):
                    desc = f"Duplicate Entry: {e1.subject_name} ({e1.subject_code}) for {e1.department_code}-Sem{e1.semester} {e1.section} at {e1.start_time}-{e1.end_time} in {e1.room_raw_text} on {e1.day_of_week} is logged multiple times."
                    conflict = Conflict(
                        conflict_type="DUPLICATE_ENTRY",
                        description=desc,
                        entry_ids=[e1.id, e2.id],
                        severity="WARNING",
                        resolved=False
                    )
                    db.add(conflict)
                    detected_conflicts.append(conflict)
                    continue

                # 2. Check Classroom Double Booking
                # If classroom_id matches OR room_raw_text matches (normalized)
                if (e1.classroom_id and e2.classroom_id and e1.classroom_id == e2.classroom_id) or (
                    e1.room_raw_text.strip().lower() == e2.room_raw_text.strip().lower()
                ):
                    # Exception: if it's the exact same class/combined section, check
                    if not (e1.subject_code == e2.subject_code and e1.faculty_name == e2.faculty_name):
                        desc = (
                            f"Room Clash in {e1.room_raw_text} on {e1.day_of_week} ({e1.start_time}-{e1.end_time} vs {e2.start_time}-{e2.end_time}): "
                            f"'{e1.subject_name}' ({e1.department_code}-Sem{e1.semester} {e1.section}) overlaps with "
                            f"'{e2.subject_name}' ({e2.department_code}-Sem{e2.semester} {e2.section})."
                        )
                        conflict = Conflict(
                            conflict_type="ROOM_DOUBLE_BOOKING",
                            description=desc,
                            entry_ids=[e1.id, e2.id],
                            severity="CRITICAL",
                            resolved=False
                        )
                        db.add(conflict)
                        detected_conflicts.append(conflict)

                # 3. Check Faculty Clash
                # Normalize faculty names (ignore minor whitespace/case)
                f1 = e1.faculty_name.strip().lower()
                f2 = e2.faculty_name.strip().lower()
                if f1 and f2 and f1 == f2 and f1 not in ["faculty", "tba", "guest faculty"]:
                    # If scheduled in different rooms
                    if e1.room_raw_text.strip().lower() != e2.room_raw_text.strip().lower():
                        desc = (
                            f"Faculty Clash for {e1.faculty_name} on {e1.day_of_week} ({e1.start_time}-{e1.end_time}): "
                            f"Assigned to '{e1.subject_name}' in {e1.room_raw_text} and simultaneously to "
                            f"'{e2.subject_name}' in {e2.room_raw_text}."
                        )
                        conflict = Conflict(
                            conflict_type="FACULTY_CLASH",
                            description=desc,
                            entry_ids=[e1.id, e2.id],
                            severity="CRITICAL",
                            resolved=False
                        )
                        db.add(conflict)
                        detected_conflicts.append(conflict)

        db.commit()
        return detected_conflicts

    @staticmethod
    def get_all_conflicts(db: Session, resolved: bool = None) -> List[ConflictResponse]:
        query = db.query(Conflict)
        if resolved is not None:
            query = query.filter(Conflict.resolved == resolved)
        
        conflicts = query.order_by(Conflict.detected_at.desc()).all()
        result = []
        for c in conflicts:
            # Fetch affected entries
            entries = []
            if c.entry_ids:
                entries_db = db.query(TimetableEntry).filter(TimetableEntry.id.in_(c.entry_ids)).all()
                entries = [TimetableEntryResponse.from_orm(e) for e in entries_db]

            result.append(ConflictResponse(
                id=c.id,
                conflict_type=c.conflict_type,
                description=c.description,
                entry_ids=c.entry_ids or [],
                severity=c.severity,
                resolved=c.resolved,
                resolution_notes=c.resolution_notes,
                detected_at=c.detected_at,
                affected_entries=entries
            ))
        return result

    @staticmethod
    def resolve_conflict(db: Session, conflict_id: int, notes: str = None) -> bool:
        conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
        if not conflict:
            return False
        conflict.resolved = True
        conflict.resolution_notes = notes or "Resolved by admin."
        db.commit()
        return True
