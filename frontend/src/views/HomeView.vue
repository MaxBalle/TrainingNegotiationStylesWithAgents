<script setup>

import Card from "primevue/card";
import Divider from 'primevue/divider';


defineEmits(['show-info-dialog']);

</script>

<template>
  <main>
    <Card>
      <template #title>Training Negotiation Styles with Agents - An AI-based approach</template>
      <template #subtitle>A bachelor thesis by Max Balle</template>
      <template #content>
        <div class="paragraph-group">
          <p>Welcome to this training platform for negotiation styles!</p>
          <p>Here you can sharpen your negotiation skills with five different AI-Models. Each model aims to imitate the negotiation style of a different conflict style as described by the Thomas-Kilmann Conflict Mode Instrument (TKI).</p>
          <p>The setting: You and your partner (opponent) want to open a café together but need to agree on the price range, size and hours before you start.</p>
          <p>To learn more about the negotiations used here and the TKI styles, you can always click <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> in the menubar.</p>
          <p>The models are based on recurrent neural networks and are trained using a simulation-based genetic algorithm.</p>
          <Divider/>
          <p>If you want to test out the different models you can choose Sandbox from the menu.</p>
          <p>If you are here for the survey, please read the information <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> carefully and then choose Identification or Turing from the menu.</p>
        </div>
      </template>
    </Card>

  </main>
</template>

<style scoped>

</style>