import { apiClient } from "./api";

export async function getPatientAnalytics(patientId) {
  const response = await apiClient.get(`/api/analytics/${patientId}`);
  return response.data;
}

export async function linkPatient(patientEmail) {
  const response = await apiClient.post("/api/users/link-patient", { patientEmail });
  return response.data;
}

export async function getLinkedPatients() {
  const response = await apiClient.get("/api/users/linked-patients");
  return response.data;
}

export async function getDoctorAlerts() {
  const response = await apiClient.get("/api/monitoring/alerts");
  return response.data;
}

export async function runAdherenceAudit() {
  const response = await apiClient.post("/api/monitoring/run");
  return response.data;
}

export async function processFrame(scheduleId, frameData, currentState, history, confidence) {
  const response = await apiClient.post(`/api/verification/${scheduleId}/process-frame`, {
    frame: frameData,
    currentState,
    history,
    confidence
  });
  return response.data;
}
