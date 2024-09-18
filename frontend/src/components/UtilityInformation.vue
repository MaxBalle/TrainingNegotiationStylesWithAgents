<script setup>
import Card from 'primevue/card';
import {ref} from "vue";

const props = defineProps(["issues", "issue_names", "issue_options"]);

const showDetails = ref(true);

defineExpose({showDetails});

const float_to_percent_string = (val) => {return Math.round(val * 100) + '%'}

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
          <template #title>Issue: {{props.issue_names[index]}}</template>
          <template #content>
            <p>Importance: <b>{{float_to_percent_string(issue[0])}}</b></p>
            <p>Preferences:</p>
            <div v-for="(option, option_index) in issue[1]" style="display: flex; flex-direction: row; justify-content: space-between">
              <p>{{issue_options[index][option_index].label}}:</p>
              <p>{{float_to_percent_string(option)}}</p>
            </div>
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
  justify-content: space-between;
}

b {
  font-weight: bolder;
  color: var(--p-primary-color);
}

</style>