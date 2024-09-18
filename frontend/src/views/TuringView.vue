<script setup>
import {nextTick, ref} from 'vue';
import Negotiation from "@/components/Negotiation.vue";
import Questionnaire from "@/components/Questionnaire.vue";
import Likert from "@/components/Likert.vue";

import Button from "primevue/button";
import SelectButton from "primevue/selectbutton";
import Card from "primevue/card";
import PersonalInformation from "@/components/PersonalInformation.vue";
import ProgressSpinner from "primevue/progressspinner";
import Step from "primevue/step";
import StepList from "primevue/steplist";
import Stepper from "primevue/stepper";

defineEmits(['show-info-dialog']);

const loading = ref(false);
const show_start_card = ref(true);
const personal_information = ref();
const judgement = ref();
const judgement_visible = ref(true);
const show_questionnaire = ref(false);

const negotiation_component = ref();

const negotiation_complete = ref(false);

const stepper_value = ref("1");

const questionnaire_questions = ref({
  certain_of_judgement: null,
  outside_influence: null,
});

const person_code = ref("pc" + Math.random().toString(16).slice(2));

const start_negotiation = () => {
  loading.value = true;
  negotiation_component.value.start("random", personal_information.value.data, person_code.value);
}

const negotiation_start = () => {
  negotiation_component.value.visible = true;
  show_start_card.value = false;
  loading.value = false;
  stepper_value.value = "2"
}

const negotiation_end = () => {
  judgement_visible.value = true;
  negotiation_complete.value = true;
  nextTick(() => {
    document.getElementById("judgement-card").scrollIntoView({ behavior: 'smooth', block: 'nearest'});
  })
}

const send_judgement = () => {
  negotiation_component.value.send_judgement(judgement.value);
}

const restart_turing = () => {
  negotiation_complete.value = false;
  loading.value = true;
  negotiation_component.value.start("random", personal_information.value.data, person_code.value);
  judgement.value = null;
}

const handle_disclosure = (truth) => {
  negotiation_component.value.close();
  negotiation_component.value.visible = false;
  judgement_visible.value = false;
}

const start_questionnaire = () => {
  negotiation_complete.value = false;
  show_questionnaire.value = true;
  stepper_value.value = "3"
}

</script>

<template>
  <Stepper :value="stepper_value" linear>
    <Card>
      <template #title>Turing-Test</template>
      <template #subtitle>Find out if you are able to tell the difference between negotiating a person or an AI-model!</template>
      <template #content>
        <StepList>
          <Step value="1">Personal Information</Step>
          <Step value="2">Identification</Step>
          <Step value="3">Questionnaire</Step>
        </StepList>
      </template>
    </Card>
  </Stepper>
  <Card v-show="show_start_card">
    <template #content>
      <p>For the research, please enter some information about yourself first:</p>
      <PersonalInformation ref="personal_information"/>
      <div class="paragraph-group">
        <p>If this is your first negotiation, please read the information <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> before you get started.</p>
        <p>This test works in pairs of two: You either negotiate against the other party or against the AI. Then you can guess what the opponent was.</p>
        <p>If there are any other persons participating in the Turing-Test in your proximity, please do your best to reveal no information that could help them determine if they are negotiating against you.</p>
        <p>This negotiation mode requires you to respond to offers within 100 seconds to ensure comparable behaviour to a model. The timer starts when you receive an offer.
          If your time runs out, you automatically accept the last offer from your opponent!</p>
        <p>You may have to wait until someone else joins the test.</p>
      </div>
    </template>
    <template #footer>
      <Button label="Start Negotiation" :loading="loading" @click="start_negotiation" :disabled="personal_information == null ? true : (Object.values(personal_information.data).includes(null) || Object.values(personal_information.data).includes(''))"/>
    </template>
  </Card>
  <div v-if="negotiation_complete">
    <Card v-if="judgement_visible" id="judgement-card">
      <template #title>judgement</template>
      <template #content>
        <div class="paragraph-group">
          <p>What kind of negotiation partner do you think was on the other end?</p>
          <p>Please choose carefully, this is the most important step for the research!</p>
        </div>
        <SelectButton v-model="judgement" :options="['Person', 'AI']" aria-labelledby="basic" :allow-empty="false" style="margin-top: 1rem"/>
      </template>
      <template #footer>
        <Button label="Send" @click="send_judgement" :disabled="judgement == null"/>
      </template>
    </Card>
    <Card v-else>
      <template #title>Options</template>
      <template #content>
        <p>Feel free to go another round or complete the survey by answering some questions:</p>
      </template>
      <template #footer>
        <div class="button-row">
          <Button label="Restart Turing-Test" @click="restart_turing"/>
          <Button label="Questionnaire" @click="start_questionnaire"/>
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
  <Questionnaire v-if="show_questionnaire" mode="turing" :questions_ref="questionnaire_questions" :person_data="personal_information.data" :person_code="person_code">
    <template #subtitle>Please enter how strongly you agree with the following statements</template>
    <template #questions>
      <p>I am certain of the judgements I made.</p>
      <Likert @choice="(c) => questionnaire_questions.certain_of_judgement = c"/>
      <p>My judgement was influenced by outside information. (E.g. by observing other parties performing the turing test)</p>
      <Likert @choice="(c) => questionnaire_questions.outside_influence = c"/>
    </template>
    <template #thanks>
      <div class="paragraph-group">
        <p>You have successfully completed the Turing-Test survey!</p>
        <p>If you haven't already, you can check out the Identification-Game. There you can find out if you can identify the different negotiation styles of the AI models!</p>
      </div>
    </template>
  </Questionnaire>
</template>

<style scoped>

</style>