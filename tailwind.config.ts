import type { Config } from 'tailwindcss';
import daisyui from 'daisyui';

export default {
  content: ["./django/templates/**/*.html", "./django/**/templates/**/*.html"],
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