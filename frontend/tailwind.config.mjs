/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'rgb(var(--color-primary-rgb, 59 130 246) / <alpha-value>)',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: 'var(--color-primary, #3b82f6)',
          600: 'var(--color-primary, #3b82f6)',
          700: 'var(--color-primary-dark, #2563eb)',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        accent: {
          DEFAULT: 'var(--color-accent, #8b5cf6)',
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: 'var(--color-accent, #8b5cf6)',
          700: '#7c3aed',
          800: '#6b21a8',
          900: '#581c87',
        },
      },
      backgroundColor: {
        'primary': 'var(--color-primary, #3b82f6)',
        'primary-dark': 'var(--color-primary-dark, #2563eb)',
        'primary-light': 'var(--color-primary-light, #60a5fa)',
        'accent': 'var(--color-accent, #8b5cf6)',
      },
      textColor: {
        'primary': 'var(--color-primary, #3b82f6)',
        'primary-dark': 'var(--color-primary-dark, #2563eb)',
        'primary-light': 'var(--color-primary-light, #60a5fa)',
        'accent': 'var(--color-accent, #8b5cf6)',
      },
      borderColor: {
        'primary': 'var(--color-primary, #3b82f6)',
        'primary-dark': 'var(--color-primary-dark, #2563eb)',
        'primary-light': 'var(--color-primary-light, #60a5fa)',
        'accent': 'var(--color-accent, #8b5cf6)',
      },
      ringColor: {
        'primary': 'var(--color-primary, #3b82f6)',
        'accent': 'var(--color-accent, #8b5cf6)',
      },
    },
  },
}


