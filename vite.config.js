import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // base: '/' 確保 AWS Amplify 靜態資源路徑正確
  // 若部署至子路徑 (e.g. /app/)，請改為 '/app/'
  base: '/',
})
