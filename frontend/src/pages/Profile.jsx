import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Button from '../components/ui/Button';
import { Save } from 'lucide-react';

const Profile = () => {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');

    const [profile, setProfile] = useState({
        university: '',
        course: '',
        year_of_study: 1,
        visa_status: 'Home',
        postcode: '',
        // Preferences merged here for unified editing
        min_salary: 11,
        max_commute_time: 30,
        preferred_roles: '',
        preferred_locations: ''
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            // Fetch both profile and preferences
            const [profRes, prefRes] = await Promise.all([
                api.get('/profile'),
                api.get('/preferences')
            ]);

            setProfile({
                ...profRes.data,
                min_salary: prefRes.data.min_salary || 11,
                max_commute_time: prefRes.data.max_commute_time || 30,
                preferred_roles: prefRes.data.preferred_roles || '',
                preferred_locations: prefRes.data.preferred_locations || ''
            });
        } catch (e) {
            console.error("Failed to fetch profile", e);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setProfile({ ...profile, [e.target.name]: e.target.value });
    };

    const handleSave = async () => {
        setSaving(true);
        setSuccessMsg('');
        try {
            // Split back into two calls
            const profileData = {
                university: profile.university,
                course: profile.course,
                year_of_study: profile.year_of_study,
                visa_status: profile.visa_status,
                postcode: profile.postcode
            };

            const prefsData = {
                min_salary: profile.min_salary,
                max_commute_time: profile.max_commute_time,
                preferred_roles: profile.preferred_roles,
                preferred_locations: profile.preferred_locations
            };

            await Promise.all([
                api.put('/profile', profileData),
                api.put('/preferences', prefsData)
            ]);

            setSuccessMsg('Profile updated successfully!');
            setTimeout(() => setSuccessMsg(''), 3000);
        } catch (e) {
            console.error(e);
            alert("Failed to update profile");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Loading profile...</div>;

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-2xl font-bold text-slate-900 mb-6">Your Profile</h1>

            <div className="bg-white shadow rounded-lg border border-slate-200 p-6 space-y-8">

                {/* Academic & Personal */}
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-slate-800 border-b pb-2">Academic & Personal Details</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700">University</label>
                            <input
                                name="university"
                                value={profile.university}
                                onChange={handleChange}
                                type="text"
                                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Course / Major</label>
                            <input
                                name="course"
                                value={profile.course}
                                onChange={handleChange}
                                type="text"
                                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Postcode</label>
                            <input
                                name="postcode"
                                value={profile.postcode}
                                onChange={handleChange}
                                type="text"
                                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Year of Study</label>
                            <select
                                name="year_of_study"
                                value={profile.year_of_study}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            >
                                <option value={1}>1st Year</option>
                                <option value={2}>2nd Year</option>
                                <option value={3}>3rd Year</option>
                                <option value={4}>4th Year / Masters</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Visa Status</label>
                            <select
                                name="visa_status"
                                value={profile.visa_status}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            >
                                <option value="Home">Home Student</option>
                                <option value="Tier 4">International (Tier 4)</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Job Preferences */}
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-slate-800 border-b pb-2">Job Preferences</h2>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Roles</label>
                        <input
                            name="preferred_roles"
                            value={profile.preferred_roles}
                            onChange={handleChange}
                            type="text"
                            className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            placeholder="e.g. Barista, Tutor"
                        />
                        <p className="text-xs text-slate-500 mt-1">Keywords separated by commas.</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Work Locations</label>
                        <input
                            name="preferred_locations"
                            value={profile.preferred_locations}
                            onChange={handleChange}
                            type="text"
                            className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500 p-2 border"
                            placeholder="e.g. Leamington Spa, Coventry"
                        />
                        <p className="text-xs text-slate-500 mt-1">Specific cities or areas to prioritize.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Min Hourly Pay: £{profile.min_salary}</label>
                            <input
                                name="min_salary"
                                type="range" min="10" max="30" step="0.5"
                                value={profile.min_salary}
                                onChange={handleChange}
                                className="w-full accent-sky-600"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Max Commute: {profile.max_commute_time} mins</label>
                            <input
                                name="max_commute_time"
                                type="range" min="15" max="90" step="15"
                                value={profile.max_commute_time}
                                onChange={handleChange}
                                className="w-full accent-sky-600"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between pt-4">
                    <span className="text-green-600 font-medium text-sm">{successMsg}</span>
                    <Button onClick={handleSave} disabled={saving} className="flex gap-2 items-center">
                        {saving ? 'Saving...' : <>Save Changes <Save className="w-4 h-4" /></>}
                    </Button>
                </div>

            </div>
        </div>
    );
};

export default Profile;
