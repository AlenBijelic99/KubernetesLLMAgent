import {
    Box,
    Step,
    StepDescription,
    StepIcon,
    StepIndicator,
    Stepper,
    StepSeparator,
    StepStatus,
    StepTitle,
    useSteps,
} from "@chakra-ui/react";
import { AgentRunPublic, Event } from "../../client";

interface RunAgentStepperProps {
    run: AgentRunPublic;
}

const groupNames: { [key: string]: string } = {
    'metric_analyser': 'Metric Analysis',
    'diagnostic': 'Diagnostic',
    'call_tool': 'Tool Call'
};

// Function to group events by key in event_data except when a specific key is encountered
const groupEvents = (events: Event[]) => {
    let groups: { events: Event[], name: string }[] = [];
    let currentGroup: Event[] = [];
    let currentKey: string | null = null;

    events.forEach(event => {
        const key = Object.keys(event.event_data)[0];

        if (currentGroup.length === 0 || key === currentKey || key === 'call_tool') {
            currentGroup.push(event);
        } else {
            groups.push({ events: currentGroup, name: groupNames[currentKey!] });
            currentGroup = [event];
        }

        if (key !== 'call_tool') {
            currentKey = key;
        }
    });

    if (currentGroup.length > 0) {
        groups.push({ events: currentGroup, name: groupNames[currentKey!] });
    }

    return groups;
};

const RunAgentStepper = ({ run }: RunAgentStepperProps) => {
    const eventGroups = groupEvents(run.events);

    const { activeStep } = useSteps({
        index: eventGroups.length,
        count: eventGroups.length,
    });

    return (
        <Stepper colorScheme="teal" index={activeStep} size="sm" orientation="vertical" gap="0" padding="10">
            {eventGroups.map((group, index) => (
                <Step key={index}>
                    <StepIndicator>
                        <StepStatus complete={<StepIcon />} />
                    </StepIndicator>

                    <Box flexShrink="0" textAlign="left" width="100%">
                        <StepTitle>{`Step ${index + 1}: ${group.name}`}</StepTitle>
                        <StepDescription as="div">
                            <Box whiteSpace="pre-wrap" wordBreak="break-word" overflowWrap="anywhere">
                                {group.events.map((event, subIndex) => {
                                    const key = Object.keys(event.event_data)[0];
                                    const messages = event.event_data[key].messages;

                                    return (
                                        <Box key={subIndex} mb={2}>
                                            <strong>{key}:</strong>
                                            {messages.map((message, msgIndex) => (
                                                <Box key={msgIndex} mt={1}>
                                                    {message.content}
                                                </Box>
                                            ))}
                                        </Box>
                                    );
                                })}
                            </Box>
                        </StepDescription>
                    </Box>

                    <StepSeparator />
                </Step>
            ))}
        </Stepper>
    );
};

export default RunAgentStepper;
