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

const RunAgentStepper = ({ run }: RunAgentStepperProps) => {
    // Function to group events by consecutive categories
    const groupEvents = (events: Event[]) => {
        let groups: Event[][] = [];
        let currentGroup: Event[] = [];
        let currentSender: string | null = null;

        events.forEach(event => {
            const sender = Object.keys(event.event_data)[0];
            if (currentGroup.length === 0 || sender === currentSender) {
                currentGroup.push(event);
            } else {
                groups.push(currentGroup);
                currentGroup = [event];
            }
            currentSender = sender;
        });

        if (currentGroup.length > 0) {
            groups.push(currentGroup);
        }

        return groups;
    };

    const eventGroups = groupEvents(run.events);

    const { activeStep } = useSteps({
        index: eventGroups.length,
        count: eventGroups.length,
    });

    return (
        <Box>
            <Stepper colorScheme='teal' index={activeStep} size='sm' orientation='vertical' height='400px' gap='0'>
                {eventGroups.map((group, index) => (
                    <Step key={index}>
                        <StepIndicator>
                            <StepStatus complete={<StepIcon />} />
                        </StepIndicator>

                        <Box flexShrink='0'>
                            <StepTitle>{`Step ${index + 1}`}</StepTitle>
                            <StepDescription>
                                {group.map((event, subIndex) => {
                                    const sender = Object.keys(event.event_data)[0];
                                    const messages = event.event_data[sender].messages;

                                    return (
                                        <Box key={subIndex} mb={2}>
                                            <strong>{sender}:</strong>
                                            {messages.map((message, msgIndex) => (
                                                <Box key={msgIndex} mt={1}>
                                                    {message.content}
                                                </Box>
                                            ))}
                                        </Box>
                                    );
                                })}
                            </StepDescription>
                        </Box>

                        <StepSeparator />
                    </Step>
                ))}
            </Stepper>
        </Box>
    );
};

export default RunAgentStepper;
