import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import JobCard from '../components/JobCard';
import { Search, Filter } from 'lucide-react';

const Jobs = () => {
    const navigate = useNavigate();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    const [showOthers, setShowOthers] = useState(false);

    // Grouping
    const sortJobs = (allJobs) => {
        const t1 = [], t2 = [], t3 = [], t4 = [];
        allJobs.forEach(job => {
            const tier = job.match_breakdown?.location_data?.tier || 5;
            if (tier === 1) t1.push(job);
            else if (tier === 2) t2.push(job);
            else if (tier === 3 || tier === 4) t3.push(job); // Nearby + Tier 4
            else t4.push(job);
        });
        return { tier1: t1, tier2: t2, tier3: t3, others: t4 };
    };

    const { tier1, tier2, tier3, others } = React.useMemo(() => sortJobs(jobs), [jobs]);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                // Fetch all jobs (increased limit for better visibility)
                const response = await api.get('/jobs?per_page=100');
                setJobs(response.data.jobs);
            } catch (err) {
                console.error("Failed to load jobs", err);
            } finally {
                setLoading(false);
            }
        };
        fetchJobs();
    }, []);

    if (loading) return (
        <div className="max-w-7xl mx-auto px-4 py-8 text-center text-slate-500">
            Loading all jobs...
        </div>
    );

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-slate-900">All Jobs</h1>
                <div className="flex gap-2">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Search jobs..."
                            className="pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                        />
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50">
                        <Filter className="w-4 h-4" />
                        Filters
                    </button>
                </div>
            </div>

            {/* Tier 1: Remote & Primary City */}
            {tier1.length > 0 && (
                <section>
                    <div className="flex items-center gap-2 mb-4">
                        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                            📍 Perfect Location Matches
                        </h2>
                        <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-xs font-bold">
                            {tier1.length}
                        </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {tier1.map(job => (
                            <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)} />
                        ))}
                    </div>
                </section>
            )}

            {/* Tier 2: Preferred Cities */}
            {tier2.length > 0 && (
                <section>
                    <div className="flex items-center gap-2 mb-4 mt-8">
                        <h2 className="text-xl font-bold text-slate-900">⭐ Preferred Cities</h2>
                        <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-xs font-bold">
                            {tier2.length}
                        </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {tier2.map(job => (
                            <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)} />
                        ))}
                    </div>
                </section>
            )}

            {/* Tier 3: Nearby Cities (Expandable, but sticking to simple for now as per snippet) */}
            {tier3.length > 0 && (
                <section>
                    <div className="flex items-center gap-2 mb-4 mt-8">
                        <h2 className="text-xl font-bold text-slate-900">🚍 Nearby Matches</h2>
                        <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-xs font-bold">
                            {tier3.length}
                        </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {tier3.map(job => (
                            <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)} />
                        ))}
                    </div>
                </section>
            )}

            {/* Tier 4+: Other (Hidden by toggle if huge, but let's show for now) */}
            {others.length > 0 && (
                <section>
                    <button
                        onClick={() => setShowOthers(!showOthers)}
                        className="flex items-center gap-2 mb-4 mt-8 hover:text-primary-600 transition-colors"
                    >
                        <h2 className="text-xl font-bold text-slate-700">
                            {showOthers ? '▼' : '▶'} Other Locations
                        </h2>
                        <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-xs font-bold">
                            {others.length}
                        </span>
                    </button>

                    {showOthers && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-80 lg:opacity-100">
                            {others.map(job => (
                                <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)} />
                            ))}
                        </div>
                    )}
                </section>
            )}

            {jobs.length === 0 && (
                <div className="col-span-full text-center py-12 text-slate-500">
                    No jobs found.
                </div>
            )}
        </div>
    );
};

export default Jobs;
