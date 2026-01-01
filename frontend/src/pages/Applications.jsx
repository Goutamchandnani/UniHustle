import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import { Building, Calendar, CheckCircle, Clock, XCircle } from 'lucide-react';

const Applications = () => {
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchApps = async () => {
            try {
                const res = await api.get('/applications');
                setApplications(res.data);
            } catch (error) {
                console.error("Failed to fetch applications", error);
            } finally {
                setLoading(false);
            }
        };
        fetchApps();
    }, []);

    const getStatusBadge = (status) => {
        switch (status) {
            case 'Applied': return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"><Clock className="w-3 h-3" /> Applied</span>;
            case 'Interview': return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"><CheckCircle className="w-3 h-3" /> Interview</span>;
            case 'Rejected': return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"><XCircle className="w-3 h-3" /> Rejected</span>;
            case 'Saved': return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">Saved</span>;
            default: return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status}</span>;
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Loading applications...</div>;

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-2xl font-bold text-slate-900 mb-6">My Applications</h1>

            {applications.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
                    <p className="text-slate-500 mb-4">You haven't applied to any jobs yet.</p>
                    <Link to="/jobs" className="text-primary-600 hover:text-primary-700 font-medium">Browse Jobs</Link>
                </div>
            ) : (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <ul className="divide-y divide-slate-100">
                        {applications.map((app) => (
                            <li key={app.id} className="p-4 sm:p-6 hover:bg-slate-50 transition-colors">
                                <Link to={`/jobs/${app.job_id}`} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                    <div>
                                        <h3 className="text-lg font-semibold text-slate-900">{app.job_title}</h3>
                                        <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                                            <Building className="w-4 h-4" /> {app.company}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <div className="text-xs text-slate-400 mb-1 flex items-center justify-end gap-1">
                                                <Calendar className="w-3 h-3" /> {new Date(app.applied_at).toLocaleDateString()}
                                            </div>
                                            {getStatusBadge(app.status)}
                                        </div>
                                    </div>
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default Applications;
