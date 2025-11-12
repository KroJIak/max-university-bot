import type { IconProps } from './types';

export function HomeIcon({ className }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 15 15"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M7.07926.222253c.23349-.229687.60804-.229687.84153 0l6.75 6.640017c.2362.23238.2393.61226.007.84849-.2324.23624-.6123.23936-.8485.00697l-.8293-.81572V12.5c0 .2761-.2238.5-.5.5H2.5c-.27614 0-.5-.2239-.5-.5V6.90201l-.82923.81572c-.23623.23239-.61612.22927-.8485-.00697-.232382-.23623-.229262-.61611.007-.84849l6.75-6.640017ZM7.50002 1.49163 12 5.91831V12h-2V8.49999c0-.27614-.22383-.5-.5-.5h-3c-.27614 0-.5.22386-.5.5V12h-3V5.91831L7.5 1.49163Zm-.5 10.50836h2V9.49999h-2v2.5Z"
        fill="currentColor"
      />
    </svg>
  );
}

