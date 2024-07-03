import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "../../hooks/useAuth"
import RunAgentButton from "../../components/Agent/RunAgentButton.tsx";
import RunList from "../../components/Agent/RunList.tsx";
import {useEffect, useState} from "react";
import {AgentRun, AgentService} from "../../client";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const [runs, setRuns] = useState<AgentRun[]>([])

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const data = await AgentService.getAgentRuns();
        setRuns(data);
      } catch (error) {
        console.error("Failed to fetch agent runs", error);
      }
    };

    fetchRuns();
  }, [])

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text>
          <RunAgentButton />
          <RunList runs={runs} />
        </Box>
      </Container>
    </>
  )
}
