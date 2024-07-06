import { useCallback, useEffect, useRef, useState } from "react";
import {
    Box,
    Container,
    Drawer,
    DrawerBody,
    DrawerCloseButton,
    DrawerContent,
    DrawerHeader,
    DrawerOverlay,
    Grid,
    GridItem,
    Text,
    useDisclosure,
    useToast,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import useAuth from "../../hooks/useAuth";
import {
    AgentRunAndEventsPublic,
    AgentRunPublic,
    AgentService,
    WebsocketService,
} from "../../client";
import RunAgentStepper from "../../components/Agent/RunAgentStepper";
import RunAgentButton from "../../components/Agent/RunAgentButton";
import RunsTable from "../../components/Agent/RunsTable";

type Run = {
    uuid: string;
}

export const Route = createFileRoute("/_layout/")({
    component: Dashboard,
    validateSearch: (search: Record<string, unknown>): Run => {
        return {
            uuid: search.run as string,
        };
    }
});

function Dashboard() {
    const { user: currentUser } = useAuth();
    const { uuid } = Route.useSearch();
    const [runs, setRuns] = useState<AgentRunPublic[]>([]);
    const [selectedRun, setSelectedRun] = useState<AgentRunAndEventsPublic | null>(null);
    const [, setStatus] = useState<any[]>([]);
    const socketRef = useRef<WebSocket | null>(null);
    const toast = useToast();
    const { isOpen, onOpen, onClose } = useDisclosure();

    const fetchRuns = useCallback(async () => {
        try {
            const data = await AgentService.getAgentRuns();
            setRuns(data.data);
        } catch (error) {
            console.error("Failed to fetch agent runs", error);
        }
    }, []);

    const fetchRunById = useCallback(async (id: string) => {
        try {
            const data = await AgentService.getAgentRunById(id);
            setSelectedRun(data);
            onOpen();
        } catch (error) {
            console.error("Failed to fetch agent run", error);
        }
    }, [onOpen]);

    useEffect(() => {
        fetchRuns();
    }, [fetchRuns]);

    useEffect(() => {
        if (uuid) {
            fetchRunById(uuid);
        }
    }, [uuid, fetchRunById]);

    useEffect(() => {
        const socket = WebsocketService.getWebSocket();
        socketRef.current = socket;

        socket.onopen = () => {
            console.log("WebSocket connection opened.");
        };

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log("Received message:", message);

                // Check if the message is a new run
                if (message.type === 'new_run') {
                    setRuns((prevRuns) => [...prevRuns, message.run]);
                    setSelectedRun(message.run);
                    onOpen();
                } else {
                    // Handle other types of messages
                    setStatus((prevStatus) => [...prevStatus, message]);
                }
            } catch (error) {
                console.error("Error parsing JSON:", error);
            }
        };

        socket.onerror = (event) => {
            let errorMessage = "An error occurred with the WebSocket connection";
            if (event instanceof ErrorEvent) {
                errorMessage = event.message;
            }
            toast({
                title: "WebSocket Error",
                description: errorMessage,
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        };

        socket.onclose = () => {
            toast({
                title: "WebSocket Closed",
                description: "WebSocket connection was closed.",
                status: "warning",
                duration: 5000,
                isClosable: true,
            });
        };

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }, [toast, onOpen]);

    const handleSelectRun = useCallback(async (run: AgentRunPublic) => {
        try {
            const data = await AgentService.getAgentRunById(run.id);
            setSelectedRun(data);
            onOpen();
        } catch (error) {
            console.error("Failed to fetch agent run", error);
        }
    }, [onOpen]);

    return (
        <Container maxW="full">
            <Box pt={12} m={4}>
                <Text fontSize="2xl">
                    Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
                </Text>
                <Text>Welcome back, nice to see you again!</Text>
                <RunAgentButton />
                <Grid templateColumns="repeat(5, 1fr)" gap={4} mt={4}>
                    <GridItem w="100%" colSpan={5}>
                        <RunsTable runs={runs} onSelectRun={handleSelectRun} selectedRun={selectedRun} />
                    </GridItem>
                </Grid>
            </Box>
            <Drawer isOpen={isOpen} placement="right" onClose={onClose} size="xl">
                <DrawerOverlay />
                <DrawerContent>
                    <DrawerCloseButton />
                    <DrawerHeader>Run Details</DrawerHeader>
                    <DrawerBody>
                        {selectedRun && <RunAgentStepper run={selectedRun} />}
                    </DrawerBody>
                </DrawerContent>
            </Drawer>
        </Container>
    );
}

export default Dashboard;
