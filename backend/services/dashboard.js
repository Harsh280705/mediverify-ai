import { apiClient } from "./api";

export async function getDashboard(patientId) {
    const [medications, schedules] = await Promise.all([
        apiClient.get(`/api/medications?patientId=${patientId}`),
        apiClient.get(`/api/schedule?patientId=${patientId}`)
    ]);

    return {
        medications: medications.data,
        schedules: schedules.data
    };
}