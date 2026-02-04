/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#64748b',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        dark: {
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        // 甘特图项目大类主题色
        gantt: {
          category1: '#1890ff', // 蓝色
          category2: '#52c41a', // 绿色
          category3: '#faad14', // 黄色
          category4: '#f5222d', // 红色
          category5: '#722ed1', // 紫色
          category6: '#13c2c2', // 青色
          category7: '#fa8c16', // 橙色
          category8: '#eb2f96', // 粉色
        },
        // 甘特图任务状态色
        ganttTask: {
          pending: '#94a3b8', // 待开始
          active: '#1890ff', // 进行中
          completed: '#22c55e', // 已完成
          delayed: '#ef4444', // 已延期
          cancelled: '#64748b', // 已取消
        },
        // 甘特图进度条颜色
        ganttProgress: {
          low: '#60a5fa', // 0-33%
          medium: '#3b82f6', // 34-66%
          high: '#2563eb', // 67-100%
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}