import '@mantine/core/styles.css'
import './App.css'

import { MantineProvider } from '@mantine/core'
import { Header } from './components/Header'

function App() {
  return (<MantineProvider>
    <div className="App">
      <Header />
    </div>
  </MantineProvider>)
}

export default App
