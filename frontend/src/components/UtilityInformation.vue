<script setup>
import Card from 'primevue/card';
import {ref} from "vue";

const props = defineProps(["issues"]);

const showDetails = ref(true);

defineExpose({showDetails});

</script>

<template>

  <Card>
    <template #title>
      <i class="pi pi-chevron-down" style="cursor: pointer" @click="() => {showDetails = false}" v-if="showDetails"/>
      <i class="pi pi-chevron-up" style="cursor: pointer" @click="() => {showDetails = true}" v-else/>
      Utility information
    </template>
    <template #content v-if="showDetails">
      <div>
        <Card v-for="(issue, index) in props.issues" style="width: fit-content">
          <template #title>Issue {{index}}</template>
          <template #content>
            <p>Importance: {{issue[0]}}</p>
            <p>Preferences:<br/>{{issue[1]}}</p>
          </template>
        </Card>
      </div>
    </template>
  </Card>

</template>

<style scoped>

.p-card-content > div {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 10px;
}

</style>