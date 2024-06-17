import { AgentService } from "../../client";
import {Button} from "@chakra-ui/react";

const RunAgentButton = () => {
    const handleClick = async () => {
        try {
            const result = await AgentService.runAgent();
            alert(result.message);
        } catch (error) {
            alert("Error running agent");
        }
    };

    return (
        <Button colorScheme='teal' onClick={handleClick}>Run Agent</Button>
    );
}

export default RunAgentButton;