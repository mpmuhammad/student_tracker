import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'

export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/mentor',
      buildConfig: {
        outDir: path.resolve(__dirname, '../student_tracker/public/frontend'),
        baseUrl: '/assets/student_tracker/frontend/',
        indexHtmlPath: path.resolve(__dirname, '../student_tracker/www/mentor.html'),
      },
    }),
    vue(),
  ],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
})
