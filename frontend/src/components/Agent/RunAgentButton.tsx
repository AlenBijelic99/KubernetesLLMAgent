import {AgentService, WebsocketService} from "../../client";
import {Box, Text, Button, useToast } from "@chakra-ui/react";
import {useEffect, useState} from "react";

const RunAgentButton = () => {
    const toast = useToast();
    const [status, setStatus] = useState<String[]>([]);

    useEffect(() => {
        const socket = WebsocketService.getWebSocket();

        socket.onmessage = (event) => {
            const message = event.data;
            setStatus((prevStatus) => [...prevStatus, message]);
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
            socket.close();
        };
    }, []);

    const handleClick = async () => {
        const agentPromise = AgentService.runAgent();

        toast.promise(agentPromise, {
            loading: {
                title: "Running Agent",
                description: "Please wait while the agent is running...",
            },
            success: {
                title: "Success",
                description: "Agent ran successfully",
                duration: 5000,
                isClosable: true,
            },
            error: {
                title: "Error",
                description: "An unexpected error occurred.",
                duration: 5000,
                isClosable: true,
            },
        });

        try {
            await agentPromise;
        } catch (error: any) {
            let errorMessage = "An unexpected error occurred.";
            if (error.response && error.response.status === 429) {
                errorMessage = "You exceeded your current quota, please check your plan and billing details.";
            } else if (error.message) {
                errorMessage = error.message;
            }

            toast({
                title: "Error",
                description: errorMessage,
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        }
    };

    return (
        <>
            <Button colorScheme='teal' onClick={handleClick}>Run Agent</Button>
            <Box mt={4}>
                {status.map((message, index) => (
                    <Text key={index}>{message}</Text>
                ))}
            </Box>
        </>
    );
}

export default RunAgentButton;
