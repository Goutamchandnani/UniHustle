import React from 'react';
import PropTypes from 'prop-types';
import { MapPin, Clock, Calendar, CheckCircle, AlertTriangle, XCircle, Heart, Eye } from 'lucide-react';
import Button from './ui/Button';
import Card from './ui/Card';

const JobCard = ({ job, onApply, onSave, onDismiss, onClick }) => {
    const {
        title,
        company_name,
        location,
        salary_min,
        salary_max,
        salary_type = 'per hour',
        posted_at,
        match_score = 0,
        schedule_analysis = []
    } = job;

    // --- Helpers ---
    const getMatchColor = (score) => {
        if (score >= 90) return 'bg-green-100 text-green-700 border-green-200';
        if (score >= 80) return 'bg-blue-100 text-blue-700 border-blue-200';
        if (score >= 70) return 'bg-sky-100 text-sky-700 border-sky-200';
        return 'bg-slate-100 text-slate-600 border-slate-200';
    };

    const getMatchLabel = (score) => {
        if (score >= 90) return 'Perfect Match';
        if (score >= 80) return 'Great Match';
        if (score >= 70) return 'Good Match';
        return 'Fair Match';
    };

    // Extract Location Data
    // Backend sends breakdown inside job object usually, or we pass it explicitly?
    // Let's look for it in job.match_breakdown first.
    let locData = job.match_breakdown?.location_data || {};

    // Badge Styles
    const getBadgeStyle = (color) => {
        switch (color) {
            case 'green': return 'bg-green-100 text-green-800';
            case 'blue': return 'bg-blue-100 text-blue-800';
            case 'purple': return 'bg-purple-100 text-purple-800';
            case 'yellow': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    // Determine Schedule Status
    const getScheduleStatus = (analysis) => {
        if (!analysis || analysis.length === 0) {
            return { icon: CheckCircle, color: 'text-green-600', text: 'Perfect schedule fit' };
        }
        const hasConflict = analysis.some(msg => msg.includes('❌'));
        if (hasConflict) {
            return { icon: XCircle, color: 'text-red-500', text: 'Schedule conflict' };
        }
        return { icon: AlertTriangle, color: 'text-amber-500', text: 'Tight timing' };
    };

    const scheduleStatus = getScheduleStatus(schedule_analysis);
    const StatusIcon = scheduleStatus.icon;

    // Format Salary
    const salaryDisplay = salary_max
        ? `£${salary_min} - £${salary_max}`
        : `£${salary_min}`;

    return (
        <div
            className="group relative bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden cursor-pointer"
            onClick={onClick}
            role="article"
            aria-label={`Job listing for ${title} at ${company_name}`}
        >
            {/* Badges Row */}
            <div className="absolute top-4 right-4 flex gap-2">
                {/* Location Badge */}
                {locData.badge && (
                    <span className={`px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${getBadgeStyle(locData.badge_color)}`}>
                        {locData.badge}
                    </span>
                )}
                {/* Match Score */}
                {match_score > 0 && (
                    <span className={`px-2 py-1 rounded-md text-xs font-bold border ${getMatchColor(match_score)}`}>
                        {Math.round(match_score)}%
                    </span>
                )}
            </div>

            <div className="p-5">
                {/* Header */}
                <div className="mb-4 pr-20">
                    <h3 className="text-lg font-bold text-slate-900 group-hover:text-primary-600 transition-colors line-clamp-1">
                        {title}
                    </h3>
                    <p className="text-slate-500 font-medium text-sm">{company_name}</p>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-4 text-sm text-slate-600">
                    <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-slate-900">{salaryDisplay}</span>
                        <span className="text-xs text-slate-400">/hr</span>
                    </div>
                    <div className="flex items-center gap-1.5 line-clamp-1">
                        <MapPin className="w-4 h-4 text-slate-400" />
                        {location}
                    </div>
                </div>

                {/* Schedule Indicator */}
                <div className={`flex items-start gap-2 p-2 rounded-lg bg-slate-50 border border-slate-100 text-sm mb-4 ${scheduleStatus.color}`}>
                    <StatusIcon className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span className="font-medium text-slate-700">{scheduleStatus.text}</span>
                </div>

                {/* Footer / Urgency */}
                <div className="flex justify-between items-center text-xs text-slate-400 border-t border-slate-100 pt-3 mb-4">
                    <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" /> 2h ago
                        </span>
                        <span className="flex items-center gap-1 text-primary-600 font-medium">
                            <Eye className="w-3 h-3" /> 12 viewing
                        </span>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                    <Button className="flex-1 py-1.5 text-sm" onClick={onApply}>
                        Quick Apply
                    </Button>
                    <button
                        onClick={onSave}
                        className="p-2 rounded-lg border border-slate-200 text-slate-400 hover:text-pink-500 hover:bg-pink-50 hover:border-pink-200 transition-colors"
                        aria-label="Save job"
                    >
                        <Heart className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};

JobCard.propTypes = {
    job: PropTypes.shape({
        title: PropTypes.string.isRequired,
        company_name: PropTypes.string,
        location: PropTypes.string,
        salary_min: PropTypes.number,
        salary_max: PropTypes.number,
        match_score: PropTypes.number,
        schedule_analysis: PropTypes.array
    }).isRequired,
    onApply: PropTypes.func,
    onSave: PropTypes.func,
    onDismiss: PropTypes.func,
    onClick: PropTypes.func,
};

export default JobCard;
