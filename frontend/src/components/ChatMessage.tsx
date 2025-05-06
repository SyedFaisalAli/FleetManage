import { ScrollArea, Text, Stack, Group, Paper, Collapse, Button } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';

export interface MessageProps {
  type: string;
  role: string;
  functionName?: string;
  timestamp: string;
  content: string;
}

export function ChatMessage({ role, content, timestamp }: MessageProps) {
  const [thinkingOpened, { toggle: toggleThinking }] = useDisclosure(true);

  const hasThink = content.startsWith("<think>");
  let thinkContent = "";
  let mainContent = "";
  if (hasThink) {
    thinkContent = content.split("<think>")[1];
    const thinkContentEndSplit = thinkContent.split("</think>");
    mainContent = (thinkContentEndSplit[1] !== undefined) ? thinkContentEndSplit[1].trimStart() : "";
    thinkContent = thinkContentEndSplit[0].trim();
  } else {
    mainContent = content.trim();
  }

  console.log(hasThink, thinkContent, mainContent);

  return (
    <Paper shadow="sm" radius="md" style={{
        backgroundColor: role === 'user' ? '#e6f7ff' : '#ffffff',
        padding: '8px 12px',
        borderRadius: '4px',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word', // Add this line to enable word wrapping in J
      }}>
        <Stack>
          {(role !== "user" && hasThink) && (
            <div>
              <Group justify="left" mb={5} >
                <Button onClick={toggleThinking}>Show Thinking</Button>
              </Group>
              <Collapse in={thinkingOpened} hidden={!hasThink}>
                  <Paper style={{ borderLeft: "5px solid #ccc" }}>
                    <ScrollArea p={5}><Text size="sm">{thinkContent}</Text></ScrollArea>
                  </Paper>
              </Collapse>
            </div>
          )}
          <Text
            size={role === "function" ? "sm" : "md"}
            c={role === "function" ? "dimmed" : undefined}
            style={{ fontFamily: (role === "function") ? "monospace" : "sans-serif"}}
          >
            {mainContent}
          </Text>
          <Group justify="right">
            <Text size="xs" style={{ color: "#666" }}>{timestamp}</Text>
          </Group>
        </Stack>
    </Paper>
  );
};

export default ChatMessage;