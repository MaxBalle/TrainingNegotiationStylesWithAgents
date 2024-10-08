<script setup>

import Accordion from 'primevue/accordion';
import AccordionPanel from 'primevue/accordionpanel';
import AccordionHeader from 'primevue/accordionheader';
import AccordionContent from 'primevue/accordioncontent';

import Image from 'primevue/image';

</script>

<template>

  <Accordion>
    <AccordionPanel value="0">
      <AccordionHeader>Negotiation</AccordionHeader>
      <AccordionContent>
        <div class="paragraph-group">
          <p class="m-0">
            Negotiations are joint effort using communication and decision-making to overcome a shared problem.
            They often are structured as an exchange of offers and end with one party accepting or rejecting the last offer.
          </p>
          <p class="m-0">
            Negotiations are integrative when both parties work towards a win-win situation by creating value together. This can be described as expanding the pie while in distributive negotiations
            the pie only gets divided and ones win is the others loss.
          </p>
          <p class="m-0">
            The negotiations used here are multi-issue negotiations, meaning there are multiple issues to solve.
            For each issue, there are different options to choose from. Every negotiation on this page has five issues with each five options.
            Every offer must specify an option for each issue, there are no partial offers!
          </p>
        </div>
      </AccordionContent>
    </AccordionPanel>
    <AccordionPanel value="1">
      <AccordionHeader>Utility</AccordionHeader>
      <AccordionContent>
        <div class="paragraph-group">
          <p class="m-0">
            Issues are usually different in how important they are to you. This is measured with the importance of an issue.
            The importances of all issues add together to 1. Your opponent probably views the importance of issues different than you,
            opening the possibility for integrative negotiation.
          </p>
          <p class="m-0">
            The different options for an issue differ in how much they fulfill your goals for that issue. To caption this,
            each option has a preference value. For each issue, there is at least one option that totally makes you happy and
            therefore has a preference of 1. The remaining options have values smaller than 1 and can even be 0. In these cases
            your goals for this issue are met partially or not at all. Keep in mind that your opponent most likely prefers different options than you!
          </p>
          <p class="m-0">
            The utility of one option is defined as the product of the importance of the issue and the preference for the option.
            As each offer combines one option for each issue, the total utility of this offer is the sum of the utilities of the chosen options.
            The best possible offer by your point of view has a total utility of 1 but probably is not as good from the perspective of your opponent!
          </p>
          <p class="m-0">
            During the negotiation, when its your turn to write your offer, there are indicators next to each issue displaying your preference for the chosen option.
            On the top of each offer (by you or your opponent) an indicator shows the total utility of that offer to you.
          </p>
        </div>
      </AccordionContent>
    </AccordionPanel>
    <AccordionPanel value="2">
      <AccordionHeader>Thomas-Kilmann Instrument</AccordionHeader>
      <AccordionContent>
        <p class="m-0" style="margin-bottom: 10px">
          The Thomas-Kilamnn Conflict Mode Instrument or TKI is a tool to look at the different approaches humans take with conflict situations.
          They can be described with two dimensions, assertiveness and cooperativeness. Assertiveness is how much one aims to satisfy the own concerns,
          cooperativeness is how much the satisfaction of the opponents concern matters.
        </p>
        <div id="tki-graphic">
          <Image src="/tki.png" alt="TKI Graphic" width="75%"/>
          <a href="https://kilmanndiagnostics.com/wp-content/uploads/2018/03/TKI_Sample_Report.pdf" target="_blank">Source</a>
        </div>
        <p class="m-0" style="margin-top: 10px">
          The different conflict modes can be applied to the behaviour of humans in negotiations.
          While no one is bound to always act in one mode, in single negotiations one mode often dominates.
          In the next panel, the different negotiation styles that match the conflict modes are described.
        </p>
      </AccordionContent>
    </AccordionPanel>
    <AccordionPanel value="3">
      <AccordionHeader>Negotiation styles</AccordionHeader>
      <AccordionContent>
        <div class="paragraph-group">
          <p class="m-0">
            <b>Accommodating</b> negotiators want you to reach your goals, even if that means they have to sacrifice parts of their own
            utility. They tend to be generous and flexible to accommodate your wishes.
          </p>
          <p class="m-0">
            <b>Collaborating</b> negotiators try to work with you in order to find the best solution for both parties. They want to explore
            multiple possible options and learn about you to try and satisfy their and your goals.
          </p>
          <p class="m-0">
            <b>Compromising</b> negotiators are moderate in both regards. They want to find a solution, but it does not have to be the
            optimal one, just partially satisfactory to both. They work with you to some degree but do not want to go too deep into it.
            It is common for them to strive for quick solutions by exchanging concessions.
          </p>
          <p class="m-0">
            <b>Avoiding</b> negotiators do not want to negotiate at all, they want to avoid the conflict. They also care little about
            your or even their own goals. Therefore they tend to flee the negotiations by concluding early.
          </p>
          <p class="m-0">
            <b>Competing</b> negotiators are assertive and uncooperative. They want to achieve as much as possible for themselves and
            do not care about you reaching your goals at all. Competing negotiators want to win, not reach a fair outcome!
          </p>
        </div>
      </AccordionContent>
    </AccordionPanel>
  </Accordion>

</template>

<style scoped>

#tki-graphic {
  text-align: center;
}

#tki-graphic a {
  text-decoration: none;
  color: var(--p-text-color);
}

@media (prefers-color-scheme: dark) {
  #tki-graphic span {
    filter: invert(100%);
  }
}

b {
  font-weight: bolder;
  color: var(--p-primary-color);
}

</style>