import { Text, AppShell, Stack, ScrollArea } from '@mantine/core';
import { useEffect, useState } from 'react';
import { InterfaceStatus, InterfaceStatusType } from './InterfaceStatus';

export function InterfaceStatusGrid() {
  const [interfaces, setInterfaces] = useState<InterfaceStatusType[]>([]);

  useEffect(() => {
    // Fetch interface data from the backend
    fetch('/api/network-status')
      .then((response) => response.json())
      .then((data) => setInterfaces(data))
      .catch((error) => console.error('Error fetching interfaces:', error));
  }, []);

  return (
    <AppShell.Aside p={10} style={{
      background: "none",
      border: "none"
    }}>
        <AppShell.Section><Text size="lg">Interfaces</Text></AppShell.Section>
        <AppShell.Section grow component={ScrollArea}>
            <Stack gap="md">
              {interfaces.map((interfaceData, _) => (
                <InterfaceStatus key={interfaceData.interfaceName} {...interfaceData} />
              ))}
            </Stack>
        </AppShell.Section>
    </AppShell.Aside>
  );
}