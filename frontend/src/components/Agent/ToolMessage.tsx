import { Box, Code, Text, Stack, Divider, useColorMode } from "@chakra-ui/react";

interface ToolMessageProps {
    message: any;
}

const ToolMessage = ({ message }: ToolMessageProps) => {
    const parseToolCalls = (content: string) => {
        return content.split("\n");
    };

    const { colorMode } = useColorMode();

    return (
        <Box
            border="1px"
            borderColor={colorMode === "dark" ? "blue.300" : "blue.500"}
            borderRadius="md"
            p={4}
            my={2}
            bg={colorMode === "dark" ? "gray.700" : "gray.100"}
            shadow="md"
        >
            <Text fontWeight="bold" fontSize="lg" mb={2} color={colorMode === "dark" ? "blue.300" : "blue.700"}>
                {message.name}
            </Text>
            <Divider my={2} />
            <Stack spacing={2}>
                {parseToolCalls(message.content).map((line: string, index: number) => (
                    <Code
                        key={index}
                        p={2}
                        borderRadius="md"
                        bg={colorMode === "dark" ? "gray.800" : "white"}
                        display="block"
                        whiteSpace="pre-wrap"
                    >
                        {line}
                    </Code>
                ))}
            </Stack>
        </Box>
    );
};

export default ToolMessage;
