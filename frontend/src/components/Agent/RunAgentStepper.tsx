import {
    Box,
    Step, StepDescription,
    StepIcon,
    StepIndicator,
    Stepper, StepSeparator,
    StepStatus,
    StepTitle,
    useSteps,
} from "@chakra-ui/react";

const RunAgentStepper = ({run}: any) => {
    const { activeStep } = useSteps({
        index: run.events.length,
        count: run.events.length,
    })

    return (
        <Box>
            <Stepper colorScheme='teal' index={activeStep} size='sm' orientation='vertical' height='400px' gap='0'>
                {run.events.map((event: any, index: number) => (
                    <Step key={event.id}>
                        <StepIndicator>
                            <StepStatus
                                complete={<StepIcon />}
                            />
                        </StepIndicator>

                        <Box flexShrink='0'>
                            <StepTitle>{`Step ${index + 1}`}</StepTitle>
                            <StepDescription>{JSON.stringify(event.event_data)}</StepDescription>
                        </Box>

                        <StepSeparator />
                    </Step>
                ))}
            </Stepper>
        </Box>
    )
}

export default RunAgentStepper;