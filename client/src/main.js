import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import BootstrapVue from 'bootstrap-vue'

import './custom.scss'
import * as axios from 'axios'

Vue.config.productionTip = false
Vue.use(BootstrapVue)
Vue.prototype.$http = axios

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
