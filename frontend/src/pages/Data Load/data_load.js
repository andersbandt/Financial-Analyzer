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
  ],
});

app.use(router);

app.component('vue-navigation-bar', VueNavigationBar);

app.mount('#app');