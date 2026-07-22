import { apiClient } from "./api";

export async function getDashboard(patientId) {
  const [medicationsRes, scheduleRes] = await Promise.all([
    apiClient.get("/api/medications", {
      params: { patientId },
    }),
    apiClient.get("/api/schedule", {
      params: { patientId },
    }),
  ]);

  return {
    medications: medicationsRes.data,
    schedules: scheduleRes.data,
  };
}

export async function getTodaySchedule(patientId) {

    const response = await apiClient.get("/api/schedule", {
        params: {
            patientId,
        },
    });

    return response.data;
}