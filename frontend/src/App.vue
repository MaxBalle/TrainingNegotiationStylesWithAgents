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
    icon: 'pi pi-comments',
    route: '/sandbox'
  },{
    label: 'Identification',
    icon: 'pi pi-clipboard',
    route: '/identification'
  },{
    label: 'Turing',
    icon: 'pi pi-clipboard',
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

</style>
