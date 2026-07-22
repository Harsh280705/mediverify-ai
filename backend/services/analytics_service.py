import logging
from datetime import datetime, timezone, timedelta
from firebase.firebase_admin import get_firestore_client

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def get_patient_analytics(self, patient_id: str) -> dict:
        """
        Calculates today's stats, weekly/monthly adherence rates, and current/longest streaks.
        """
        try:
            snapshots = self.db.collection("schedules").where("patientId", "==", patient_id).get()
            schedules = []
            for snap in snapshots:
                data = snap.to_dict()
                data["id"] = snap.id
                schedules.append(data)
                
            now = datetime.now(timezone.utc)
            today_str = now.strftime("%Y-%m-%d")
            
            # Today's stats
            today_taken = 0
            today_pending = 0
            today_missed = 0
            
            for s in schedules:
                if s.get("scheduledDate") == today_str:
                    status = s.get("status", "Pending")
                    scheduled_dt = s.get("scheduledDateTime")
                    
                    if scheduled_dt and scheduled_dt.tzinfo is None:
                        scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
                        
                    if status == "Taken":
                        today_taken += 1
                    elif status == "Pending":
                        if scheduled_dt and now > scheduled_dt:
                            today_missed += 1
                        else:
                            today_pending += 1
                            
            # Adherence by periods: last 7 days and last 30 days
            limit_7 = now - timedelta(days=7)
            limit_30 = now - timedelta(days=30)
            
            taken_7, total_7 = 0, 0
            taken_30, total_30 = 0, 0
            taken_all, total_all = 0, 0
            
            for s in schedules:
                status = s.get("status", "Pending")
                scheduled_dt = s.get("scheduledDateTime")
                
                if not scheduled_dt:
                    continue
                if scheduled_dt.tzinfo is None:
                    scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
                    
                # We only consider schedules that are due (scheduledDateTime is in the past)
                if scheduled_dt > now:
                    continue
                    
                is_taken = 1 if status == "Taken" else 0
                
                # All-time
                taken_all += is_taken
                total_all += 1
                
                # Last 7 days
                if scheduled_dt >= limit_7:
                    taken_7 += is_taken
                    total_7 += 1
                    
                # Last 30 days
                if scheduled_dt >= limit_30:
                    taken_30 += is_taken
                    total_30 += 1
                    
            adherence_7 = round((taken_7 / total_7 * 100), 2) if total_7 > 0 else 100.0
            adherence_30 = round((taken_30 / total_30 * 100), 2) if total_30 > 0 else 100.0
            adherence_overall = round((taken_all / total_all * 100), 2) if total_all > 0 else 100.0
            
            # Streak calculation
            # 1. Group schedules by scheduledDate
            daily_schedules = {}
            for s in schedules:
                date = s.get("scheduledDate")
                if not date:
                    continue
                if date not in daily_schedules:
                    daily_schedules[date] = []
                daily_schedules[date].append(s)
                
            # 2. Check adherence per date (day is adherent if there are no missed/pending past schedules on that day)
            adherent_dates = set()
            for date, day_scheds in daily_schedules.items():
                is_adherent = True
                for s in day_scheds:
                    status = s.get("status", "Pending")
                    scheduled_dt = s.get("scheduledDateTime")
                    if scheduled_dt and scheduled_dt.tzinfo is None:
                        scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
                        
                    # If dose is Taken, it's fine. If Pending and in the past, it's missed -> not adherent
                    if status == "Pending" and scheduled_dt and now > scheduled_dt:
                        is_adherent = False
                        break
                    # If Pending and in the future, it's not missed yet, so it doesn't break yesterday's/today's streak
                
                if is_adherent and len(day_scheds) > 0:
                    adherent_dates.add(date)
                    
            # 3. Sort dates and find longest and current streak
            sorted_dates = sorted(list(daily_schedules.keys()))
            
            longest_streak = 0
            current_streak = 0
            temp_streak = 0
            
            # Calculate longest streak
            for d in sorted_dates:
                if d in adherent_dates:
                    temp_streak += 1
                    if temp_streak > longest_streak:
                        longest_streak = temp_streak
                else:
                    temp_streak = 0
                    
            # Calculate current streak (consecutive adherent days ending today or yesterday)
            # Find current streak by starting from today's date and going backwards
            current_streak = 0
            check_date = now.date()
            
            # If today has schedules and all are compliant, or no schedules, start checking from today
            # If today has missed schedules, streak is 0
            # If today has pending future schedules, we count yesterday as the anchor
            while True:
                date_str = check_date.strftime("%Y-%m-%d")
                if date_str in daily_schedules:
                    if date_str in adherent_dates:
                        current_streak += 1
                    else:
                        # Streak broken
                        break
                else:
                    # If there are no schedules for this date:
                    # If this check_date is before the earliest scheduled date, stop.
                    if sorted_dates and date_str < sorted_dates[0]:
                        break
                    # Otherwise, skip empty days (don't break streak for days with no schedules)
                check_date -= timedelta(days=1)
                
            return {
                "today": {
                    "taken": today_taken,
                    "pending": today_pending,
                    "missed": today_missed
                },
                "adherence": {
                    "weekly": adherence_7,
                    "monthly": adherence_30,
                    "overall": adherence_overall
                },
                "streaks": {
                    "current": current_streak,
                    "longest": longest_streak
                }
            }
        except Exception as e:
            logger.error(f"Failed to calculate patient analytics: {e}")
            return {
                "today": {"taken": 0, "pending": 0, "missed": 0},
                "adherence": {"weekly": 100.0, "monthly": 100.0, "overall": 100.0},
                "streaks": {"current": 0, "longest": 0}
            }
