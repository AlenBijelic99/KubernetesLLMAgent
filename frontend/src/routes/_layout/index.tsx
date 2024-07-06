import { useEffect, useRef, useState } from "react";
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
//import {createFileRoute, useParams} from "@tanstack/react-router";
import useAuth from "../../hooks/useAuth";
import {
    AgentRunAndEventsPublic,
    AgentRunPublic,
    AgentService,
    WebsocketService,
} from "../../client";
import RunAgentStepper from "../../components/Agent/RunAgentStepper";
import RunAgentButton from "../../components/Agent/RunAgentButton.tsx";
import RunsTable from "../../components/Agent/RunsTable.tsx";
import {createFileRoute, useParams} from "@tanstack/react-router";

export const Route = createFileRoute("/_layout/")({
    component: Dashboard,
})

function Dashboard(){
    const { user: currentUser } = useAuth();
    const params = useParams({ from: "/_layout/$uuid" });
    const uuid = params?.uuid as string | undefined;
    const [runs, setRuns] = useState<AgentRunPublic[]>([]);
    const [selectedRun, setSelectedRun] = useState<AgentRunAndEventsPublic | null>(null);
    const [status, setStatus] = useState<any[]>([]);
    const socketRef = useRef<WebSocket | null>(null);
    const toast = useToast();
    const { isOpen, onOpen, onClose } = useDisclosure();

    useEffect(() => {
        const fetchRuns = async () => {
            try {
                const data = await AgentService.getAgentRuns();
                setRuns(data.data);
            } catch (error) {
                console.error("Failed to fetch agent runs", error);
            }
        };

        fetchRuns();
    }, []);

    useEffect(() => {
        const fetchRunById = async (id: string) => {
            try {
                const data = await AgentService.getAgentRunById(id);
                setSelectedRun(data);
                onOpen();
            } catch (error) {
                console.error("Failed to fetch agent run", error);
            }
        };

        if (uuid) {
            fetchRunById(uuid);
        }
    }, [uuid, onOpen]);

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
                setStatus((prevStatus) => [...prevStatus, message]);
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
    }, [toast]);

    const handleSelectRun = (run: AgentRunAndEventsPublic) => {
        setSelectedRun(run);
        onOpen();
    };

    return (
        <Container maxW="full">
            <Box pt={12} m={4}>
                <Text fontSize="2xl">
                    Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
                </Text>
                <Text>Welcome back, nice to see you again!</Text>
                <RunAgentButton />
                <Box mt={4}>
                    {status.map((message, index) => (
                        <Text key={index}>{JSON.stringify(message)}</Text>
                    ))}
                </Box>
                <Grid templateColumns="repeat(5, 1fr)" gap={4}>
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
};

export default Dashboard;
