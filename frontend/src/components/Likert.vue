<script setup>

import {ref} from "vue";

const val = ref();

const options = ref(["Strongly disagree","Disagree","Somewhat disagree","Neutral","Somewhat agree","Agree","Strongly agree"])

import RadioButton from 'primevue/radiobutton';

const emit = defineEmits(['choice']);

</script>

<template>
  <div style="display: flex; flex-direction: column; flex-wrap: wrap; gap: 0.25rem; margin: 0.25rem 0 1rem 0">
    <div v-for="(option, index) in options">
      <RadioButton v-model="val" :inputId="'likert'+index" :value="option" @change="$emit('choice', val)"/>
      <label :for="'likert'+index">{{option}}</label>
    </div>
  </div>
</template>

<style scoped>
.p-radiobutton {
  margin-right: 0.5rem;
}
</style>