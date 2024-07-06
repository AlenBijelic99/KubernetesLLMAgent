import {useEffect, useState} from "react";
import {
    Box,
    Button,
    HStack,
    Icon,
    Step,
    StepDescription,
    StepIndicator,
    Stepper,
    StepSeparator,
    StepStatus,
    StepTitle,
    Text,
    useColorMode,
    useSteps,
} from "@chakra-ui/react";
import {CheckIcon, ChevronDownIcon, ChevronUpIcon} from "@chakra-ui/icons";
import {AgentRunPublic, Event} from "../../client";
import {MdDoNotDisturbOn} from "react-icons/md";
import ToolMessage from "./ToolMessage.tsx";
import AIMessage from "./AIMessage.tsx";

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

    let lastKey: string | null = null;

    events.forEach(event => {
        const key = Object.keys(event.event_data)[0];
        if (key !== 'call_tool') {
            if (groups[key]) {
                groups[key].push(event);
                lastKey = key;
            }
        } else if (lastKey && groups[lastKey]) {
            groups[lastKey].push(event);
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

    useEffect(() => {
        setExpandedSteps([]); // Reset expanded steps when the run changes
    }, [run]);

    const toggleExpand = (key: string) => {
        setExpandedSteps(prev =>
            prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
        );
    };

    const expandAll = () => {
        setExpandedSteps(stepKeys);
    };

    const collapseAll = () => {
        setExpandedSteps([]);
    };

    return (
        <Box>
            <HStack mb={4}>
                <Button onClick={expandAll} colorScheme="teal">Expand All</Button>
                <Button onClick={collapseAll} colorScheme="teal">Collapse All</Button>
            </HStack>
            <Stepper colorScheme="teal" index={activeStep} size="sm" orientation="vertical" gap="0" padding="10">
                {stepKeys.map((key) => (
                    <Box key={key} width='100%'>
                        <Step>
                            <StepIndicator>
                                <StepStatus complete={eventGroups[key].length > 0 ? <CheckIcon/> :
                                    <Icon height='1.5em' width='1.5em'
                                          color={colorMode === "dark" ? "gray.800" : "white"} as={MdDoNotDisturbOn}/>}/>
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
                                            <Box mb={expandedSteps.includes(key) ? 8 : 0}>
                                                {eventGroups[key].map((event, subIndex) => {
                                                    const eventKey = Object.keys(event.event_data)[0];
                                                    const messages = event.event_data[eventKey].messages;

                                                    return (
                                                        <Box key={subIndex} mb={2}>
                                                            {messages.map((message, msgIndex) => (
                                                                <Box key={msgIndex}>
                                                                    {message.content !== "" && (
                                                                        <>
                                                                            {message.type === 'ai' ? (
                                                                                <AIMessage message={message}/>
                                                                            ) : message.type === 'tool' ? (
                                                                                <ToolMessage message={message}/>
                                                                            ) : (
                                                                                <Text>Unknown message type</Text>
                                                                            )}
                                                                        </>
                                                                    )}
                                                                </Box>
                                                            ))}
                                                        </Box>
                                                    );
                                                })}
                                            </Box>
                                            <Box
                                                position="absolute"
                                                bottom="0"
                                                left="0"
                                                right="0"
                                                height={expandedSteps.includes(key) ? 30 : 50}
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
                                                {expandedSteps.includes(key) ? <ChevronUpIcon boxSize={6}/> :
                                                    <ChevronDownIcon boxSize={6}/>}
                                            </Box>
                                        </Box>
                                    )}
                                </StepDescription>
                            </Box>

                            <StepSeparator/>
                        </Step>
                    </Box>
                ))}
            </Stepper>
        </Box>
    );
};

export default RunAgentStepper;
