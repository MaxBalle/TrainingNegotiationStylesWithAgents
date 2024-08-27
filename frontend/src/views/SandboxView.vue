<script setup>
import Card from 'primevue/card';
import SelectButton from 'primevue/selectbutton';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import { ref } from 'vue';

const model = ref('collaborating');
const options = ref(['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']);

const state = ref('choosing_model');
const loading = ref(false);

const url = "ws://localhost:8001/"
let websocket;

const issue_options = ref([
  {val: 0, label: 'A'},
  {val: 1, label: 'B'},
  {val: 2, label: 'C'},
  {val: 3, label: 'D'},
  {val: 4, label: 'E'},
])

const issues = ref();
const current_offer_choices = ref([null, null, null, null, null])
const current_opponent_offer = ref()
const offer_stack = ref([])
const conclusion = ref()

const websocket_message_event_handler = (event) => {
  const message = JSON.parse(event.data)
  switch (message.message_type) {
    case "perspective":
      issues.value = message.issues;
      loading.value = false;
      state.value = 'writing_new_offer';
      break;
    case "offer":
      current_opponent_offer.value = message.values
      loading.value = false;
      state.value = 'viewing_opponent_offer';
      break;
    case "accept":
      loading.value = false;
      state.value = 'concluded';
      conclusion.value = 'accepted_by_opponent'
      websocket.close()
      break;
    case "reject":
      loading.value = false;
      state.value = 'concluded';
      conclusion.value = 'rejected_by_opponent'
      websocket.close()
      break;
  }
}

const start_negotiation = () => {
  loading.value = true;
  websocket = new WebSocket(url);
  websocket.onmessage = websocket_message_event_handler;
  websocket.onopen = () => {
    websocket.send(model.value);
  }
};

const send_offer = () => {
  loading.value = true;
  websocket.send(JSON.stringify({
    type: "offer",
    values: current_offer_choices.value
  }));
  offer_stack.value.unshift({
    author: "self",
    values: current_offer_choices.value
  });
  current_offer_choices.value = [null, null, null, null, null]
}

const write_counteroffer = () => {
  offer_stack.value.unshift({
    author: "opponent",
    values: current_opponent_offer.value
  });
  current_opponent_offer.value = null;
  state.value = 'writing_new_offer'
}

const accept = () => {
  websocket.send(JSON.stringify({type: 'accept'}))
  state.value = 'concluded'
  conclusion.value = 'accepted_by_self'
  websocket.close()
}

const reject = () => {
  websocket.send(JSON.stringify({type: 'reject'}))
  state.value = 'concluded'
  conclusion.value = 'rejected_by_self'
  websocket.close()
}

const clean = () => {
  issues.value = null;
  current_offer_choices.value = [null, null, null, null, null];
  current_opponent_offer.value = null;
  offer_stack.value = [];
  conclusion.value = null;
}
const restart = () => {
  clean();
  state.value = 'negotiating';
  start_negotiation();
}

const new_model = () => {
  clean();
  state.value = 'choosing_model';
}

</script>

<template>
  <div class="sandbox">
    <Card id="choose_model_card" v-if="state === 'choosing_model'">
      <template #title>Choose the TKI-style of your opponent</template>
      <template #content>
        <SelectButton v-model="model" :options="options" aria-labelledby="basic"/>
      </template>
      <template #footer>
        <Button label="Start Negotiation" :loading="loading" @click="start_negotiation"/>
      </template>
    </Card>
    <div v-else>
      <Card>
        <template #title>Utility information</template>
        <template #content>
          {{issues}}
        </template>
      </Card>
      <Card v-if="loading">
        <template #content>
          <ProgressSpinner/>
        </template>
      </Card>
      <div v-else>
        <Card v-if="state === 'viewing_opponent_offer'">
          <template #title>Newest opponent offer</template>
          <template #content>
            Offer: {{current_opponent_offer}}
          </template>
          <template #footer>
            <Button label="Accept" @click="accept"/>
            <Button label="Reject" @click="reject"/>
            <Button label="Write Counteroffer" @click="write_counteroffer"/>
          </template>
        </Card>
        <Card v-if="state === 'writing_new_offer'">
          <template #title>Write your offer</template>
          <template #content>
            <div v-for="(issue, index) in issues">
              <p>Issue {{index}} with importance {{issue[0]}}</p>
              <SelectButton v-model="current_offer_choices[index]" :options="issue_options" optionValue="val" optionLabel="label"/>
            </div>
          </template>
          <template #footer>
            <Button label="Send offer" @click="send_offer"/>
          </template>
        </Card>
        <Card v-if="state === 'concluded'">
          <template #title>Negotiation concluded</template>
          <template #content>End: {{conclusion}}</template>
          <template #footer>
            <Button label="Restart" @click="restart"/>
            <Button label="New model" @click="new_model"/>
          </template>
        </Card>
      </div>
      <div>
        <Card v-for="(offer, index) in offer_stack">
          <template #title>Offer Nr. {{offer_stack.length - index}} (Author: {{offer.author}})</template>
          <template #content>
            {{offer.values}}
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>