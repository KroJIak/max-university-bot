import type { IconProps } from './types';

export function BellIcon({ className }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        d="M12 5.5c2.7614 0 5 2.23858 5 5v2.2396c0 .4898.1798.9626.5052 1.3287l1.2756 1.4352C19.6407 16.4708 18.954 18 17.6597 18H6.34025c-1.29427 0-1.98098-1.5292-1.12112-2.4965l1.27567-1.4352c.32542-.3661.50518-.8389.50518-1.3287L7 10.5c0-2.76142 2.23858-5 5-5Zm0 0V3M11 21h2"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

