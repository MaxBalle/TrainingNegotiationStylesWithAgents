<script setup>
import { RouterLink, RouterView } from 'vue-router'
import {ref} from "vue";
import Menubar from 'primevue/menubar';
import Dialog from 'primevue/dialog';

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

const dialog_visible = ref(false);

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
      <template #end>
        <i class="pi pi-info-circle menubar_clickable_icon" @click="dialog_visible = true"/>
      </template>
    </Menubar>
  </header>
  <Dialog v-model:visible="dialog_visible" modal dismissableMask header="Negotiation Information" :style="{ width: '25rem' }">
    <p>Explanatory text here.</p>
  </Dialog>
  <RouterView
      @show-info-dialog="dialog_visible = true"
  />
</template>

<style scoped>
.menubar_clickable_icon {
  margin-right: 1rem;
  cursor: pointer;
}
</style>
