import {
    Spinner,
    Table,
    TableContainer,
    Tbody,
    Td,
    Th,
    Thead,
    Tr, useColorMode
} from "@chakra-ui/react";
import { Icon } from "@chakra-ui/icons";
import { MdOutlineErrorOutline, MdCheckCircleOutline } from 'react-icons/md';

const RunsTable = ({ runs, onSelectRun, selectedRun }: any) => {
    const { colorMode } = useColorMode();
    return (
        <TableContainer>
            <Table variant='simple' size='sm'>
                <Thead>
                    <Tr>
                        <Th><Icon as={MdCheckCircleOutline} boxSize={5} color='gray.500' /></Th>
                        <Th>Start Time</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {runs.map((run: any) => (
                        <Tr
                            key={run.id}
                            onClick={() => onSelectRun(run)}
                            _hover={{ cursor: "pointer" }}
                            bg={colorMode === "dark"
                                ? selectedRun?.id === run.id ? "gray.900" : "gray.800"
                                : selectedRun?.id === run.id ? "gray.200" : "white"}
                            color={colorMode === "dark" ? "white" : "black"}
                        >
                            <Td>
                                {run.status === 'failed' ? (
                                    <Icon as={MdOutlineErrorOutline} boxSize={5} color='red.500' />
                                ) : run.status === 'running' ? (
                                    <Spinner color='blue.500' size='sm'/>
                                ) : (
                                    <Icon as={MdCheckCircleOutline} boxSize={5} color='green.500' />
                                )}
                            </Td>
                            <Td>{run.start_time}</Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </TableContainer>
    )
}

export default RunsTable;
