import {Box, Heading, Stack, Text, useColorMode} from "@chakra-ui/react";

interface AIMessageProps {
    message: any;
}

const AIMessage = ({message}: AIMessageProps) => {
    const {colorMode} = useColorMode();

    return (
        <Box
            border="1px"
            borderColor={colorMode === "dark" ? "teal.300" : "teal.500"}
            borderRadius="md"
            p={4}
            my={2}
            bg={colorMode === "dark" ? "gray.700" : "gray.100"}
            shadow="md"
        >
            {message.content !== "" && (
                <>
                    <Text fontSize='sm'>{message.response_metadata.model_name}</Text>
                    <Heading as="h3" size="md" mb={2} color={colorMode === "dark" ? "teal.300" : "teal.700"}>
                        AI Message
                    </Heading>
                    <Text fontSize='md' mb={4} p={2} bg={colorMode === "dark" ? "gray.800" : "white"} borderRadius="md">
                        {message.content}
                    </Text>
                </>
            )}
            {Array.isArray(message.tool_calls) && message.tool_calls.length > 0 && (
                <Stack spacing={4}>
                    {message.error && message.error !== "" && (
                        <Text fontSize="md">
                            Error : {message.error}
                        </Text>
                    )}
                    <Heading as="h4" size="sm" color={colorMode === "dark" ? "blue.300" : "blue.700"}>
                        Calling Functions
                    </Heading>
                    {message.tool_calls.map((tool_call: any, index: number) => (
                        <Box
                            key={index}
                            border="1px"
                            borderColor={message.error && message.error !== "" ? "red.500" : colorMode === "dark" ? "blue.300" : "blue.500"}
                            borderRadius="md"
                            p={4}
                            bg={colorMode === "dark" ? "gray.800" : "white"}
                            shadow="sm"
                        >
                            <Text fontSize='sm'>{message.response_metadata.model_name}</Text>
                            <Text fontSize='md' fontWeight="bold" color={colorMode === "dark" ? "blue.200" : "blue.600"}>
                                {tool_call.name}
                            </Text>
                            <Text fontSize='md' mt={2}>{JSON.stringify(tool_call.args)}</Text>
                        </Box>
                    ))}
                </Stack>
            )}
        </Box>
    );
};

export default AIMessage;
