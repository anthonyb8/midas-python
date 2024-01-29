/** @type {import('tailwindcss').Config} */

const { colors, fontFamily, border } = require('./theme');

module.exports = {
  content: [ 
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",],
  
  theme: {
    extend: {
      colors: {
        darkBackground: colors.darkBackground,
        darkSecondaryBg: colors.darkSecondaryBackground
      },
      borderWidth: {
        darkBorder: border.widthDefault
      },
      borderColor: {
        darkBorderColor: border.colorDefault
      },
      textColor: {
        darkTextColor : colors.textColor
      },
      fontFamily: {
        darkFontFamily: fontFamily.default
      },
    },
  },
  plugins: [],
}



