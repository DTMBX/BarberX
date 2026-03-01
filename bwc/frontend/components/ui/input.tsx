'use client';

import { forwardRef, type InputHTMLAttributes, useId } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  helperText?: string;
  /** Visually hide the label (still accessible to screen readers) */
  hideLabel?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, hideLabel, className, id: providedId, ...props }, ref) => {
    const autoId = useId();
    const id = providedId || autoId;
    const errorId = error ? `${id}-error` : undefined;
    const helperId = helperText ? `${id}-helper` : undefined;

    return (
      <div className="space-y-1.5">
        {label && (
          <label
            htmlFor={id}
            className={cn('block text-sm font-medium text-slate-400', hideLabel && 'sr-only')}
          >
            {label}
            {props.required && (
              <span className="text-red-400 ml-0.5" aria-hidden="true">
                *
              </span>
            )}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          aria-invalid={!!error}
          aria-describedby={[errorId, helperId].filter(Boolean).join(' ') || undefined}
          className={cn(
            'block w-full rounded-lg border bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500',
            'transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-slate-900',
            error
              ? 'border-red-500 focus:ring-red-500'
              : 'border-slate-600 focus:ring-blue-500 hover:border-slate-500',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            className
          )}
          {...props}
        />
        {error && (
          <p id={errorId} className="text-xs text-red-400" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={helperId} className="text-xs text-slate-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
