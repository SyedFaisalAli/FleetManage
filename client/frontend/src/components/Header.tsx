import { Group, Image, Container } from '@mantine/core';
import { useState } from 'react';
import classes from './Header.module.css';

const links = [
  { name: 'Assistant', to: '/assistant' },
  { name: 'Configs', to: '/configs' },
  { name: 'Settings', to: '/settings' }
];

export function Header() {
    const [active, setActive] = useState(links[0].to);

    const items = links.map((link) => (
        <a
            key={link.name}
            href={link.to}
            data-active={active === link.to || undefined}
            className={classes.link}
            onClickCapture={(event) => {
                event.preventDefault();
                setActive(link.to);
            }}
        >
            {link.name}
        </a>
    ));

    return (
        <header className={classes.header}>
            <Container size='md' className={classes.inner}>
                <h1 className={classes.title}>Net Assist</h1>
                <Group gap={5} visibleFrom='xs'>
                    {items}
                </Group>
            </Container>
        </header>
    );
}