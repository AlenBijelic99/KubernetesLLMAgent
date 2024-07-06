import { Box, Container, Grid, GridItem, Text, useToast } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import useAuth from "../../hooks/useAuth";
import RunAgentButton from "../../components/Agent/RunAgentButton";
import RunsTable from "../../components/Agent/RunsTable";
import { useEffect, useRef, useState } from "react";
import { AgentRunPublic, AgentService, WebsocketService } from "../../client";
import RunAgentStepper from "../../components/Agent/RunAgentStepper";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
});

function Dashboard() {
  const { user: currentUser } = useAuth();
  const [runs, setRuns] = useState<AgentRunPublic[]>([]);
  const [selectedRun, setSelectedRun] = useState<AgentRunPublic | null>(null);
  const [status, setStatus] = useState<any[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const toast = useToast();

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const data = await AgentService.getAgentRuns();
        setRuns(data.data);
      } catch (error) {
        console.error("Failed to fetch agent runs", error);
      }
    };

    fetchRuns();
  }, []);

  useEffect(() => {
    const socket = WebsocketService.getWebSocket();
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connection opened.");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log("Received message:", message);
        setStatus((prevStatus) => [...prevStatus, message]);
      } catch (error) {
        console.error("Error parsing JSON:", error);
      }
    };

    socket.onerror = (event) => {
      let errorMessage = "An error occurred with the WebSocket connection";
      if (event instanceof ErrorEvent) {
        errorMessage = event.message;
      }
      toast({
        title: "WebSocket Error",
        description: errorMessage,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    };

    socket.onclose = () => {
      toast({
        title: "WebSocket Closed",
        description: "WebSocket connection was closed.",
        status: "warning",
        duration: 5000,
        isClosable: true,
      });
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [toast]);

  return (
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text>
          <RunAgentButton />
          <Box mt={4}>
            {status.map((message, index) => (
                <Text key={index}>{JSON.stringify(message)}</Text>
            ))}
          </Box>
          <Grid templateColumns="repeat(5, 1fr)" gap={4}>
            <GridItem w="100%" colSpan={2}>
              <RunsTable runs={runs} onSelectRun={setSelectedRun} />
            </GridItem>
            <GridItem w="100%" colSpan={3}>
              {runs.length === 0 ? (
                  <Text>Please run the agent to show element</Text>
              ) : selectedRun ? (
                  <RunAgentStepper run={selectedRun} />
              ) : (
                  <Text>Please select a run in the left side</Text>
              )}
            </GridItem>
          </Grid>
        </Box>
      </Container>
  );
}

export default Dashboard;
