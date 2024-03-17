/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./recipester/templates/**/*.dhtml", "./recipester/*.py"],
  daisyui: {
    themes: ["light", "dark"],
  },
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("daisyui"),
  ],
};
