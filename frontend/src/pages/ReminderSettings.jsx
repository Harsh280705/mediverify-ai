import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";

import {
    requestNotificationPermission,
} from "../services/notification";

import {
    saveReminderSettings,
    getReminderSettings,
} from "../services/reminderService";

export default function ReminderSettings() {

    const { currentUser } = useAuth();

    const [loading, setLoading] = useState(true);

    const [settings, setSettings] = useState({

        notificationsEnabled: true,

        browserNotifications: true,

        pushNotifications: false,

        reminderTimes: {

            Morning: "08:00",

            Afternoon: "14:00",

            Evening: "19:00",

            Night: "22:00",
        },

        remindBeforeMinutes: 15,
    });

    useEffect(() => {

        async function load() {

            if (!currentUser) return;

            try {

                const data =
                    await getReminderSettings(currentUser.uid);

                setSettings(data);

            } catch {

                console.log("Using defaults");

            }

            setLoading(false);

        }

        load();

    }, [currentUser]);

    async function save() {

        const granted =
            await requestNotificationPermission();

        if (!granted) {

            alert("Notification permission denied");

            return;

        }

        await saveReminderSettings({

            patientId: currentUser.uid,

            ...settings,

        });

        alert("Reminder settings saved");

    }

    function updateTime(name, value) {

        setSettings((prev) => ({

            ...prev,

            reminderTimes: {

                ...prev.reminderTimes,

                [name]: value,

            },

        }));

    }

    if (loading)
        return <p>Loading...</p>;

    return (

        <div className="max-w-2xl mx-auto p-8">

            <h1 className="text-3xl font-bold mb-8">

                Reminder Settings

            </h1>

            <label>

                <input
                    type="checkbox"
                    checked={settings.notificationsEnabled}
                    onChange={(e) =>
                        setSettings({
                            ...settings,
                            notificationsEnabled:
                                e.target.checked,
                        })
                    }
                />

                Enable Reminders

            </label>

            <br /><br />

            <label>

                <input
                    type="checkbox"
                    checked={settings.browserNotifications}
                    onChange={(e) =>
                        setSettings({
                            ...settings,
                            browserNotifications:
                                e.target.checked,
                        })
                    }
                />

                Browser Notifications

            </label>

            <br /><br />

            {Object.entries(settings.reminderTimes).map(
                ([key, value]) => (

                    <div
                        key={key}
                        className="mb-4"
                    >

                        <label>

                            {key}

                        </label>

                        <input
                            className="border ml-4 p-2"
                            type="time"
                            value={value}
                            onChange={(e) =>
                                updateTime(
                                    key,
                                    e.target.value
                                )
                            }
                        />

                    </div>

                )
            )}

            <select
                value={settings.remindBeforeMinutes}
                onChange={(e) =>
                    setSettings({
                        ...settings,
                        remindBeforeMinutes:
                            Number(e.target.value),
                    })
                }
            >

                <option value={15}>
                    15 minutes
                </option>

                <option value={30}>
                    30 minutes
                </option>

                <option value={60}>
                    1 hour
                </option>

            </select>

            <br /><br />

            <button
                onClick={save}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg"
            >

                Save Settings

            </button>

        </div>

    );

}