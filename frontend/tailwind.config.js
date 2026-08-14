module.exports = {
  content: [
    './app/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        background: '#121212',
        card: '#18181B', // zinc-900
        border: '#27272A', // zinc-800
        primary: '#FAFAFA', // zinc-50
        secondary: '#A1A1AA', // zinc-400
        input: '#18181B',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    }
  },
  plugins: []
};
