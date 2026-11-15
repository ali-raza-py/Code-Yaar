import { cn } from "@/lib/utils";

function InfinityLoop({ className, ...props }: React.ComponentProps<"svg">) {
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn(className)}
      {...props}
    >
      <title>Loading...</title>
      <style>{`
        @keyframes loading-ui-infinity-dash {
          to {
            stroke-dashoffset: 256.58892822265625;
          }
        }
      `}</style>
      <path
        d="M24.3 30C11.4 30 5 43.3 5 50s6.4 20 19.3 20c19.3 0 32.1-40 51.4-40C88.6 30 95 43.3 95 50s-6.4 20-19.3 20C56.4 70 43.6 30 24.3 30z"
        stroke="currentColor"
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray="205.271142578125 51.317785644531256"
        style={{
          transform: "scale(0.8)",
          transformOrigin: "50px 50px",
          animationName: "loading-ui-infinity-dash",
          animationDuration: "var(--duration, 2s)",
          animationTimingFunction: "linear",
          animationIterationCount: "infinite",
        }}
      />
    </svg>
  );
}

export { InfinityLoop };

function Diamond(props: React.ComponentProps<"svg">) {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      role="status"
      aria-label="Loading"
      {...props}
    >
      <style>{`
        @keyframes spin-pixel {
          0% { opacity: 0; }
          1% { opacity: 1; }
          100% { opacity: 0; }
        }
        .pixel-1 { animation: spin-pixel 0.8s ease-in-out 0s infinite; }
        .pixel-2 { animation: spin-pixel 0.8s ease-in-out 0.1s infinite; }
        .pixel-3 { animation: spin-pixel 0.8s ease-in-out 0.2s infinite; }
        .pixel-4 { animation: spin-pixel 0.8s ease-in-out 0.3s infinite; }
        .pixel-5 { animation: spin-pixel 0.8s ease-in-out 0.4s infinite; }
        .pixel-6 { animation: spin-pixel 0.8s ease-in-out 0.5s infinite; }
        .pixel-7 { animation: spin-pixel 0.8s ease-in-out 0.6s infinite; }
        .pixel-8 { animation: spin-pixel 0.8s ease-in-out 0.7s infinite; }
      `}</style>
      {/* Top */}
      <rect className="pixel-1" x="8" y="0" width="4" height="4" />
      {/* Top Right */}
      <rect className="pixel-2" x="12" y="4" width="4" height="4" />
      {/* Right */}
      <rect className="pixel-3" x="16" y="8" width="4" height="4" />
      {/* Bottom Right */}
      <rect className="pixel-4" x="12" y="12" width="4" height="4" />
      {/* Bottom */}
      <rect className="pixel-5" x="8" y="16" width="4" height="4" />
      {/* Bottom Left */}
      <rect className="pixel-6" x="4" y="12" width="4" height="4" />
      {/* Left */}
      <rect className="pixel-7" x="0" y="8" width="4" height="4" />
      {/* Top Left */}
      <rect className="pixel-8" x="4" y="4" width="4" height="4" />
    </svg>
  );
}

export { Diamond };
