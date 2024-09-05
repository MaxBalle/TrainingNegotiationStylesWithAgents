<script setup>
import {computed, ref} from 'vue';

import UtilityInformation from "@/components/UtilityInformation.vue";

import Card from 'primevue/card';
import SelectButton from 'primevue/selectbutton';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import Knob from 'primevue/knob';

import { useToast } from "primevue/usetoast";
import Toast from 'primevue/toast';
const toast = useToast();

const props = defineProps(["mode"]);
const emit = defineEmits(['negotiation-start','negotiation-end','disclosure']);

const state = ref('init');
const loading = ref(false);

const url = "ws://localhost:8001/"
let websocket;

const issue_names = ref(['Price', 'Open at', 'Open for', 'Tables', 'Team size'])
const issue_options = ref([
  [{val: 0, label: '€'}, {val: 1, label: '€€'}, {val: 2, label: '€€€'}, {val: 3, label: '€€€€'}, {val: 4, label: '€€€€€'},],
  [{val: 0, label: '9:00'}, {val: 1, label: '9:30'}, {val: 2, label: '10:00'}, {val: 3, label: '10:30'}, {val: 4, label: '11:00'},],
  [{val: 0, label: '5h'}, {val: 1, label: '6h'}, {val: 2, label: '7h'}, {val: 3, label: '8h'}, {val: 4, label: '9h'},],
  [{val: 0, label: '8'}, {val: 1, label: '9'}, {val: 2, label: '10'}, {val: 3, label: '11'}, {val: 4, label: '12'},],
  [{val: 0, label: '2'}, {val: 1, label: '3'}, {val: 2, label: '4'}, {val: 3, label: '5'}, {val: 4, label: '6'},],
])

const issues = ref();
const calcUtility = (choices) => {
  if (typeof choices == 'undefined') {
    return 0;
  }
  let total = 0;
  for (let i = 0; i < choices.length; i++) {
    if (choices[i] != null) {
      total += issues.value[i][0] * issues.value[i][1][choices[i]];
    }
  }
  return total;
}

const timeout = ref()
const counter = ref()
let interval

const current_offer_choices = ref([null, null, null, null, null])
const current_offer_utility = computed(() => calcUtility(current_offer_choices.value))
const current_opponent_offer = ref()
const current_opponent_offer_utility = ref()
const offer_stack = ref([])
const conclusion = ref()

const visible = ref(false);

const utilityInformationComponent = ref();

const start = (model, survey_data) => {
  state.value = "init";
  loading.value = true;
  websocket = new WebSocket(url);
  websocket.onmessage = websocket_message_event_handler;
  websocket.onopen = () => {
    websocket.send(JSON.stringify({
      message_type: "init",
      mode: props.mode,
      model: model,
      personal_information: survey_data
    }));
  }
  websocket.onerror = (error) => {
    console.log(error)
    toast.add({severity: "error", summary: 'Websocket error', detail: 'Problem with the connection to server for hosting the negotiations and models', life: 3000 })
    loading.value = false;
  }
  counter.value = null;
};

const websocket_message_event_handler = (event) => {
  const message = JSON.parse(event.data);
  switch (message.message_type) {
    case "init":
      issues.value = message.issues;
      if (message.start) {
        loading.value = false;
        state.value = "writing_new_offer";
      }
      timeout.value = message.timeout;
      websocket.send(JSON.stringify({
        message_type: "init_ack"
      }))
      emit('negotiation-start');
      break;
    case "offer":
      current_opponent_offer.value = message.values;
      current_opponent_offer_utility.value = calcUtility(current_opponent_offer.value);
      loading.value = false;
      state.value = "viewing_opponent_offer";
      counter.value = timeout.value;
      if (timeout.value != null) {
        interval = setInterval(() => {
          counter.value--;
          if (counter.value === 0) {
            counter.value = null;
            conclude("self", "accept");
          }
        }, 1000);
      }
      break;
    case "end":
      loading.value = false;
      conclude("opponent", message.outcome)
      break;
    case "disclosure":
      emit('disclosure', message.opponent);
      break;
    case "error":
      console.log(message);
      toast.add({severity: "error", summary: 'Websocket error', detail: 'Server send error: '+message.error, life: 3000 });
      break;
  }
}

const send_offer = () => {
  clearInterval(interval);
  loading.value = true;
  websocket.send(JSON.stringify({
    message_type: "offer",
    values: current_offer_choices.value
  }));
  offer_stack.value.unshift({
    author: "self",
    values: current_offer_choices.value,
    utility: calcUtility(current_offer_choices.value)
  });
  current_offer_choices.value = [null, null, null, null, null];
}

const write_counteroffer = () => {
  offer_stack.value.unshift({
    author: "opponent",
    values: current_opponent_offer.value,
    utility: current_opponent_offer_utility.value
  });
  current_opponent_offer.value = null;
  current_opponent_offer_utility.value = null;
  state.value = "writing_new_offer";
}

const conclude = (author, outcome) => {
  clearInterval(interval);
  conclusion.value = {
    outcome: outcome,
    ending_party: author
  }
  if(author === "self") {
    offer_stack.value.unshift({
      author: "opponent",
      values: current_opponent_offer.value,
      utility: current_opponent_offer_utility.value
    });
    websocket.send(JSON.stringify({
      message_type: "end",
      outcome: outcome
    }));
  }
  state.value = "concluded";
  emit('negotiation-end');
}

const send_judgment = (judgment) => {
  websocket.send(JSON.stringify({
    message_type: "judgment",
    judgment: judgment
  }))
}

const close = () => {
  state.value = 'init';
  loading.value = false;
  issues.value = null;
  current_offer_choices.value = [null, null, null, null, null];
  current_opponent_offer.value = null;
  current_opponent_offer_utility.value = null;
  offer_stack.value = [];
  conclusion.value = null;
  websocket.close();
  utilityInformationComponent.value.showDetails = true;
}

defineExpose({
  start,
  visible,
  websocket,
  close,
  send_judgment
});

const float_to_percent_string = (val) => {return Math.round(val * 100) + '%'}

</script>

<template>
  <div v-if="visible">
    <Toast/>
    <UtilityInformation ref="utilityInformationComponent" :issues="issues" :issue_names="issue_names" :issue_options="issue_options"/>
    <Card v-if="loading" style="width: fit-content">
      <template #content>
        <ProgressSpinner/>
      </template>
    </Card>
    <div v-else>
      <Card v-if="state === 'viewing_opponent_offer'" style="width: fit-content">
        <template #title>
          <div>
            <p>Newest opponent offer</p>
            <Knob v-model="current_opponent_offer_utility" :max="1" readonly :size="50" :valueTemplate="float_to_percent_string" v-tooltip="'This offers utility to you'"/>
          </div>
        </template>
        <template #content>
          <div class="issue_row" v-for="(issue, index) in issues">
            <label v-tooltip.left="'Importance to you '+float_to_percent_string(issue[0])">{{issue_names[index]}}</label>
            <SelectButton v-model="current_opponent_offer[index]" :options="issue_options[index]" optionValue="val" optionLabel="label" :disabled="true"
                          v-tooltip="'Your preference for ' + issue_options[index][current_opponent_offer[index]].label + ' is ' + issue[1][current_opponent_offer[index]]"/>
          </div>
        </template>
        <template #footer>
          <div class="button-row">
            <Button label="Accept" @click="conclude('self', 'accept')"/>
            <Button label="Reject" @click="conclude('self','reject')"/>
            <Button label="Write Counteroffer" @click="write_counteroffer"/>
          </div>
          <div v-if="counter != null" style="display: flex; flex-direction: row; align-items: center; gap: 10px; margin-top: 10px">
            <label>Time left:</label>
            <Knob v-model="counter" :max="timeout" :size="50" v-tooltip="'You have to send your offer in this time or i will end automatically'"/>
          </div>
        </template>
      </Card>
      <Card v-if="state === 'writing_new_offer'" style="width: fit-content; margin-left: auto">
        <template #title>
          <div>
            <p>Write your offer</p>
            <Knob v-model="current_offer_utility" :max="1" readonly :size="50" :valueTemplate="float_to_percent_string" v-tooltip="'The total utility of the offer'"/>
          </div>
        </template>
        <template #content>
          <div class="issue_row" v-for="(issue, index) in issues">
            <label v-tooltip.left="'Importance to you '+float_to_percent_string(issue[0])">{{issue_names[index]}}</label>
            <SelectButton v-model="current_offer_choices[index]" :options="issue_options[index]" optionValue="val" optionLabel="label"/>
            <Knob v-model="issue[1][current_offer_choices[index]]" :max="1" readonly :size="50" :valueTemplate="float_to_percent_string" v-tooltip="'Your preference for the chosen value'"/>
          </div>
        </template>
        <template #footer>
          <div style="display: flex; flex-direction: row; align-items: center; gap: 20px">
            <Button label="Send offer" @click="send_offer" :disabled="current_offer_choices.some((oc) => oc == null) || current_offer_choices.length !== issues.length"/>
            <div v-if="counter != null" style="display: flex; flex-direction: row; align-items: center; gap: 10px">
              <label>Time left:</label>
              <Knob v-model="counter" :max="timeout" :size="50" v-tooltip="'You have to send your offer in this time or i will end automatically'"/>
            </div>
          </div>
        </template>
      </Card>
      <Card v-if="state === 'concluded'" :style="'width: fit-content'+[conclusion.ending_party === 'self' ? '; margin-left: auto' : '']">
        <template #title>Offer {{conclusion.outcome}}ed</template>
        <template #subtitle>Negotiation ended by {{conclusion.ending_party === 'self' ? 'yourself' : 'your opponent'}}</template>
      </Card>
    </div>
    <div>
      <Card :style="'width: fit-content'+[offer.author === 'self' ? '; margin-left: auto' : '']" v-for="(offer, index) in offer_stack">
        <template #title>
          <div>
            <p>Offer Nr. {{offer_stack.length - index}}</p>
            <Knob v-model="offer.utility" :max="1" readonly :size="50" :valueTemplate="float_to_percent_string"
                  v-tooltip="'This offers utility to you'"/>
          </div>
        </template>
        <template #subtitle>coming from {{offer.author === 'self' ? 'yourself' : 'your opponent'}}</template>
        <template #content>
          <div class="issue_row" v-for="(issue, index) in issues">
            <label v-tooltip.left="'Importance to you '+float_to_percent_string(issue[0])">{{issue_names[index]}}</label>
            <SelectButton v-model="offer.values[index]" :options="issue_options[index]" optionValue="val" optionLabel="label" :disabled="true"
                          v-tooltip="'Your preference for ' + issue_options[index][offer.values[index]].label + ' is ' + issue[1][offer.values[index]]"/>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>

.issue_row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.issue_row label {
  flex-grow: 1;
}

.p-card-title div {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: end;
}

.p-card-title p {
  font-weight: var(--p-card-title-font-weight);
}

</style>