import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import path from "path"
import components from 'unplugin-vue-components/vite';
import { AntDesignXVueResolver } from 'ant-design-x-vue/resolver';

// https://vite.dev/config/
export default defineConfig({
  plugins: [ components({
    resolvers: [AntDesignXVueResolver()]
  }),vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    // Vite路径别名配置
    alias: {
      '@': path.resolve('./src')
    }
  }

})
