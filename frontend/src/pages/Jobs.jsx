import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import JobCard from '../components/JobCard';
import { Search, Filter } from 'lucide-react';

const Jobs = () => {
    const navigate = useNavigate();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                // Fetch all jobs (for now, maybe paginated later)
                const response = await api.get('/jobs?per_page=50');
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

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {jobs.length > 0 ? (
                    jobs.map(job => (
                        <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)} />
                    ))
                ) : (
                    <div className="col-span-full text-center py-12 text-slate-500">
                        No jobs found.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Jobs;
