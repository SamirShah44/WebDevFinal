import type { Config } from 'tailwindcss';
import daisyui from 'daisyui';

export default {
  content: ["./TeenPatti/templates/**/*.html", "./TeenPatti/**/templates/**/*.html"],
  darkMode: "media",
  theme: {
    extend: {},
  },
  daisyui: {
    themes: [
      "light",
      "dark",
    ]
  },
  plugins: [daisyui],
} satisfies Config;