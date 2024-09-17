<script setup>

import Select from 'primevue/select';
import {computed, ref} from "vue";

const data = ref({
  age_group: null,
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
    <Select v-model="data.age_group" :options="['< 18','18-24','25-34','35-44','45-54','55-64','> 64']" placeholder="Age" />
    <Select v-model="data.gender" :options="['Man','Woman','Other']" placeholder="Gender" class="w-full md:w-56" />
    <Select v-model="data.highest_education" :options="['Secondary education','Upper secondary education (e.g. Abitur)','Bachelor or equivalent','Master or equivalent','Higher']"
            placeholder="Highest education" class="w-full md:w-56"/>
    <Select v-model="data.negotiation_experience" :options="['No experience','Some experience','Experienced','Highly experienced']" placeholder="Negotiation experience" class="w-full md:w-56" />
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