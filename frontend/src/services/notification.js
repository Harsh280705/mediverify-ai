export async function requestNotificationPermission() {

    if (!("Notification" in window)) {
        alert("This browser does not support notifications.");
        return false;
    }

    if (Notification.permission === "granted") {
        return true;
    }

    const permission = await Notification.requestPermission();

    return permission === "granted";
}

export function showNotification(title, body) {

    if (Notification.permission !== "granted") return;
    
    new Notification(title, {
        body,
        icon: "/logo192.png", // optional
    });

}