<script setup>
import { ref } from 'vue';
import Negotiation from "@/components/Negotiation.vue";

import Button from "primevue/button";
import SelectButton from "primevue/selectbutton";
import Card from "primevue/card";

defineEmits(['show-info-dialog']);

const loading = ref(false);
const choosing_model = ref(true);
const model = ref();
const tki_options = ref(['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']);

const negotiation_component = ref();

const negotiation_complete = ref(false);
const start_negotiation = () => {
  loading.value = true;
  negotiation_component.value.start(model.value);
}
const negotiation_start = () => {
  negotiation_component.value.visible = true;
  choosing_model.value = false;
  loading.value = false;
}
const negotiation_end = () => {
  negotiation_complete.value = true;
}

const restart_negotiation = () => {
  negotiation_complete.value = false;
  loading.value = true;
  negotiation_component.value.close();
  negotiation_component.value.start(model.value);
}

const choose_new_model = () => {
  choosing_model.value = true;
  negotiation_complete.value = false;
  negotiation_component.value.close();
  negotiation_component.value.visible = false;
}

</script>

<template>
  <Card v-if="choosing_model">
    <template #title>Choose the TKI-style of your opponent</template>
    <template #content>
      <SelectButton v-model="model" :options="tki_options" aria-labelledby="basic" />
    </template>
    <template #footer>
      <Button label="Start Negotiation" :loading="loading" @click="start_negotiation" :disabled="model == null"/>
    </template>
  </Card>
  <Card v-if="negotiation_complete">
    <template #title>Options</template>
    <template #footer>
      <div class="button-row">
        <Button label="Restart" @click="restart_negotiation"/>
        <Button label="Choose Model" @click="choose_new_model"/>
      </div>
    </template>
  </Card>
  <Negotiation ref="negotiation_component" mode="sandbox" @negotiation-start="negotiation_start" @negotiation-end="negotiation_end"/>
</template>

<style scoped>

.p-selectbutton {
  flex-wrap: wrap;
}

</style>