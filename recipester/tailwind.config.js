/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./recipester/templates/**/*.dhtml", "./recipester/*.py"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
};
