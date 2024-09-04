<script setup>
import {ref} from 'vue';
import Negotiation from "@/components/Negotiation.vue";
import Survey from "@/components/Survey.vue";

import Button from "primevue/button";
import SelectButton from "primevue/selectbutton";
import Card from "primevue/card";

defineEmits(['show-info-dialog']);

const loading = ref(false);
const show_start_card = ref(true);
const survey = ref()
const tki_options = ref(['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']);
const judgment = ref();
const judgment_send = ref(false);
const disclosure = ref();

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
  negotiation_complete.value = true;
  judgment_send.value = false;
}

const send_judgment = () => {
  negotiation_component.value.send_judgment(judgment.value);
}

const restart_identification = () => {
  negotiation_complete.value = false;
  loading.value = true;
  negotiation_component.value.start("random", survey.value.data);
  judgment.value = null;
}

const handle_disclosure = (truth) => {
  console.log(truth)
  negotiation_component.value.close();
  negotiation_component.value.visible = false;
  judgment_send.value = true;
  disclosure.value = truth;
}

</script>

<template>
  <Card v-show="show_start_card">
    <template #title>Can you identify what TKI-style you negotiate with?</template>
    <template #content>
      <p>For the research, please enter some information about yourself:</p>
      <Survey ref="survey"/>
      <p>If this is your first negotiation, please check out the information <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> before you get started.</p>
    </template>
    <template #footer>
      <Button label="Start Negotiation" :loading="loading" @click="start_negotiation" :disabled="survey == null ? true : (Object.values(survey.data).includes(null) || Object.values(survey.data).includes(''))"/>
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
      <template #title>Conclusion</template>
      <template #content>
        <p v-if="disclosure === judgment">You identified the opponent model correctly as {{disclosure}}!</p>
        <p v-else>Your judgment of {{judgment}} was incorrect, you negotiated against the {{disclosure}} model.</p>
        <p style="margin-top: 1rem">Feel free to negotiate another round:</p>
      </template>
      <template #footer>
        <div class="button-row">
          <Button label="Restart" @click="restart_identification"/>
        </div>
      </template>
    </Card>
  </div>
  <Negotiation ref="negotiation_component" mode="identification"
               @negotiation-start="negotiation_start" @negotiation-end="negotiation_end" @disclosure="handle_disclosure"/>
</template>

<style scoped>

</style>