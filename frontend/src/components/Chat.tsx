import { useRef, useState, useEffect } from 'react';
import { ScrollArea, Container, AppShell, Textarea, Button, Group, Stack } from '@mantine/core';
import { MessageProps, ChatMessage } from './ChatMessage';

function websocketProtocol() {
  if (window.location.protocol === 'https:') {
    return 'wss://';
  } else {
    return 'ws://';
  }
}

export function Chat() {
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [inputValue, setInputValue] = useState('');
  const ws = useRef<WebSocket>(null);
  const viewport = useRef<HTMLDivElement>(null);

  const scrollToBottom = () =>
    viewport.current!.scrollTo({ top: viewport.current!.scrollHeight, behavior: 'smooth' });

  // Initialize WebSocket connection
  useEffect(() => {
    ws.current = new WebSocket(websocketProtocol() + window.location.host + '/mcp_bridge/ws');

    ws.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    const wsCurrent = ws.current;

    return () => {
        wsCurrent.close();
    };
  }, []);

  useEffect(() => {
    if (!ws.current) return;

    ws.current.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      if (newMessage.content === "") {
        return;
      }
      setMessages(prevMessages => {
        if (prevMessages.length > 0) {
          console.log(prevMessages[prevMessages.length - 1])
        }
        if (prevMessages.length > 0
          && prevMessages[prevMessages.length - 1].timestamp === newMessage.timestamp
          && prevMessages[prevMessages.length - 1].role === newMessage.role)
        {
          const newMessages = prevMessages.slice(0, prevMessages.length - 1);
          newMessages.push(newMessage);
          return newMessages;
        } else {
          return [...prevMessages, newMessage]
        }
      });
    };
  }, []);

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (!ws.current) return;
    const message = {
      type: "request",
      role: "user",
      timestamp: new Date().toISOString(),
      content: inputValue
    }

    try {
      await ws.current.send(JSON.stringify(message));
      setMessages(prevMessages => [...prevMessages, message]);
      setInputValue('');

    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <AppShell.Main>
      <Container size="md">
          <Stack gap="md" align="stretch" style={{ height: 'calc(100vh - 100px)' }}>
              <ScrollArea p={10} viewportRef={viewport}>
                <Stack gap="md" flex={1}>
                  {messages.map((message, index) => (
                    <ChatMessage key={index} {...message} />
                  ))}
                </Stack>
              </ScrollArea>
              <Group style={{ marginTop: 'auto', marginBottom: '16px' }}>
                <Textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type a message..."
                  autosize
                  flex={1}
                  maxRows={4}
                  minRows={3}
                />
                <Button onClick={handleSendMessage} disabled={!inputValue}>
                  Send
                </Button>
              </Group>
          </Stack>
      </Container>
    </AppShell.Main>
  );
};
