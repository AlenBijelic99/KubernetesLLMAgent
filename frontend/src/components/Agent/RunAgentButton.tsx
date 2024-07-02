import { AgentService } from "../../client";
import { Button, useToast } from "@chakra-ui/react";

const RunAgentButton = () => {
    const toast = useToast();

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
        <Button colorScheme='teal' onClick={handleClick}>Run Agent</Button>
    );
}

export default RunAgentButton;
