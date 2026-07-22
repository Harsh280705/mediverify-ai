import { getFirebaseAuth } from "./firebase";

const API = "http://127.0.0.1:8000/api";

async function authHeaders() {

    const user = getFirebaseAuth().currentUser;

    if (!user)
        throw new Error("User not logged in");

    const token = await user.getIdToken();

    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    };
}

export async function getVerificationSchedule(scheduleId) {

    const headers = await authHeaders();

    const response = await fetch(
        `${API}/verification/${scheduleId}`,
        {
            headers,
        }
    );

    if (!response.ok)
        throw new Error("Failed loading verification");

    return response.json();
}