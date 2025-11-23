/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx}",
    ],
    theme: {
        extend: {
            colors: {
                gold: {
                    50: '#FFF9E5',
                    100: '#FFF2CC',
                    200: '#FFE699',
                    300: '#FFD966',
                    400: '#FFC107',
                    500: '#E6AD06',
                    600: '#CC9905',
                    700: '#B38604',
                    800: '#997303',
                    900: '#806003',
                },
                'black-rich': '#0A0A0A',
            }
        },
    },
    plugins: [],
}
