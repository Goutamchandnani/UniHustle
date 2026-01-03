import React, { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import Button from './ui/Button';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const HOURS = Array.from({ length: 13 }, (_, i) => i + 9); // 9am to 9pm (21:00)

const TimetableGrid = ({ initialData, onSave, loading, onChange, showControls = true }) => {
    // State: Map of "Day-Hour" string to Activity Type (or null if free)
    // Key format: "Monday-9"
    const [schedule, setSchedule] = useState({});
    const [isDragging, setIsDragging] = useState(false);
    const [dragAction, setDragAction] = useState(null); // 'add' or 'remove'

    useEffect(() => {
        if (initialData) {
            const newSchedule = {};
            initialData.forEach(slot => {
                // Parse "09:00:00" -> 9
                const startHour = parseInt(slot.start_time.split(':')[0], 10);
                const endHour = parseInt(slot.end_time.split(':')[0], 10);
                const duration = endHour - startHour;

                for (let i = 0; i < duration; i++) {
                    const key = `${slot.day_of_week}-${startHour + i}`;
                    newSchedule[key] = slot.activity_type || 'Class';
                }
            });
            setSchedule(newSchedule);
        }
    }, [initialData]);

    // Lift state up whenever it changes
    useEffect(() => {
        if (onChange) {
            const slots = [];
            Object.entries(schedule).forEach(([key, type]) => {
                const [day, hourStr] = key.split('-');
                const hour = parseInt(hourStr, 10);
                slots.push({
                    day_of_week: day,
                    start_time: `${hour}:00`,
                    end_time: `${hour + 1}:00`,
                    activity_type: type
                });
            });
            onChange(slots);
        }
    }, [schedule, onChange]);

    const toggleSlot = (day, hour) => {
        const key = `${day}-${hour}`;
        setSchedule(prev => {
            const newState = { ...prev };
            if (newState[key]) {
                delete newState[key];
            } else {
                newState[key] = 'Class';
            }
            return newState;
        });
    };

    const handleMouseDown = (day, hour) => {
        setIsDragging(true);
        const key = `${day}-${hour}`;
        setDragAction(schedule[key] ? 'remove' : 'add');
        toggleSlot(day, hour);
    };

    const handleMouseEnter = (day, hour) => {
        if (!isDragging) return;
        const key = `${day}-${hour}`;

        setSchedule(prev => {
            const newState = { ...prev };
            if (dragAction === 'add') {
                newState[key] = 'Class';
            } else {
                delete newState[key];
            }
            return newState;
        });
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setDragAction(null);
    };

    // Convert state back to API format
    const handleSave = () => {
        const slots = [];
        // Simple algorithm: coalesce adjacent slots if needed, or just save hourly blocks
        // For simplicity, saving hourly blocks. Backend can optimize if needed.

        Object.entries(schedule).forEach(([key, type]) => {
            const [day, hourStr] = key.split('-');
            const hour = parseInt(hourStr, 10);

            slots.push({
                day_of_week: day,
                start_time: `${hour}:00`,
                end_time: `${hour + 1}:00`,
                activity_type: type
            });
        });

        onSave(slots);
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden select-none" onMouseLeave={handleMouseUp}>
            {/* Header */}
            <div className="grid grid-cols-8 border-b border-slate-200 bg-slate-50">
                <div className="p-3 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center border-r border-slate-200">
                    Time
                </div>
                {DAYS.map(day => (
                    <div key={day} className="p-3 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center hidden md:block">
                        {day.slice(0, 3)}
                    </div>
                ))}
                {/* Mobile View Label support omitted for brevity, keeping desktop grid for now */}
            </div>

            {/* Grid */}
            <div className="relative">
                {HOURS.map(hour => (
                    <div key={hour} className="grid grid-cols-8 border-b border-slate-100 last:border-0">
                        {/* Time Label */}
                        <div className="p-2 text-xs text-slate-400 text-right pr-4 border-r border-slate-100">
                            {hour}:00
                        </div>

                        {/* Days */}
                        {DAYS.map(day => {
                            const isActive = !!schedule[`${day}-${hour}`];
                            return (
                                <div
                                    key={`${day}-${hour}`}
                                    className={clsx(
                                        "h-10 cursor-pointer transition-colors border-r border-slate-50 last:border-0",
                                        isActive ? "bg-sky-100 hover:bg-sky-200" : "hover:bg-slate-50"
                                    )}
                                    onMouseDown={() => handleMouseDown(day, hour)}
                                    onMouseEnter={() => handleMouseEnter(day, hour)}
                                    onMouseUp={handleMouseUp}
                                >
                                    {isActive && (
                                        <div className="w-full h-full flex items-center justify-center">
                                            <div className="w-1.5 h-1.5 rounded-full bg-sky-500" />
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>

            {showControls && (
                <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-between items-center">
                    <div className="text-sm text-slate-500">
                        Click and drag to mark your class times.
                    </div>
                    <div className="flex gap-2">
                        <Button variant="ghost" onClick={() => setSchedule({})}>Clear</Button>
                        <Button onClick={handleSave} disabled={loading}>
                            {loading ? 'Saving...' : 'Save Schedule'}
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TimetableGrid;
