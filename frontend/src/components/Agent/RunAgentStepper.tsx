import {useState} from "react";
import {
    Box,
    Step,
    StepDescription,
    StepIndicator,
    Stepper,
    StepSeparator,
    StepStatus,
    StepTitle,
    useColorMode,
    useSteps,
} from "@chakra-ui/react";
import {CheckIcon, ChevronDownIcon, ChevronUpIcon, MinusIcon} from "@chakra-ui/icons";
import {AgentRunPublic, Event} from "../../client";

interface RunAgentStepperProps {
    run: AgentRunPublic;
}

const stepKeys = ['metric_analyser', 'diagnostic', 'solution', 'incident_reporter'];

const groupNames: { [key: string]: string } = {
    'metric_analyser': 'Metric Analysis',
    'diagnostic': 'Diagnostic',
    'solution': 'Solution',
    'incident_reporter': 'Incident Report'
};

// Function to group events by key in event_data except when a specific key is encountered
const groupEvents = (events: Event[]) => {
    let groups: { [key: string]: Event[] } = {
        'metric_analyser': [],
        'diagnostic': [],
        'solution': [],
        'incident_reporter': []
    };

    events.forEach(event => {
        const key = Object.keys(event.event_data)[0];
        if (groups[key]) {
            groups[key].push(event);
        }
    });

    return groups;
};

const RunAgentStepper = ({run}: RunAgentStepperProps) => {
    const eventGroups = groupEvents(run.events);

    // Find the index of the last step with data
    const lastStepWithDataIndex = stepKeys.reduce((lastIndex, key, index) => {
        return eventGroups[key].length > 0 ? index + 1 : lastIndex;
    }, 0);

    const {activeStep} = useSteps({
        index: lastStepWithDataIndex,
        count: stepKeys.length,
    });

    const [expandedSteps, setExpandedSteps] = useState<string[]>([]);
    const {colorMode} = useColorMode();

    const toggleExpand = (key: string) => {
        setExpandedSteps(prev =>
            prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
        );
    };

    return (
        <Stepper colorScheme="teal" index={activeStep} size="sm" orientation="vertical" gap="0" padding="10">
            {stepKeys.map((key) => (
                <Step key={key}>
                    <StepIndicator>
                        <StepStatus complete={eventGroups[key].length > 0 ? <CheckIcon/> : <MinusIcon/>}/>
                    </StepIndicator>

                    <Box flexShrink="0" textAlign="left" width="100%" minHeight="60px" mb="4">
                        <StepTitle>{`${groupNames[key]}`}</StepTitle>
                        <StepDescription as="div">
                            {eventGroups[key].length > 0 && (
                                <Box
                                    whiteSpace="pre-wrap"
                                    wordBreak="break-word"
                                    overflowWrap="anywhere"
                                    maxHeight={expandedSteps.includes(key) ? "none" : "100px"}
                                    overflow="hidden"
                                    position="relative"
                                >
                                    {eventGroups[key].map((event, subIndex) => {
                                        const eventKey = Object.keys(event.event_data)[0];
                                        const messages = event.event_data[eventKey].messages;

                                        return (
                                            <Box key={subIndex} mb={2}>
                                                <strong>{eventKey}:</strong>
                                                {messages.map((message, msgIndex) => (
                                                    <Box key={msgIndex} mt={1}>
                                                        {message.content}
                                                    </Box>
                                                ))}
                                            </Box>
                                        );
                                    })}
                                    <Box
                                        position="absolute"
                                        bottom="0"
                                        left="0"
                                        right="0"
                                        height="50px"
                                        display="flex"
                                        justifyContent="center"
                                        alignItems="flex-end"
                                        cursor="pointer"
                                        onClick={() => toggleExpand(key)}
                                        {...(!expandedSteps.includes(key) && {
                                            bgGradient: colorMode === "dark"
                                                ? "linear(to-t, gray.800, rgba(255,255,255,0))"
                                                : "linear(to-t, white, rgba(255,255,255,0))"
                                        })}
                                    >
                                        {expandedSteps.includes(key) ? <ChevronUpIcon boxSize={6} /> : <ChevronDownIcon boxSize={6} />}
                                    </Box>
                                </Box>
                            )}
                        </StepDescription>
                    </Box>

                    <StepSeparator/>
                </Step>
            ))}
        </Stepper>
    );
};

export default RunAgentStepper;
