<template>
  <div class="min-h-screen bg-gray-900 text-white relative overflow-hidden">
    <!-- 星空背景 -->
    <div class="starfield fixed inset-0 pointer-events-none z-0" ref="starfield"></div>

    <!-- 星云效果 -->
    <div class="nebula nebula-1 fixed rounded-full blur-3xl pointer-events-none z-0"></div>
    <div class="nebula nebula-2 fixed rounded-full blur-3xl pointer-events-none z-0"></div>
    <div class="nebula nebula-3 fixed rounded-full blur-3xl pointer-events-none z-0"></div>

    <!-- 萤火虫容器 -->
    <div class="fixed inset-0 pointer-events-none z-1" ref="fireflies"></div>

    <!-- 主内容 -->
    <div class="relative z-10 flex items-center justify-center min-h-screen">
      <div class="w-full max-w-md p-8 bg-gray-800 rounded-lg text-center">
        <p>正在跳转到登录/注册页面...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 星空和萤火虫相关
const starfield = ref(null)
const fireflies = ref(null)
const firefliesData = ref([])

onMounted(() => {
  // 创建星空和萤火虫效果
  createStarfield()
  createFireflies()
  animateFireflies()
  // 重定向
  setTimeout(() => {
    router.replace({ path: '/login', query: { mode: 'register' } })
  }, 1000) // 短暂显示效果后跳转
})

// 星空和萤火虫动画函数
const createStarfield = () => {
  if (!starfield.value) return

  const starCount = 150
  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div')
    star.className = 'star'

    const size = Math.random() * 2 + 1
    const x = Math.random() * 100
    const y = Math.random() * 100
    const duration = Math.random() * 3 + 2
    const minOpacity = Math.random() * 0.3 + 0.2

    star.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${x}%;
      top: ${y}%;
      --duration: ${duration}s;
      --min-opacity: ${minOpacity};
      animation-delay: ${Math.random() * duration}s;
    `

    starfield.value.appendChild(star)
  }
}

const createFireflies = () => {
  if (!fireflies.value) return

  const count = 25
  for (let i = 0; i < count; i++) {
    const firefly = document.createElement('div')
    firefly.className = 'firefly'

    const fireflyData = {
      el: firefly,
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: 0,
      vy: 0,
      phase: Math.random() * Math.PI * 2
    }

    firefliesData.value.push(fireflyData)
    fireflies.value.appendChild(firefly)
  }
}

const animateFireflies = () => {
  firefliesData.value.forEach(f => {
    f.phase += 0.02
    f.vx += Math.sin(f.phase) * 0.01
    f.vy += Math.cos(f.phase * 0.7) * 0.01

    f.vx *= 0.99
    f.vy *= 0.99

    f.x += f.vx
    f.y += f.vy

    // 边界检测
    if (f.x < 0) f.x = window.innerWidth
    if (f.x > window.innerWidth) f.x = 0
    if (f.y < 0) f.y = window.innerHeight
    if (f.y > window.innerHeight) f.y = 0

    f.el.style.transform = `translate(${f.x}px, ${f.y}px)`
  })

  requestAnimationFrame(animateFireflies)
}
</script>

<style>
/* 星空背景 */
.starfield {
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: #ffffff;
  border-radius: 50%;
  animation: twinkle var(--duration) ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: var(--min-opacity); transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 星云效果 */
.nebula {
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

.nebula-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 100, 150, 0.15) 0%, transparent 70%);
  top: -200px;
  right: -100px;
}

.nebula-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(100, 0, 120, 0.1) 0%, transparent 70%);
  bottom: 10%;
  left: -100px;
}

.nebula-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(0, 212, 170, 0.08) 0%, transparent 70%);
  top: 40%;
  right: 20%;
}

/* 萤火虫粒子 */
.firefly {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #00d4aa;
  border-radius: 50%;
  box-shadow:
    0 0 6px 2px #00d4aa,
    0 0 12px 4px rgba(0, 212, 170, 0.3),
    0 0 20px 6px rgba(0, 212, 170, 0.1);
  pointer-events: none;
  z-index: 1;
  animation: firefly-glow 3s ease-in-out infinite;
}

@keyframes firefly-glow {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}
</style>
