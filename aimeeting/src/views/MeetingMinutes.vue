<template>
  <div class="data-div">
    <!-- <div class="top-div">
      <div class="top-left-div" @click="handleBackHome">
        <el-avatar :src="backImage" :size="30" />
        <span>返回首页</span>
      </div>
      <div class="top-right-div">
        <div class="right-item">
          <a href="/file/PPT创作用户操作手册.pptx" download="PPT创作用户操作手册.pptx">
            <img :src="downfile" style="margin-right: 10px;" />
            <span>PPT创作用户操作手册</span>
          </a>
        </div>
        <div class="right-item" @click="handleOpenDisc">
          <img :src="xieyiImage" />
          <span>知识库用户协议</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px">
          <el-avatar :src="userAvatar" />
          <span style="color: white; font-size: 18px">{{ currNickName }}</span>
        </div>
      </div>
    </div> -->
    <div class="content-div">
      <MeetingContent style="width: 100%; height: 100%;" />
    </div>
  </div>
</template>

<script>
import backImage from "@/assets/images/data/icon_back.svg";
import xieyiImage from "@/assets/images/data/icon_xieyi.svg";
import downfile from "@/assets/images/data/downfile.svg";
import userAvatar from "@/assets/images/home/tou_xiang_new.svg";
import MeetingContent from '../components/MeetingContent.vue'

export default {
  components: {
    MeetingContent
  },
  name: "MeetingMinutes",
  data() {
    return {
      backImage,
      xieyiImage,
      downfile,
      currNickName: this.$store.getters.nickName,
      userAvatar,
    };
  },
  mounted() {
  },
  methods: {
    handleBackHome() {
      this.$router.push({ path: "/home" });
    },
    handleOpenDisc() {
      const eventBus = require("@/utils/useDisclaimerAgreement").default;
      eventBus.$emit("show-disclaimer-modal", {
        buttonState: false,
        show: true,
      });
    },
  },
};
</script>

<style scoped lang="scss">
.data-div {
  width: 100%;
  height: 100%;
  background-size: cover;
  display: flex;
  flex-direction: column;
  .top-div {
    flex: 1;
    display: flex;
    justify-content: space-between;
    .top-left-div {
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 12px;
      span {
        color: rgb(226, 226, 226);
        font-size: 15px;
      }
    }
    .top-right-div {
      display: flex;
      align-items: center;
      gap: 20px;
      .right-item {
        display: flex;
        gap: 6px;
        align-items: center;
        cursor: pointer;
        span {
          color: rgb(226, 226, 226);
        }
      }
    }
  }
  .content-div {
    flex: 10;
    display: flex;
    height: 100%;
    border-radius: 12px;
    overflow: hidden;
    background-color: aliceblue;
    background-size: cover;
  }
}
</style>

