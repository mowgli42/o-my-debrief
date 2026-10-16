import { mount } from 'svelte'
// Leaflet first so app.css overrides (dark .leaflet-container) win by source order.
import 'leaflet/dist/leaflet.css'
import './app.css'
import App from './App.svelte'

const app = mount(App, { target: document.getElementById('app') })
export default app
