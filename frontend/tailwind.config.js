/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: "#0B1220",
          surface: "#121B2E",
          alt: "#17233A",
          border: "#253347",
        },
        ink: {
          primary: "#E8EDF6",
          secondary: "#94A3B8",
          muted: "#5B6B85",
        },
        brand: {
          DEFAULT: "#7C9EFF",
          soft: "#3D4E85",
        },
        pulse: {
          healthy: "#6EE7C9",
          warning: "#FBBF24",
          risk: "#FB7185",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
      },
      backgroundImage: {
        "glass-gradient": "linear-gradient(135deg, rgba(124,158,255,0.08), rgba(110,231,201,0.03))",
      },
      keyframes: {
        pulseLine: {
          "0%, 100%": { transform: "scaleY(1)" },
          "50%": { transform: "scaleY(1.6)" },
        },
      },
      animation: {
        pulseLine: "pulseLine 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
