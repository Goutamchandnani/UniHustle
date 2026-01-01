import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const Button = ({ children, variant = 'primary', className, ...props }) => {
    const baseStyles = "px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";

    const variants = {
        primary: "bg-sky-600 text-white hover:bg-sky-700 focus:ring-sky-500",
        secondary: "bg-secondary text-white hover:bg-slate-600 focus:ring-secondary",
        outline: "border-2 border-sky-600 text-sky-600 hover:bg-sky-50 focus:ring-sky-500",
        ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
    };

    return (
        <button
            className={twMerge(baseStyles, variants[variant], className)}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;
