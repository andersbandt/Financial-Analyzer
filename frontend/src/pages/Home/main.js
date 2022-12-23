import { createApp } from 'vue';
import App from './App.vue';
import VueNavigationBar from '/src/components/navbar.js';

import router from '/routers.js'

const app = createApp(App);

app.use(router);

app.component('vue-navigation-bar', VueNavigationBar);

app.mount('#app');