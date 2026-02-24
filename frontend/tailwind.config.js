module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Mode light
        light: {
          background: "#ffffff",
          foreground: "#1a1a1a",
          card: "#f5f5f5",
          border: "#e5e5e5",
          muted: "#9ca3af",
        },
        // Mode dark
        dark: {
          background: "#0f0f15",
          foreground: "#ffffff",
          card: "#1a1a24",
          border: "#2d2d3a",
          muted: "#6b7280",
        },
        // Palette Finova - Modernes et vibrantes
        finova: {
          primary: "#2563eb", // Bleu vibrant - couleur principale
          secondary: "#7c3aed", // Violet - accents
          accent: "#06b6d4", // Cyan - highlights
          success: "#10b981", // Vert - positif
          warning: "#f59e0b", // Amber - attention
          danger: "#ef4444", // Rouge - erreur
        },
      },
      backgroundImage: {
        'gradient-finova': 'linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #06b6d4 100%)',
        'gradient-dark': 'linear-gradient(135deg, #1a1a24 0%, #2d2d3a 100%)',
      },
      boxShadow: {
        'finova': '0 20px 25px -5px rgba(37, 99, 235, 0.1)',
        'finova-lg': '0 25px 50px -12px rgba(37, 99, 235, 0.15)',
      },
    },
  },
  plugins: [],
};
