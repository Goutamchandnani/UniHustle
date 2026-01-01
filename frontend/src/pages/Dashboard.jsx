import React, { useEffect, useState } from 'react';
import api from '../services/api';
import JobCard from '../components/JobCard';
import StatsCard from '../components/dashboard/StatsCard';
import { Briefcase, Send, Calendar, Star, Bell, Clock } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const navigate = useNavigate();
    const [jobs, setJobs] = useState([]);
    const [applications, setApplications] = useState([]);
    const [stats, setStats] = useState({ matches: 0, applications: 0, interviews: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadDashboard = async () => {
            try {
                const [jobsRes, appsRes, statsRes] = await Promise.all([
                    api.get('/jobs?sort_by=match_score&per_page=3'), // Top 3 matches
                    api.get('/applications'),
                    api.get('/stats')
                ]);
                setJobs(jobsRes.data.jobs);
                setApplications(appsRes.data);
                setStats(statsRes.data);
            } catch (err) {
                console.error("Dashboard load failed", err);
            } finally {
                setLoading(false);
            }
        };
        loadDashboard();
    }, []);

    if (loading) return (
        <div className="max-w-7xl mx-auto px-4 py-8 animate-pulse">
            <div className="h-8 bg-slate-200 rounded w-1/3 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="h-24 bg-slate-200 rounded-xl"></div>
                <div className="h-24 bg-slate-200 rounded-xl"></div>
                <div className="h-24 bg-slate-200 rounded-xl"></div>
            </div>
        </div>
    );

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

            {/* 1. Welcome Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Good morning, {stats.student_name || 'Student'}! 👋</h1>
                    <p className="text-slate-500 mt-1">
                        You have <span className="text-primary-600 font-bold">{stats.matches} new matches</span> waiting for you today.
                    </p>
                </div>
                <button className="relative p-2 text-slate-400 hover:text-slate-600">
                    <Bell className="w-6 h-6" />
                    <span className="absolute top-1.5 right-2 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                </button>
            </div>

            {/* 4. Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatsCard
                    label="New Matches"
                    value={stats.matches}
                    icon={Star}
                    colorClass="bg-yellow-500"
                />
                <StatsCard
                    label="Applications"
                    value={stats.applications}
                    icon={Send}
                    colorClass="bg-blue-500"
                />
                <StatsCard
                    label="Interviews"
                    value={stats.interviews}
                    icon={Calendar}
                    colorClass="bg-purple-500"
                />
            </div>

            {/* 3. Perfect Matches */}
            <section>
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                        <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" /> Top Matches for You
                    </h2>
                    <Link to="/jobs" className="text-sm font-medium text-primary-600 hover:text-primary-700">View All</Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {jobs.length > 0 ? (
                        jobs.map(job => (
                            <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)} />
                        ))
                    ) : (
                        <div className="col-span-full p-8 text-center bg-slate-50 rounded-xl text-slate-500">
                            No perfect matches found yet. Check your schedule settings!
                        </div>
                    )}
                </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* 6. Recent Applications */}
                <div className="lg:col-span-2">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-bold text-slate-900">Recent Applications</h2>
                        <Link to="/applications" className="text-sm font-medium text-primary-600 hover:text-primary-700">View All</Link>
                    </div>
                    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                        {applications.length > 0 ? (
                            <div className="divide-y divide-slate-100">
                                {applications.slice(0, 5).map(app => (
                                    <div key={app.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-slate-100 rounded-lg">
                                                <Briefcase className="w-5 h-5 text-slate-500" />
                                            </div>
                                            <div>
                                                <div className="font-medium text-slate-900">{app.job_title}</div>
                                                <div className="text-sm text-slate-500">{app.company}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <span className="text-xs text-slate-400">
                                                {new Date(app.applied_at).toLocaleDateString()}
                                            </span>
                                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border
                                        ${app.status === 'Applied' ? 'bg-blue-50 text-blue-700 border-blue-200' : ''}
                                        ${app.status === 'Interview' ? 'bg-purple-50 text-purple-700 border-purple-200' : ''}
                                        ${app.status === 'Saved' ? 'bg-slate-100 text-slate-600 border-slate-200' : ''}
                                     `}>
                                                {app.status}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="p-8 text-center text-slate-500">
                                You haven't applied to any jobs yet.
                            </div>
                        )}
                    </div>
                </div>

                {/* 5. Needs Attention */}
                <div>
                    <h2 className="text-lg font-bold text-slate-900 mb-4">Needs Attention</h2>
                    <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-4">
                        <div className="flex gap-3 items-start">
                            <div className="p-1.5 bg-amber-100 text-amber-600 rounded mt-0.5">
                                <Clock className="w-4 h-4" />
                            </div>
                            <div>
                                <div className="text-sm font-medium text-slate-900">Confirm Interview Availability</div>
                                <div className="text-xs text-slate-500 mt-0.5">Barista at Costa • By Tomorrow</div>
                            </div>
                        </div>
                        <div className="flex gap-3 items-start">
                            <div className="p-1.5 bg-red-100 text-red-600 rounded mt-0.5">
                                <Calendar className="w-4 h-4" />
                            </div>
                            <div>
                                <div className="text-sm font-medium text-slate-900">Update Profile</div>
                                <div className="text-xs text-slate-500 mt-0.5">Your availability expired yesterday.</div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </div>
    );
};

export default Dashboard;
