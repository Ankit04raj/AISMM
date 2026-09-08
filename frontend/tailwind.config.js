export default {
  content: ['./index.html', './src/**/*.{js,jsx}'], darkMode: 'class',
  theme: { extend: { colors: {
    obsidian: { bg: '#07090E', card: '#0D121F', cardHover: '#131B2E', border: '#1E293B', subtle: '#2A364F' },
    brand: { 50:'#f5f3ff',100:'#ede9fe',200:'#ddd6fe',300:'#c4b5fd',400:'#a78bfa',500:'#8b5cf6',600:'#7C3AED',700:'#6d28d9',800:'#5b21b6',900:'#4c1d95' },
    neon: { cyan:'#06B6D4',cyanGlow:'#22D3EE',violet:'#7C3AED',pink:'#EC4899',emerald:'#10B981',amber:'#F59E0B' }
  } } }, plugins: []
}
