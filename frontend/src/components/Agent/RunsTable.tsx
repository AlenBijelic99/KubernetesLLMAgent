import {
    Spinner,
    Table,
    TableContainer,
    Tbody,
    Td, Tfoot,
    Th,
    Thead,
    Tr
} from "@chakra-ui/react";
import {AgentRunPublic} from "../../client";
import {CheckCircleIcon, WarningIcon} from "@chakra-ui/icons";

interface RunListProps {
    runs: AgentRunPublic[];
}

const RunsTable = ({runs}: RunListProps) => {
    return (
        <TableContainer>
            <Table variant='simple'>
                <Thead>
                    <Tr>
                        <Th>State</Th>
                        <Th>Timestamp</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {runs.map((run) => (
                        <Tr key={run.id}>
                            <Td>
                                {run.status === 'failed' ? (
                                    <WarningIcon color='red.500' />
                                ) : run.status === 'running' ? (
                                    <Spinner color='blue.500' size='sm'/>
                                ) : (
                                    <CheckCircleIcon color='green.500' />
                                )}
                            </Td>
                            <Td>{run.start_time}</Td>
                        </Tr>
                    ))}
                </Tbody>
                <Tfoot>
                    <Tr>
                        <Th>State</Th>
                        <Th>Timestamp</Th>
                    </Tr>
                </Tfoot>
            </Table>
        </TableContainer>
    )
}

export default RunsTable;