import '@mantine/core/styles.css'
import './App.css'

import { AppShell, Container, Grid, MantineProvider, MantineColorsTuple, createTheme } from '@mantine/core'
import { Header } from './components/Header'
import { InterfaceStatusGrid } from './components/InterfaceStatusGrid'
import { Chat } from './components/Chat';


const myColor: MantineColorsTuple =
[
  "#f3f4f7",
  "#e4e5e6",
  "#c7c8ce",
  "#a7aab7",
  "#8b90a3",
  "#7a7f97",
  "#717792",
  "#60657f",
  "#545a72",
  "#474d66"
];

const theme = createTheme({
  colors: {
    myColor,
  }
});

function App() {
  return (<MantineProvider theme={theme}>
      <AppShell
        header={{ height: 60 }}
        navbar={{
          width: 300,
          breakpoint: 'sm',
          collapsed: {
            mobile: true,
            desktop: true
          }
        }}
        aside={{
          width: 300,
          breakpoint: 'xs'
        }}
        padding="md"
      >
        <Header />
        <InterfaceStatusGrid />
        <Chat />
      </AppShell>
  </MantineProvider>);
}

export default App
