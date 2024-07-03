import {Box, Container, Grid, GridItem, Text} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "../../hooks/useAuth"
import RunAgentButton from "../../components/Agent/RunAgentButton.tsx";
import RunsTable from "../../components/Agent/RunsTable.tsx";
import {useEffect, useState} from "react";
import {AgentRunPublic, AgentService} from "../../client";
import RunAgentStepper from "../../components/Agent/RunAgentStepper.tsx";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const [runs, setRuns] = useState<AgentRunPublic[]>([]);
  const [selectedRun, setSelectedRun] = useState<AgentRunPublic | null>(null);

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

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text>
          <RunAgentButton />
          <Grid templateColumns='repeat(5, 1fr)'>
            <GridItem w='100%' colSpan={2} h='10' >
              <RunsTable runs={runs} onSelectRun={setSelectedRun} />
            </GridItem>
            <GridItem w='100%' colStart={3} colEnd={6}>
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
    </>
  )
}
