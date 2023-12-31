/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [ 
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",],
  theme: {
    extend: {
      colors: {
        darkBackground: 'rgb(53,54,58)', // Example of a custom color
      },
      borderWidth: {
        default: '1px', // Custom border width
      },
      borderColor: theme => ({
        default: theme('colors.gray.300', 'currentColor'), // Custom border color
      }),
      textColor: {
        'default': 'white', // Custom text color
      },
      fontFamily: {
        'default': ['sans-serif'], // Custom font family
      },
    },
  },
  plugins: [],
}



