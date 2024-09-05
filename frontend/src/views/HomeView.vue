<script setup>

import Card from "primevue/card";

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
          <p>Here you can sharpen your negotiation skills with five different AI-Models. Each aims to imitate the negotiation style of a different conflict style as described by the Thomas-Kilmann Conflict Mode Instrument (TKI).</p>
          <p>To learn more about the negotiations used here and the TKI styles, you can always click <i class="pi pi-info-circle" style="cursor: pointer" @click="$emit('show-info-dialog')"/> in the menubar.</p>
          <p>The models are based on recurrent neural networks and are trained using a simulation-based genetic algorithm.</p>
          <p>Try out different models in the sandbox or participate in the survey by performing an identification or a Turing-Test!</p>
        </div>

      </template>
    </Card>

  </main>
</template>

<style scoped>

</style>