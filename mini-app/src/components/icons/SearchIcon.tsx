import type { IconProps } from './types';

export function SearchIcon({ className }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="11" cy="11" r="7.5" stroke="currentColor" strokeWidth="1.8" fill="none" />
      <line
        x1="17.25"
        y1="17.25"
        x2="22"
        y2="22"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

