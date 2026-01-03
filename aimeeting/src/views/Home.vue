<template>
  <div class="home">
    <h1>首页</h1>
    <el-button type="primary" @click="goToMeetingMinutes">进入会议纪要</el-button>
  </div>
</template>

<script>
export default {
  name: 'Home',
  methods: {
    goToMeetingMinutes() {
      this.$router.push('/meeting-minutes')
    }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 20px;
}
</style>


