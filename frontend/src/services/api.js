const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '') + '/api';

export const api = {
  // Live Availability
  getAvailableNow: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);
    if (params.buildingCode) query.append('building_code', params.buildingCode);
    if (params.floor !== undefined && params.floor !== null && params.floor !== '') query.append('floor', params.floor);
    if (params.roomType) query.append('room_type', params.roomType);

    const res = await fetch(`${API_BASE}/classrooms/available-now?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch classroom availability');
    return res.json();
  },

  // Single Classroom Status
  getClassroomStatus: async (classroomId, params = {}) => {
    const query = new URLSearchParams();
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);

    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/status?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch classroom status');
    return res.json();
  },

  // Single Classroom Weekly Schedule
  getClassroomSchedule: async (classroomId) => {
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/schedule`);
    if (!res.ok) throw new Error('Failed to fetch classroom schedule');
    return res.json();
  },

  // Search Classrooms
  searchClassrooms: async (params) => {
    const query = new URLSearchParams({
      start_time: params.startTime,
      end_time: params.endTime
    });
    if (params.dayOfWeek) query.append('day_of_week', params.dayOfWeek);
    if (params.buildingCode) query.append('building_code', params.buildingCode);
    if (params.floor !== undefined && params.floor !== null && params.floor !== '') query.append('floor', params.floor);
    if (params.roomType) query.append('room_type', params.roomType);
    if (params.minCapacity) query.append('min_capacity', params.minCapacity);
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);

    const res = await fetch(`${API_BASE}/classrooms/search?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to search classrooms');
    return res.json();
  },

  // Buildings and Map
  getBuildings: async () => {
    const res = await fetch(`${API_BASE}/buildings`);
    if (!res.ok) throw new Error('Failed to fetch buildings');
    return res.json();
  },

  getFloorMap: async (buildingCode, floor, params = {}) => {
    const query = new URLSearchParams();
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);

    const res = await fetch(`${API_BASE}/buildings/${buildingCode}/floors/${floor}/map?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch floor map');
    return res.json();
  },

  // Timetables & Analytics
  getDepartments: async () => {
    const res = await fetch(`${API_BASE}/departments`);
    if (!res.ok) throw new Error('Failed to fetch departments');
    return res.json();
  },

  getSectionTimetable: async (departmentCode, semester, section) => {
    const query = new URLSearchParams({
      department_code: departmentCode,
      semester,
      section
    });
    const res = await fetch(`${API_BASE}/timetables/section?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch section timetable');
    return res.json();
  },

  getFacultyTimetable: async (facultyName) => {
    const res = await fetch(`${API_BASE}/timetables/faculty/${encodeURIComponent(facultyName)}`);
    if (!res.ok) throw new Error('Failed to fetch faculty timetable');
    return res.json();
  },

  getFacultyList: async () => {
    const res = await fetch(`${API_BASE}/faculty`);
    if (!res.ok) throw new Error('Failed to fetch faculty list');
    return res.json();
  },

  getCampusAnalytics: async () => {
    const res = await fetch(`${API_BASE}/analytics/overview`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  // Admin & PDF Upload
  uploadTimetablePdf: async (file, academicYear = '2026-27') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('academic_year', academicYear);

    const res = await fetch(`${API_BASE}/admin/upload-pdf`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload and parse PDF timetable');
    return res.json();
  },

  getUploadStatus: async (uploadId) => {
    const res = await fetch(`${API_BASE}/admin/uploads/${uploadId}/status`);
    if (!res.ok) throw new Error('Failed to fetch upload status');
    return res.json();
  },

  getUploadReview: async (uploadId) => {
    const res = await fetch(`${API_BASE}/admin/uploads/${uploadId}/review`);
    if (!res.ok) throw new Error('Failed to fetch upload review data');
    return res.json();
  },

  approveUpload: async (uploadId) => {
    const res = await fetch(`${API_BASE}/admin/uploads/${uploadId}/approve`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to approve upload');
    return res.json();
  },

  // Conflict Center
  getConflicts: async () => {
    const res = await fetch(`${API_BASE}/conflicts`);
    if (!res.ok) throw new Error('Failed to fetch conflicts');
    return res.json();
  },

  resolveConflict: async (conflictId, notes) => {
    const res = await fetch(`${API_BASE}/conflicts/${conflictId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolution_notes: notes })
    });
    if (!res.ok) throw new Error('Failed to resolve conflict');
    return res.json();
  },

  // Exceptions
  getExceptions: async (activeOnly = false) => {
    const res = await fetch(`${API_BASE}/exceptions?active_only=${activeOnly}`);
    if (!res.ok) throw new Error('Failed to fetch exceptions');
    return res.json();
  },

  createException: async (data) => {
    const res = await fetch(`${API_BASE}/exceptions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create timetable exception');
    return res.json();
  },

  deleteException: async (exceptionId) => {
    const res = await fetch(`${API_BASE}/exceptions/${exceptionId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete exception');
    return res.json();
  }
};
