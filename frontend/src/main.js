import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import Tooltip from 'primevue/tooltip';
import ToastService from 'primevue/toastservice';

const app = createApp(App)

app.use(router);

app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
});

app.directive('tooltip', Tooltip);

app.use(ToastService);

app.mount('#app')
