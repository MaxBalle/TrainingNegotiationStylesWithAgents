<script setup>

import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Select from 'primevue/select';
import {computed, ref} from "vue";

const data = ref({
  name: null,
  age: null,
  gender: null,
  highest_education: null,
  negotiation_experience: null
})

const isComplete = () => {
  for (let field in data.value) {
    if (field == null) return false;
  }
  return true;
}

const complete = computed(isComplete);

defineExpose({
  data,
  complete
});

</script>

<template>
  <div class="form">
    <InputText id="name" v-model="data.name" placeholder="Name"/>
    <InputNumber v-model="data.age" :min="0" :max="150" placeholder="Age" :inputStyle="{width: '75px'}"/>
    <Select v-model="data.gender" :options="['Man','Woman','Other']" placeholder="Gender" class="w-full md:w-56" />
    <Select v-model="data.highest_education" :options="['Abitur','Bachelor','Master','Higher']" placeholder="Highest education" class="w-full md:w-56" />
    <Select v-model="data.negotiation_experience" :options="['No experience','Some experience','Highly experienced']" placeholder="Negotiation experience" class="w-full md:w-56" />
  </div>
</template>

<style scoped>

.form {
  display: flex;
  flex-direction: row;
  gap: 10px;
  margin: 10px 0;
}

</style>