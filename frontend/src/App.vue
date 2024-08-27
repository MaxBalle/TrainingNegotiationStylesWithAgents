<script setup>
import { RouterLink, RouterView } from 'vue-router'
import {ref} from "vue";
import Menubar from 'primevue/menubar';

const menu_items = ref([
  {
    label: 'Home',
    icon: 'pi pi-home',
    route: '/'
  },{
    label: 'Sandbox',
    icon: 'pi pi-home',
    route: '/sandbox'
  },{
    label: 'Categorization',
    icon: 'pi pi-home',
    route: '/categorization'
  },{
    label: 'Turing',
    icon: 'pi pi-home',
    route: '/turing'
  },
]);
</script>

<template>
  <header>
    <Menubar :model="menu_items">
      <template #item="{ item, props, hasSubmenu }">
        <RouterLink :to="item.route" class="p-menubar-item-link">
          <span :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
        </RouterLink>
      </template>
    </Menubar>
  </header>

  <RouterView />
</template>

<style scoped>
/*
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}*/

@media (min-width: 1024px) {
  /*
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }*/
}
</style>
