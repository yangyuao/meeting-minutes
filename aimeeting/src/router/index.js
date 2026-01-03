import Vue from 'vue'
import VueRouter from 'vue-router'
import MeetingMinutes from '../views/MeetingMinutes.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    redirect: '/meeting-minutes'
  },
  {
    path: '/meeting-minutes',
    name: 'MeetingMinutes',
    component: MeetingMinutes
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router


