import React, { useMemo } from 'react';
import { Clock, AlertTriangle, CheckCircle, ArrowRightLeft } from 'lucide-react';
import Card from './ui/Card';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const ScheduleComparison = ({ studentSchedule, jobShifts }) => {
    // Group by Day
    const dayComparison = useMemo(() => {
        return DAYS.map(day => {
            const classes = studentSchedule.filter(s => s.day_of_week === day);
            const shifts = jobShifts.filter(s => s.day === day || s.day_of_week === day); // Handle different key names if any

            if (classes.length === 0 && shifts.length === 0) return null;

            // Simple conflict check for visualization (Overlap)
            let conflict = null;
            // In a real app, reuse the precise backend logic or pass it down
            const hasOverlap = classes.some(c =>
                shifts.some(s => {
                    const cStart = parseInt(c.start_time.split(':')[0]);
                    const cEnd = parseInt(c.end_time.split(':')[0]);
                    const sStart = parseInt(s.start.split(':')[0]);
                    const sEnd = parseInt(s.end.split(':')[0]);
                    return Math.max(cStart, sStart) < Math.min(cEnd, sEnd);
                })
            );

            if (hasOverlap) conflict = "Direct Time Conflict";

            return { day, classes, shifts, conflict };
        }).filter(Boolean); // Remove empty days
    }, [studentSchedule, jobShifts]);

    if (dayComparison.length === 0) {
        return (
            <Card className="p-6 text-center text-slate-500">
                No shifts or classes to compare for this job.
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-slate-900">Schedule Compatibility</h3>

            <div className="space-y-4">
                {dayComparison.map(({ day, classes, shifts, conflict }) => (
                    <div key={day} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                        {/* Header */}
                        <div className={`px-4 py-2 text-sm font-semibold flex justify-between items-center ${conflict ? 'bg-red-50 text-red-700' : 'bg-slate-50 text-slate-700'}`}>
                            <span>{day}</span>
                            {conflict ? (
                                <span className="flex items-center gap-1 text-red-600"><AlertTriangle className="w-4 h-4" /> {conflict}</span>
                            ) : (
                                <span className="flex items-center gap-1 text-green-600"><CheckCircle className="w-4 h-4" /> Fits Schedule</span>
                            )}
                        </div>

                        {/* Comparison Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">

                            {/* Classes Column */}
                            <div className="p-4 bg-slate-50/50">
                                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 block">Your Classes</span>
                                {classes.length > 0 ? (
                                    <div className="space-y-2">
                                        {classes.map((cls, i) => (
                                            <div key={i} className="flex items-center gap-3 bg-white p-2 rounded border border-slate-200 shadow-sm border-l-4 border-l-red-500">
                                                <Clock className="w-4 h-4 text-slate-400" />
                                                <div>
                                                    <div className="text-sm font-medium text-slate-900">{cls.activity_type || 'Class'}</div>
                                                    <div className="text-xs text-slate-500">{cls.start_time.slice(0, 5)} - {cls.end_time.slice(0, 5)}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-sm text-slate-400 italic">No classes</div>
                                )}
                            </div>

                            {/* Shifts Column */}
                            <div className="p-4">
                                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 block">Job Shifts</span>
                                {shifts.length > 0 ? (
                                    <div className="space-y-2">
                                        {shifts.map((shift, i) => (
                                            <div key={i} className="flex items-center gap-3 bg-green-50 p-2 rounded border border-green-200 shadow-sm border-l-4 border-l-green-500">
                                                <Clock className="w-4 h-4 text-green-600" />
                                                <div>
                                                    <div className="text-sm font-medium text-green-900">Work Shift</div>
                                                    <div className="text-xs text-green-700">{shift.start.slice(0, 5)} - {shift.end.slice(0, 5)}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-sm text-slate-400 italic">No shifts</div>
                                )}
                            </div>

                        </div>

                        {/* Commute/Gap Info (Dummy visual for now) */}
                        <div className="bg-slate-50 px-4 py-2 text-xs text-slate-500 border-t border-slate-100 flex items-center gap-2">
                            <ArrowRightLeft className="w-3 h-3" />
                            <span>Estimated commute time logic would appear here (e.g. 30min gap required).</span>
                        </div>

                    </div>
                ))}
            </div>
        </div>
    );
};

export default ScheduleComparison;
