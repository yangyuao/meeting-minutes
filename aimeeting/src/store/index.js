import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    nickName: '用户'
  },
  getters: {
    nickName: state => state.nickName
  },
  mutations: {
    setNickName(state, name) {
      state.nickName = name
    }
  },
  actions: {
    setNickName({ commit }, name) {
      commit('setNickName', name)
    }
  }
})


