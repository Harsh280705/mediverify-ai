import { getFirebaseAuth } from "./firebase";

const API = "http://127.0.0.1:8000/api";

async function authHeaders() {
    const user = getFirebaseAuth().currentUser;

    if (!user) {
        throw new Error("User not logged in");
    }

    const token = await user.getIdToken();

    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    };
}

export async function saveReminderSettings(data) {

    const headers = await authHeaders();

    const response = await fetch(
        `${API}/reminders/settings`,
        {
            method: "POST",
            headers,
            body: JSON.stringify(data),
        }
    );

    if (!response.ok)
        throw new Error("Failed to save settings");

    return response.json();
}

export async function getReminderSettings(patientId) {

    const headers = await authHeaders();

    const response = await fetch(
        `${API}/reminders/settings?patientId=${patientId}`,
        {
            headers,
        }
    );

    if (!response.ok)
        throw new Error("Failed loading settings");

    return response.json();
}

export async function getDueReminders(patientId) {

    const headers = await authHeaders();

    const response = await fetch(
        `${API}/reminders/due?patientId=${patientId}`,
        {
            headers,
        }
    );

    if (!response.ok) {
        throw new Error("Failed loading due reminders");
    }

    return response.json();
}

export async function markNotificationSent(scheduleId) {

    const headers = await authHeaders();

    const response = await fetch(
        `${API}/reminders/${scheduleId}/notification-sent`,
        {
            method: "PATCH",
            headers,
        }
    );

    if (!response.ok) {
        throw new Error("Failed updating notification");
    }

    return response.json();
}