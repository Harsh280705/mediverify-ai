import { useEffect } from "react";
import { useAuth } from "../hooks/useAuth";

import {
    getDueReminders,
    markNotificationSent,
} from "../services/reminderService";

import {
    showNotification,
} from "../services/notification";

export default function ReminderScheduler() {

    const { currentUser } = useAuth();

    useEffect(() => {

        if (!currentUser) return;

        async function checkReminders() {

            try {

                const response =
                    await getDueReminders(
                        currentUser.uid
                    );

                const reminders =
                    response.reminders;

                for (const reminder of reminders) {

                    showNotification(

                        "💊 MediVerify AI",

                        `Time to take ${reminder.medicineName}`

                    );

                    await markNotificationSent(
                        reminder.id
                    );

                }

            } catch (err) {

                console.error(err);

            }

        }

        checkReminders();

        const interval =
            setInterval(
                checkReminders,
                60000
            );

        return () =>
            clearInterval(interval);

    }, [currentUser]);

    return null;
}