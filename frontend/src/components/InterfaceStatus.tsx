import { Paper } from '@mantine/core';
import styles from './InterfaceStatus.module.css';

export interface InterfaceStatusType {
    interfaceName: string;
    ipAddress: string;
    gateway: string;
    readyStatus: string;
}

export function InterfaceStatus({
    interfaceName, ipAddress, gateway, readyStatus
}: InterfaceStatusType) {
    return (
        <Paper className={styles.interfaceStatus} shadow="xs" p="xs" radius="lg">
            <h2>{interfaceName}</h2>
            <p><span>IP Address:</span><br />{ipAddress}</p>
            <p><span>Gateway:</span><br />{gateway}</p>
            <p><span>Status:</span> {readyStatus.toUpperCase()}</p>
        </Paper>
    );
}