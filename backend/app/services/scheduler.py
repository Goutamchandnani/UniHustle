from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Tuple

class ScheduleAnalyzer:
    def __init__(self, commute_time_mins: int = 30):
        self.commute_time = timedelta(minutes=commute_time_mins)
        self.min_buffer = timedelta(minutes=15) # Minimum required personal buffer

    def analyze_fit(self, student_timetable: List[Dict], job_shifts: List[Dict]) -> Dict[str, Any]:
        """
        Analyzes the compatibility between a student's timetable and job shifts.
        Returns a dictionary with score, status, and detailed conflict analysis.
        """
        conflicts = []
        warnings = []
        total_shifts = len(job_shifts)
        if total_shifts == 0:
             return self._result(100, "Perfect Fit", "Flexible schedule - no fixed shifts.")

        conflicting_shifts = 0
        tight_shifts = 0

        for shift in job_shifts:
            shift_day = shift['day'].lower()
            shift_start = self._to_time(shift['start'])
            shift_end = self._to_time(shift['end'])

            # Filter classes for the same day
            days_classes = [c for c in student_timetable if c['day'].lower() == shift_day]
            
            has_conflict = False
            for cls in days_classes:
                cls_start = self._to_time(cls['start'])
                cls_end = self._to_time(cls['end'])

                # 1. Direct Conflict (Overlap)
                if self._overlaps(shift_start, shift_end, cls_start, cls_end):
                    conflicts.append(f"❌ Shift on {shift_day} ({shift['start']}-{shift['end']}) overlaps with class ({cls['start']}-{cls['end']})")
                    has_conflict = True
                    break # Stop checking other classes for this shift if one conflict found

                # 2. Insufficient Buffer (Commute check)
                # Check buffer if shift starts after class
                if shift_start > cls_end:
                    gap = self._time_diff(cls_end, shift_start)
                    required_gap = self.commute_time + self.min_buffer
                    
                    if gap < self.commute_time:
                         conflicts.append(f"❌ Impossible commute on {shift_day}: Only {gap.seconds//60}m gap between class end and shift start (need {self.commute_time.seconds//60}m)")
                         has_conflict = True
                         break
                    elif gap < required_gap:
                        warnings.append(f"⚠️ Tight timing on {shift_day}: {gap.seconds//60}m gap (Commute is {self.commute_time.seconds//60}m)")
                        tight_shifts += 1

                # Check buffer if class starts after shift (student needs to get to class)
                if cls_start > shift_end:
                    gap = self._time_diff(shift_end, cls_start)
                    required_gap = self.commute_time + self.min_buffer
                    
                    if gap < self.commute_time:
                         conflicts.append(f"❌ Impossible commute on {shift_day}: Shift ends too close to class start.")
                         has_conflict = True
                         break
                    elif gap < required_gap:
                         warnings.append(f"⚠️ Tight timing on {shift_day}: rushing from work to class.")
                         tight_shifts += 1

            if has_conflict:
                conflicting_shifts += 1

        # Calculate Score
        score = self._calculate_score(total_shifts, conflicting_shifts, tight_shifts)
        
        return self._result(score, self._get_status_label(score), conflicts + warnings)

    def _overlaps(self, start1: time, end1: time, start2: time, end2: time) -> bool:
        """Check if two time ranges overlap."""
        return max(start1, start2) < min(end1, end2)

    def _time_diff(self, start: time, end: time) -> timedelta:
        """Calculate difference between two times."""
        dummy_date = datetime(2000, 1, 1) # Arbitrary date
        dt1 = datetime.combine(dummy_date, start)
        dt2 = datetime.combine(dummy_date, end)
        if dt2 < dt1:
            dt2 += timedelta(days=1) # Handle overnight? (Simple version assumes same day)
        return dt2 - dt1

    def _to_time(self, time_input: Any) -> time:
        """Convert 'HH:MM' string or time object to time object."""
        if isinstance(time_input, time):
            return time_input
        if not time_input:
             return time(0, 0) # Fallback? Or raise error?

        time_str = str(time_input)
        try:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            try:
                return datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                 return time(0,0) # Fail safe


    def _calculate_score(self, total: int, conflicts: int, tight: int) -> int:
        if conflicts > 0:
            # High penalty for conflicts. If major conflict exists, score drops below 60.
            # E.g., if 1 out of 5 shifts conflicts, maybe 50?
            percentage_conflict = conflicts / total
            if percentage_conflict > 0.5:
                return 0
            return max(0, 50 - (conflicts * 10)) # Immediate fail range
        
        # Base score 100
        score = 100
        # Deduct for tight timings
        score -= (tight * 10)
        
        # Deduct for commute burden (optional advanced feature)
        
        return max(0, score)

    def _get_status_label(self, score: int) -> str:
        if score == 100: return "Perfect Fit"
        if score >= 80: return "Good Fit"
        if score >= 60: return "Challenge"
        return "Conflict"

    def _result(self, score, status, messages):
        return {
            "score": score,
            "status": status,
            "analysis": messages
        }
