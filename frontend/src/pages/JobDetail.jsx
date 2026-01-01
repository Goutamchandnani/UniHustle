import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import Button from '../components/ui/Button';
import ScheduleComparison from '../components/ScheduleComparison';
import { MapPin, Building, Banknote } from 'lucide-react';

const JobDetail = () => {
    const { id } = useParams();
    const [job, setJob] = useState(null);
    const [userSchedule, setUserSchedule] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [jobRes, scheduleRes] = await Promise.all([
                    api.get(`/jobs/${id}`),
                    api.get('/schedule')
                ]);
                setJob(jobRes.data);
                setUserSchedule(scheduleRes.data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const [applying, setApplying] = useState(false);
    const [hasApplied, setHasApplied] = useState(false);
    const [applicationStatus, setApplicationStatus] = useState(null); // 'Applied', 'Saved', etc.

    // Check application status on load
    useEffect(() => {
        const checkStatus = async () => {
            if (!job) return;
            try {
                // We'll fetch all applications and filter (optimize this endpoint later)
                const res = await api.get('/applications');
                const existingApp = res.data.find(app => app.job_id === job.id);
                if (existingApp) {
                    setHasApplied(true);
                    setApplicationStatus(existingApp.status);
                }
            } catch (error) {
                console.error("Failed to check status", error);
            }
        };
        checkStatus();
    }, [job]);

    const handleApply = async () => {
        setApplying(true);
        try {
            await api.post('/applications', { job_id: job.id });
            setHasApplied(true);
            setApplicationStatus('Applied');
            // Optionally show toast
        } catch (error) {
            console.error(error);
            if (error.response?.data?.message === "Already applied for this job") {
                setHasApplied(true);
                setApplicationStatus('Applied');
            } else {
                alert("Failed to apply");
            }
        } finally {
            setApplying(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Loading details...</div>;
    if (!job) return <div className="p-8 text-center text-red-500">Job not found.</div>;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Left Column: Job Info */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8">
                        <h1 className="text-3xl font-bold text-slate-900 mb-2">{job.title}</h1>
                        <div className="flex flex-wrap gap-4 text-sm text-slate-600 mb-6">
                            <span className="flex items-center gap-1"><Building className="w-4 h-4" /> {job.company_name}</span>
                            <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {job.location}</span>
                            <span className="flex items-center gap-1 font-semibold text-slate-900"><Banknote className="w-4 h-4" /> £{job.salary_min} - £{job.salary_max}</span>
                        </div>

                        <div className="prose max-w-none text-slate-600">
                            <h3 className="text-lg font-semibold text-slate-900">Description</h3>
                            <p>{job.description}</p>
                        </div>
                    </div>

                    {/* New Component */}
                    <ScheduleComparison studentSchedule={userSchedule} jobShifts={job.shifts} />

                </div>

                {/* Right Column: Actions & Summary */}
                <div className="space-y-6">
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sticky top-24">
                        <div className="mb-6">
                            <div className="text-sm text-slate-500 mb-1">Match Score</div>
                            <div className="flex items-center gap-2">
                                <span className="text-4xl font-bold text-primary-600">{Math.round(job.match_analysis?.total_score || 0)}%</span>
                                <span className="px-2 py-0.5 rounded-full bg-primary-50 text-primary-700 text-sm font-medium">Great Fit</span>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <Button
                                className="w-full"
                                onClick={handleApply}
                                disabled={applying || hasApplied}
                                variant={hasApplied ? "outline" : "primary"}
                            >
                                {hasApplied ? (applicationStatus === 'Saved' ? "Saved" : "Applied") : (applying ? "Sending..." : "Apply Now")}
                            </Button>
                            <Button variant="outline" className="w-full" disabled={hasApplied && applicationStatus === 'Saved'}>
                                {hasApplied && applicationStatus === 'Saved' ? "Saved" : "Save Job"}
                            </Button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default JobDetail;
