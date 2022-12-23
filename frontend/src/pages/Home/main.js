// import Vue from 'vue'
// import App from '/src/pages/Home/App.vue'

// Vue.config.productionTip = false

// new Vue({
//   render: h => h(App)
// }).$mount('#app')


// import { createApp } from 'vue'
// import App from './App.vue'

// import NavBar from '/src/components/NavBar.vue'

// import '/src/assets/main.css'


// import VueNavigationBar from 'vue-navigation-bar';
// import 'vue-navigation-bar/dist/vue-navigation-bar.css';


// // create and mount the root instance
// //createApp(App).mount('#app')

// const app = createApp(App);
// app.mount("#app")

// app.component('vue-navigation-bar', VueNavigationBar);

import { createApp } from 'vue';
import App from './App.vue';
import VueNavigationBar from '/src/components/navbar.js';
import { createRouter, createWebHistory } from 'vue-router';

const app = createApp(App);

const StubbedRoute = { template: '<div></div>' };

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: StubbedRoute },
    { path: '/public/data_load.html', name: 'about', component: StubbedRoute },
    { path: '/locations', name: 'locations', component: StubbedRoute },
    { path: '/blog', name: 'blog', component: StubbedRoute },
    { path: '/pricing', name: 'pricing', component: StubbedRoute },
    { path: '/pricing/pro', name: 'pricing-pro', component: StubbedRoute },
    { path: '/pricing/starter', name: 'pricing-starter', component: StubbedRoute },
    { path: '/contact', name: 'contact', component: StubbedRoute },
    { path: '/customer-service', name: 'customer-service', component: StubbedRoute },
    { path: '/accounting', name: 'accounting', component: StubbedRoute },
    { path: '/reception', name: 'reception', component: StubbedRoute },
    { path: '/signup', name: 'signup', component: StubbedRoute },
    { path: '/login', name: 'login', component: StubbedRoute },
  ],
});

app.use(router);

app.component('vue-navigation-bar', VueNavigationBar);

app.mount('#app');