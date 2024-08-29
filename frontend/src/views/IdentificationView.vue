<script setup>
import { ref } from 'vue';
import Negotiation from "@/components/Negotiation.vue";

import Button from "primevue/button";
import SelectButton from "primevue/selectbutton";
import Card from "primevue/card";

defineEmits(['show-info-dialog']);

const loading = ref(false);
const show_start_card = ref(true);
const tki_options = ref(['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']);
const judgment = ref();
const judgment_send = ref(false);

const negotiation_component = ref();

const negotiation_complete = ref(false);

const start_negotiation = () => {
  loading.value = true;
  negotiation_component.value.start("random");
}

const negotiation_start = () => {
  negotiation_component.value.visible = true;
  show_start_card.value = false;
  loading.value = false;
}

const negotiation_end = () => {
  negotiation_complete.value = true;
}

const send_judgment = () => {
  negotiation_component.value.send_judgment(judgment.value);
  negotiation_component.value.close();
  negotiation_component.value.visible = false;
  judgment_send.value = true;
}

const restart_identification = () => {
  negotiation_complete.value = false;
  loading.value = true;
  negotiation_component.value.start("random");
}

</script>

<template>
  <Card v-if="show_start_card">
    <template #title>Can you identify what TKI-style you negotiate with?</template>
    <template #content>
      <p>For the research, please enter some information about yourself:</p>
      <p>If this is your first negotiation, please check out the information <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> before you get started.</p>
    </template>
    <template #footer>
      <Button label="Start Negotiation" :loading="loading" @click="start_negotiation"/>
    </template>
  </Card>
  <div v-if="negotiation_complete">
    <Card v-if="!judgment_send">
      <template #title>Judgment</template>
      <template #content>
        <p>What do you think was the TKI of you opponent?</p>
        <SelectButton v-model="judgment" :options="tki_options" aria-labelledby="basic" :allow-empty="false"/>
      </template>
      <template #footer>
        <Button label="Send" @click="send_judgment" :disabled="judgment == null"/>
      </template>
    </Card>
    <Card v-else>
      <template #title>Options</template>
      <template #footer>
        <div class="button-row">
          <Button label="Restart" @click="restart_identification"/>
        </div>
      </template>
    </Card>
  </div>
  <Negotiation ref="negotiation_component" mode="identification" @negotiation-start="negotiation_start" @negotiation-end="negotiation_end"/>
</template>

<style scoped>

</style>