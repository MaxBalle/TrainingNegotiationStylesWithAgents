<script setup>
import { ref } from 'vue';
import Negotiation from "@/components/Negotiation.vue";

import Button from "primevue/button";
import SelectButton from "primevue/selectbutton";
import Card from "primevue/card";
import Survey from "@/components/Survey.vue";
import ProgressSpinner from "primevue/progressspinner";

defineEmits(['show-info-dialog']);

const loading = ref(false);
const show_start_card = ref(true);
const survey = ref();
const judgment = ref();
const judgment_visible = ref(true);

const negotiation_component = ref();

const negotiation_complete = ref(false);

const start_negotiation = () => {
  loading.value = true;
  negotiation_component.value.start("random", survey.value.data);
}

const negotiation_start = () => {
  negotiation_component.value.visible = true;
  show_start_card.value = false;
  loading.value = false;
}

const negotiation_end = () => {
  judgment_visible.value = true;
  negotiation_complete.value = true;
}

const send_judgment = () => {
  negotiation_component.value.send_judgment(judgment.value);
}

const restart_turing = () => {
  negotiation_complete.value = false;
  loading.value = true;
  negotiation_component.value.start("random", survey.value.data);
  judgment.value = null;
}

const handle_disclosure = (truth) => {
  negotiation_component.value.close();
  negotiation_component.value.visible = false;
  judgment_visible.value = false;
}

</script>

<template>
  <Card v-show="show_start_card">
    <template #title>Turing-Test</template>
    <template #subtitle>Can you tell if you negotiate against a person or an AI-model?</template>
    <template #content>
      <p>For the research, please enter some information about yourself:</p>
      <Survey ref="survey"/>
      <p>If this is your first negotiation, please check out the information <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> before you get started.</p>
      <p>You may have to wait until someone else joins the Test</p>
    </template>
    <template #footer>
      <Button label="Start Negotiation" :loading="loading" @click="start_negotiation" :disabled="survey == null ? true : (Object.values(survey.data).includes(null) || Object.values(survey.data).includes(''))"/>
    </template>
  </Card>
  <div v-if="negotiation_complete">
    <Card v-if="judgment_visible">
      <template #title>Judgment</template>
      <template #content>
        <div class="paragraph-group">
          <p>What kind of negotiation partner do you think was on the other end?</p>
          <p>Please choose carefully, this is the most important step for the research!</p>
        </div>
        <SelectButton v-model="judgment" :options="['Person', 'AI']" aria-labelledby="basic" :allow-empty="false" style="margin-top: 1rem"/>
      </template>
      <template #footer>
        <Button label="Send" @click="send_judgment" :disabled="judgment == null"/>
      </template>
    </Card>
    <Card v-else>
      <template #title>Options</template>
      <template #footer>
        <div class="button-row">
          <Button label="Restart" @click="restart_turing"/>
        </div>
      </template>
    </Card>
  </div>
  <Card v-if="loading && !show_start_card && !negotiation_complete" style="width: fit-content">
    <template #content>
      <ProgressSpinner/>
    </template>
  </Card>
  <Negotiation ref="negotiation_component" mode="turing"
               @negotiation-start="negotiation_start" @negotiation-end="negotiation_end" @disclosure="handle_disclosure"/>
</template>

<style scoped>

</style>