'use client';

import Link from 'next/link';

/**
 * Error handling states (spec §43)
 *
 * Provides user-friendly error pages for all common error conditions.
 * Never display raw JSON errors to users.
 */

interface ErrorStateProps {
  title: string;
  message: string;
  action?: {
    label: string;
    href: string;
  };
  illustration?: 'network' | 'auth' | 'not-found' | 'server' | 'empty';
}

function ErrorIllustration({ type }: { type: string }) {
  const iconClass = 'h-12 w-12 text-gray-300';

  switch (type) {
    case 'network':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21l2.5-2.5m-5 0L12 21m0-9a9 9 0 100-9m0 9v.008m0-5.008a5 5 0 100-5" />
        </svg>
      );
    case 'auth':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
      );
    case 'not-found':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
        </svg>
      );
    case 'empty':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m6 4.125l2.25 2.25m0 0l2.25 2.25M12 13.875l2.25-2.25M12 13.875l-2.25 2.25M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
        </svg>
      );
    default:
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      );
  }
}

export function ErrorState({ title, message, action, illustration = 'server' }: ErrorStateProps) {
  return (
    <div className="flex min-h-[400px] items-center justify-center p-8">
      <div className="text-center max-w-sm">
        <div className="flex justify-center mb-4">
          <ErrorIllustration type={illustration} />
        </div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">{title}</h2>
        <p className="text-sm text-gray-600 mb-6">{message}</p>
        {action && (
          <Link
            href={action.href}
            className="inline-flex items-center rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 transition-colors"
          >
            {action.label}
          </Link>
        )}
      </div>
    </div>
  );
}

// ─── Predefined Error States ────────────────────────────────────────────────

export function NetworkError() {
  return (
    <ErrorState
      title="Connection lost"
      message="We couldn't reach the server. Please check your internet connection and try again."
      action={{ label: 'Try again', href: '#' }}
      illustration="network"
    />
  );
}

export function UnauthorizedError() {
  return (
    <ErrorState
      title="Sign in required"
      message="You need to be signed in to access this page."
      action={{ label: 'Sign in', href: '/sign-in' }}
      illustration="auth"
    />
  );
}

export function NotFoundError({ resource = 'Page' }: { resource?: string }) {
  return (
    <ErrorState
      title={`${resource} not found`}
      message={`The ${resource.toLowerCase()} you're looking for doesn't exist or has been moved.`}
      action={{ label: 'Go home', href: '/' }}
      illustration="not-found"
    />
  );
}

export function ServerError() {
  return (
    <ErrorState
      title="Something went wrong"
      message="We're having trouble loading this page. Please try again in a moment."
      action={{ label: 'Try again', href: '#' }}
      illustration="server"
    />
  );
}

export function EmptyState({ title, message, action }: { title: string; message: string; action?: { label: string; href: string } }) {
  return (
    <ErrorState
      title={title}
      message={message}
      action={action}
      illustration="empty"
    />
  );
}
