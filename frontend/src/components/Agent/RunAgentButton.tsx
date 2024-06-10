import { AgentService } from "../../client";

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
        <button onClick={handleClick}>Run Agent</button>
    );
}

export default RunAgentButton;