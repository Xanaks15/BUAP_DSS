/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                corporate: {
                    blue: '#0074C8',
                    green: '#00A65A',
                    red: '#C80000',
                    gray: '#F3F4F6', // Professional gray background
                    dark: '#1F2937'
                }
            }
        },
    },
    plugins: [],
}
