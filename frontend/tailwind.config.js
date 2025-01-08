/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'cyber': {
          bg: '#1B1F2A',
          primary: '#2D9CDB',
          secondary: '#E91E63',
          accent: '#FFC107',
        }
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgb(45 156 219 / 0.5), 0 0 15px rgb(45 156 219 / 0.5), 0 0 20px rgb(45 156 219 / 0.5)' },
          '100%': { boxShadow: '0 0 10px rgb(45 156 219), 0 0 30px rgb(45 156 219), 0 0 40px rgb(45 156 219)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [{
      cyberpunk: {
        ...require('daisyui/src/theming/themes')['cyberpunk'],
        'primary': '#2D9CDB',
        'secondary': '#E91E63',
        'accent': '#FFC107',
        'neutral': '#1B1F2A',
        'base-100': '#1B1F2A',
      }
    }],
  },
}
