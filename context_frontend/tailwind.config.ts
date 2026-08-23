import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0a0a0c",
          panel: "#111114",
          raised: "#17171b",
          hover: "#1c1c21",
        },
        border: {
          DEFAULT: "#232328",
          subtle: "#1a1a1e",
        },
        accent: {
          DEFAULT: "#6d5bf5",
          hover: "#7d6cf7",
          muted: "#6d5bf5",
        },
        ink: {
          DEFAULT: "#e8e8ea",
          muted: "#9a9aa3",
          faint: "#5f5f68",
        },
        success: "#3dd68c",
        danger: "#f0555c",
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        xl: "10px",
        "2xl": "14px",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.2s ease-out",
        "pulse-dot": "pulse-dot 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
