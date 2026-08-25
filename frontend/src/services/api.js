export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/$/, '');

const request = async (path, options = {}) => {
  const url = `${API_BASE_URL}${path}`;
  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    console.error(`API request failed: ${url}`, error);
    throw new Error(`API request failed for ${url}: ${error.message}`);
  }

  if (!response.ok) {
    console.error(`API responded with ${response.status}: ${url}`);
    throw new Error(`API error: ${response.status} ${response.statusText} (${url})`);
  }

  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    console.error(`API returned a non-JSON response: ${url}`, {
      status: response.status,
      contentType
    });
    throw new Error(`API returned non-JSON content for ${url} (status ${response.status})`);
  }

  return response.json();
};

export const api = {
  // Live Availability
  getAvailableNow: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);
    if (params.buildingCode) query.append('building_code', params.buildingCode);
    if (params.floor !== undefined && params.floor !== null && params.floor !== '') query.append('floor', params.floor);
    if (params.roomType) query.append('room_type', params.roomType);

    return request(`/api/classrooms/available-now?${query.toString()}`);
  },

  // Single Classroom Status
  getClassroomStatus: async (classroomId, params = {}) => {
    const query = new URLSearchParams();
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);

    return request(`/api/classrooms/${classroomId}/status?${query.toString()}`);
  },

  // Single Classroom Weekly Schedule
  getClassroomSchedule: async (classroomId) => {
    return request(`/api/classrooms/${classroomId}/schedule`);
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

    return request(`/api/classrooms/search?${query.toString()}`);
  },

  // Buildings and Map
  getBuildings: async () => {
    return request('/api/buildings');
  },

  getBuildingClassrooms: async (buildingId, params = {}) => {
    const query = new URLSearchParams();
    if (params.simulatedTime) query.append('simulated_time', params.simulatedTime);
    if (params.simulatedDay) query.append('simulated_day', params.simulatedDay);

    return request(`/api/buildings/${buildingId}/classrooms?${query.toString()}`);
  },

  // Timetables & Analytics
  getCampusStats: async () => {
    return request('/api/stats/overview');
  },

  // Admin & PDF Upload
  uploadTimetable: async (file, academicYear = '2026-27') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('academic_year', academicYear);

    return request('/api/admin/upload-timetable', {
      method: 'POST',
      body: formData
    });
  },

  getTimetableReview: async (uploadId) => {
    return request(`/api/admin/timetable-review/${uploadId}`);
  },

  approveUpload: async (uploadId) => {
    return request(`/api/admin/approve-upload/${uploadId}`, {
      method: 'POST'
    });
  },

  // Conflict Center
  getConflicts: async () => {
    return request('/api/admin/conflicts');
  },

  resolveConflict: async (conflictId, notes) => {
    const query = new URLSearchParams({ notes });
    return request(`/api/admin/conflicts/${conflictId}/resolve?${query.toString()}`, {
      method: 'POST'
    });
  },

  // Exceptions
  getExceptions: async () => {
    return request('/api/admin/exceptions');
  },

  createException: async (data) => {
    return request('/api/admin/exceptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },

  deleteException: async (exceptionId) => {
    return request(`/api/admin/exceptions/${exceptionId}`, {
      method: 'DELETE'
    });
  },

  deleteTimetableEntry: async (entryId) => {
    return request(`/api/admin/timetable-entries/${entryId}`, {
      method: 'DELETE'
    });
  },

  resetDatabase: async () => {
    return request('/api/seed/reset', {
      method: 'POST'
    });
  }
};
