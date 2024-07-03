import {List, ListIcon, ListItem} from "@chakra-ui/react";
import {MdCheckCircle} from "react-icons/md";

const RunList = ({ runs }: any) => {
    return (
        <List spacing={3}>
            {runs.map((run: any) => (
                <ListItem key={run.id} _hover={{
                    background: "white",
                    color: "teal.500",
                }}>
                    <ListIcon as={MdCheckCircle} color='green.500' />
                    {run.start_time} - {run.status}
                </ListItem>
            ))}
        </List>
    )
}

export default RunList;