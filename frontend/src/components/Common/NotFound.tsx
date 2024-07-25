import { Button, Container, Text } from "@chakra-ui/react"
import {useNavigate} from "@tanstack/react-router"

const NotFound = () => {
  const navigate = useNavigate()
  return (
    <>
      <Container
        h="100vh"
        alignItems="stretch"
        justifyContent="center"
        textAlign="center"
        maxW="sm"
        centerContent
      >
        <Text
          fontSize="8xl"
          color="ui.main"
          fontWeight="bold"
          lineHeight="1"
          mb={4}
        >
          404
        </Text>
        <Text fontSize="md">Oops!</Text>
        <Text fontSize="md">Page not found.</Text>
        <Button
          onClick={() => {
            navigate({ to: "/", search: ""});
          }}
          color="ui.main"
          borderColor="ui.main"
          variant="outline"
          mt={4}
        >
          Go back
        </Button>
      </Container>
    </>
  )
}

export default NotFound
