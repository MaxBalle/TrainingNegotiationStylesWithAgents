<script setup>
import {ref} from 'vue';

import Card from "primevue/card";
import Button from "primevue/button";

const props = defineProps(["mode", "questions_ref", "person_data", "person_code"]);

const url = "wss://trainingnegotiationstyleswithagents-ws.onrender.com"

const questioning = ref(true);

let websocket;
const send_questionnaire = () => {
  questioning.value = false;
  websocket = new WebSocket(url);
  websocket.onopen = () => {
    websocket.send(JSON.stringify({
      message_type: "questionnaire",
      mode: props.mode,
      person_code: props.person_code,
      personal_information: props.person_data,
      questions: props.questions_ref
    }));
    websocket.close();
  }
}

</script>

<template>
  <Card v-if="questioning">
    <template #title>Questionnaire</template>
    <template #subtitle>
      <slot name="subtitle"></slot>
    </template>
    <template #content>
      <slot name="questions"></slot>
    </template>
    <template #footer>
      <Button label="Send" :disabled="Object.values(questions_ref).includes(null)" @click="send_questionnaire"/>
    </template>
  </Card>
  <Card v-else>
    <template #title>Thank you very much!</template>
    <template #content>
      <slot name="thanks"></slot>
    </template>
  </Card>
</template>

<style scoped>

</style>
