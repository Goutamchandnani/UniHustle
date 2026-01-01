import React from 'react';
import { clsx } from 'clsx';

const StatsCard = ({ label, value, icon: Icon, colorClass }) => {
    return (
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
            <div className={clsx("p-3 rounded-lg", colorClass)}>
                <Icon className="w-6 h-6 text-white" />
            </div>
            <div>
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <p className="text-2xl font-bold text-slate-900">{value}</p>
            </div>
        </div>
    );
};

export default StatsCard;
