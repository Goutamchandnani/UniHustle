import React, { useState, useEffect } from 'react';
import api from '../services/api';
import TimetableGrid from '../components/TimetableGrid';

const TimetableInput = ({ embedded = false, onScheduleChange }) => {
    const [initialData, setInitialData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        loadSchedule();
    }, []);

    const [commuteBuffer, setCommuteBuffer] = useState(30);

    const loadSchedule = async () => {
        try {
            const [schedRes, prefRes] = await Promise.all([
                api.get('/schedule'),
                api.get('/preferences')
            ]);
            setInitialData(schedRes.data);
            if (prefRes.data.max_commute_time) {
                setCommuteBuffer(prefRes.data.max_commute_time);
            }
        } catch (error) {
            console.error('Failed to load data', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (slots) => {
        setSaving(true);
        setMessage(null);
        try {
            await Promise.all([
                api.put('/schedule', slots),
                api.put('/preferences', { max_commute_time: commuteBuffer })
            ]);
            setMessage({ type: 'success', text: 'Settings updated successfully! Matches will recalculate.' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to save settings.' });
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Loading settings...</div>;

    const content = (
        <div className={embedded ? "" : "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"}>
            {!embedded && (
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-slate-900">Manage Your Availability</h1>
                    <p className="text-slate-500">
                        Set your class schedule and your maximum commute tolerance.
                    </p>
                </div>
            )}

            {message && (
                <div className={`mb-4 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                    {message.text}
                </div>
            )}

            <div className={`grid grid-cols-1 ${embedded ? "" : "lg:grid-cols-4"} gap-8`}>
                <div className={embedded ? "w-full" : "lg:col-span-3"}>
                    <TimetableGrid
                        initialData={initialData}
                        onSave={handleSave}
                        loading={saving}
                        onChange={onScheduleChange}
                        showControls={!embedded}
                    />
                </div>

                {!embedded && (
                    <div className="space-y-6">
                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <h3 className="font-semibold text-slate-900 mb-4">Commute Buffer</h3>
                            <p className="text-xs text-slate-500 mb-4">
                                How long are you willing to commute <b>between class and work</b>?
                            </p>

                            <div className="flex items-center gap-4 mb-2">
                                <input
                                    type="range"
                                    min="15"
                                    max="90"
                                    step="5"
                                    value={commuteBuffer}
                                    onChange={(e) => setCommuteBuffer(parseInt(e.target.value))}
                                    className="w-full accent-primary-600"
                                />
                                <span className="font-mono text-sm font-bold text-slate-700 w-12">{commuteBuffer}m</span>
                            </div>
                            <div className="flex justify-between text-xs text-slate-400 px-1">
                                <span>15m</span>
                                <span>90m</span>
                            </div>
                        </div>

                        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 text-sm text-blue-700">
                            <p className="font-semibold mb-1">💡 Pro Tip</p>
                            Marking your classes helps us avoid recommending shifts that overlap or leave too little travel time.
                        </div>
                    </div>
                )}
            </div>
        </div>
    );

    return content;
};

export default TimetableInput;
