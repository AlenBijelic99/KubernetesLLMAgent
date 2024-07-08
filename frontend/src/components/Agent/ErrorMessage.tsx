import { Box, Text, Heading, useColorMode } from "@chakra-ui/react";

interface ErrorMessageProps {
    message: any;
}

const ErrorMessage = ({ message }: ErrorMessageProps) => {
    const { colorMode } = useColorMode();

    return (
        <Box
            border="1px"
            borderColor={colorMode === "dark" ? "red.300" : "red.500"}
            borderRadius="md"
            p={4}
            my={2}
            bg={colorMode === "dark" ? "gray.700" : "gray.100"}
            shadow="md"
        >
            {message.content !== "" && (
                <>
                    <Text fontSize='sm'>{message.response_metadata.model_name}</Text>
                    <Heading as="h3" size="md" mb={2} color={colorMode === "dark" ? "red.300" : "red.700"}>
                        Error
                    </Heading>
                    <Text fontSize='md' mb={4} p={2} bg={colorMode === "dark" ? "gray.800" : "white"} borderRadius="md">
                        {message.content}
                    </Text>
                </>
            )}
        </Box>
    );
};

export default ErrorMessage;
