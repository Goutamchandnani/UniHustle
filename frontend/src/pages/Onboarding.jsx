import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import TimetableInput from './TimetableInput'; // Reuse existing component logic if possible, or we might need to wrap it.
// Checking TimetableInput, it's a full page. We might want to extract the grid or just use it as is for step 3.
// For MVP, let's just render it or a simplified version. Actually TimetableInput is complex.
// Let's TRY to import it. If it has its own layout/header, it might look weird.
// Better to create a wrapper or modify TimetableInput to be embeddable?
// Let's import it but maybe we just hide the navbar in Onboarding.

import { ArrowRight, Check, BookOpen, MapPin, Calendar } from 'lucide-react';
import Button from '../components/ui/Button';

const Onboarding = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // Step 1 Data
    const [profile, setProfile] = useState({
        university: '',
        course: '',
        year_of_study: 1,
        visa_status: 'Home',
        postcode: ''
    });

    // Step 2 Data
    const [prefs, setPrefs] = useState({
        min_salary: 11,
        max_commute_time: 30,
        preferred_roles: '', // Comma-separated string
        preferred_locations: '' // Comma-separated string
    });

    // Step 3 Data
    const [scheduleSlots, setScheduleSlots] = useState([]);

    const handleProfileChange = (e) => {
        setProfile({ ...profile, [e.target.name]: e.target.value });
    };

    const handlePrefsChange = (e) => {
        setPrefs({ ...prefs, [e.target.name]: e.target.value });
    };

    const submitStep1 = async () => {
        setLoading(true);
        try {
            await api.put('/profile', profile);
            setStep(2);
        } catch (e) {
            console.error(e);
            alert("Failed to save profile");
        } finally {
            setLoading(false);
        }
    };

    const submitStep2 = async () => {
        setLoading(true);
        try {
            await api.put('/preferences', prefs);
            setStep(3);
        } catch (e) {
            console.error(e);
            alert("Failed to save preferences");
        } finally {
            setLoading(false);
        }
    };

    const finishOnboarding = async () => {
        setLoading(true);
        try {
            // Save Schedule
            await api.put('/schedule', scheduleSlots);
            navigate('/');
        } catch (e) {
            console.error(e);
            alert("Failed to save schedule");
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl w-full space-y-8">

                {/* Progress Bar */}
                <div className="relative">
                    <div className="absolute inset-0 flex items-center" aria-hidden="true">
                        <div className="w-full border-t border-slate-200" />
                    </div>
                    <div className="relative flex justify-between">
                        {[1, 2, 3].map((s) => (
                            <div key={s} className={`bg-white px-2 flex items-center justify-center`}>
                                <div className={`h-8 w-8 rounded-full flex items-center justify-center border-2 
                                    ${step > s ? 'bg-sky-600 border-sky-600 text-white' :
                                        step === s ? 'border-sky-600 text-sky-600' : 'border-slate-300 text-slate-300'}`}>
                                    {step > s ? <Check className="w-5 h-5" /> : s}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white py-8 px-8 shadow rounded-xl border border-slate-100">

                    {step === 1 && (
                        <div className="space-y-6">
                            <div className="text-center">
                                <h2 className="text-2xl font-bold text-slate-900">Let's set up your profile</h2>
                                <p className="mt-2 text-slate-500">Tell us a bit about your studies so we can find relevant jobs.</p>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700">University</label>
                                    <input
                                        name="university"
                                        value={profile.university}
                                        onChange={handleProfileChange}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        placeholder="e.g. King's College London"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700">Course / Major</label>
                                    <input
                                        name="course"
                                        value={profile.course}
                                        onChange={handleProfileChange}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        placeholder="e.g. Computer Science"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700">Postcode (for accurate commute calculation)</label>
                                    <input
                                        name="postcode"
                                        value={profile.postcode}
                                        onChange={handleProfileChange}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        placeholder="e.g. SW1A 1AA"
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700">Year of Study</label>
                                        <select
                                            name="year_of_study"
                                            value={profile.year_of_study}
                                            onChange={handleProfileChange}
                                            className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        >
                                            <option value={1}>1st Year</option>
                                            <option value={2}>2nd Year</option>
                                            <option value={3}>3rd Year</option>
                                            <option value={4}>4th Year / Masters</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700">Status</label>
                                        <select
                                            name="visa_status"
                                            value={profile.visa_status}
                                            onChange={handleProfileChange}
                                            className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        >
                                            <option value="Home">Home Student</option>
                                            <option value="Tier 4">International (Tier 4)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <Button onClick={submitStep1} className="w-full flex justify-center items-center gap-2" disabled={loading}>
                                Continue <ArrowRight className="w-4 h-4" />
                            </Button>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-6">
                            <div className="text-center">
                                <h2 className="text-2xl font-bold text-slate-900">What are you looking for?</h2>
                                <p className="mt-2 text-slate-500">We filter out jobs that don't match these criteria.</p>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">What kind of jobs do you want?</label>
                                    <input
                                        name="preferred_roles"
                                        value={prefs.preferred_roles}
                                        onChange={handlePrefsChange}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        placeholder="e.g. Barista, Tutor, Retail, Warehouse"
                                    />
                                    <p className="text-xs text-slate-500 mt-1">Separate keywords with commas (we'll fetch jobs specifically for these).</p>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">Preferred Work Locations (Optional)</label>
                                    <input
                                        name="preferred_locations"
                                        value={prefs.preferred_locations}
                                        onChange={handlePrefsChange}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                                        placeholder="e.g. Leamington Spa, Coventry, Remote"
                                    />
                                    <p className="text-xs text-slate-500 mt-1">If set, we'll prioritize jobs in these areas regardless of commute distance.</p>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">Minimum Hourly Pay: £{prefs.min_salary}</label>
                                    <input
                                        name="min_salary"
                                        type="range" min="10" max="30" step="0.5"
                                        value={prefs.min_salary}
                                        onChange={handlePrefsChange}
                                        className="w-full accent-sky-600"
                                    />
                                    <div className="flex justify-between text-xs text-slate-400">
                                        <span>£10</span>
                                        <span>£30+</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">Max Commute Time: {prefs.max_commute_time} mins</label>
                                    <input
                                        name="max_commute_time"
                                        type="range" min="15" max="90" step="15"
                                        value={prefs.max_commute_time}
                                        onChange={handlePrefsChange}
                                        className="w-full accent-sky-600"
                                    />
                                    <div className="flex justify-between text-xs text-slate-400">
                                        <span>15 mins</span>
                                        <span>90 mins</span>
                                    </div>
                                </div>
                            </div>

                            <Button onClick={submitStep2} className="w-full flex justify-center items-center gap-2" disabled={loading}>
                                Continue <ArrowRight className="w-4 h-4" />
                            </Button>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="space-y-6">
                            <div className="text-center">
                                <h2 className="text-2xl font-bold text-slate-900">Set your Availability</h2>
                                <p className="mt-2 text-slate-500">Mark your classes. We'll find jobs that fit around them.</p>
                            </div>

                            {/* Embed existing component in a contained wrapper */}
                            <div className="border border-slate-200 rounded-lg p-2 h-96 overflow-y-auto">
                                <TimetableInput embedded={true} onScheduleChange={setScheduleSlots} />
                                {/* We might need to modify TimetableInput to accept an 'embedded' prop to hide its own header/layout if it has one */}
                            </div>

                            <div className="flex gap-4">
                                <Button onClick={finishOnboarding} className="w-full flex justify-center items-center gap-2" disabled={loading}>
                                    {loading ? 'Finishing...' : <>Finish & Find Jobs <Check className="w-4 h-4" /></>}
                                </Button>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default Onboarding;
