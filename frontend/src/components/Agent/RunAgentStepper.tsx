import {
    Box,
    Text,
    Step, StepDescription,
    StepIcon,
    StepIndicator,
    StepNumber,
    Stepper, StepSeparator,
    StepStatus,
    StepTitle,
    useSteps
} from "@chakra-ui/react";

const steps = [
    { title: 'First', description: 'Contact Info' },
    { title: 'Second', description: 'Date & Time' },
    { title: 'Third', description: 'Select Rooms' },
]

const RunAgentStepper = ({run}: any) => {
    const { activeStep } = useSteps({
        index: 1,
        count: steps.length,
    })

    return (
        <Box>
            <Stepper index={activeStep} orientation='vertical' height='400px' gap='0'>
                {steps.map((step, index) => (
                    <Step key={index}>
                        <StepIndicator>
                            <StepStatus
                                complete={<StepIcon />}
                                incomplete={<StepNumber />}
                                active={<StepNumber />}
                            />
                        </StepIndicator>

                        <Box flexShrink='0'>
                            <StepTitle>{step.title}</StepTitle>
                            <StepDescription>{step.description}</StepDescription>
                        </Box>

                        <StepSeparator />
                    </Step>
                ))}
            </Stepper>
            <Box mt={4}>
                <Text>Status: {run.status}</Text>
                <Text>Start Time: {run.start_time}</Text>
                {/* Add more details as needed */}
            </Box>
        </Box>
    )
}

export default RunAgentStepper;