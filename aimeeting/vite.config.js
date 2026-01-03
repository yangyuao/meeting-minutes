import { defineConfig } from 'vite'
import { createVuePlugin } from 'vite-plugin-vue2'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [createVuePlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0', // 允许外部访问
    https: true, // 启用 HTTPS
    open: true,
    strictPort: false,
    // 确保静态文件正确服务
    fs: {
      strict: false
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    https: true, // 预览服务器也启用 HTTPS
    cors: true
  },
  define: {
    // 为了兼容 Vue 2 的 process.env 写法
    'process.env': {}
  }
})

