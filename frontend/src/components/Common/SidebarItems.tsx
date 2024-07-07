import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { FiBriefcase, FiHome, FiSettings, FiUsers } from "react-icons/fi";

import type { UserPublic } from "../../client";
import {useState} from "react";

const items = [
    { icon: FiHome, title: "Dashboard", path: "/" },
    { icon: FiBriefcase, title: "Items", path: "/items" },
    { icon: FiSettings, title: "User Settings", path: "/settings" },
];

interface SidebarItemsProps {
    onClose?: () => void;
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
    const queryClient = useQueryClient();
    const textColor = useColorModeValue("ui.main", "ui.light");
    const bgActive = useColorModeValue("#E2E8F0", "#4A5568");
    const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"]);
    const navigate = useNavigate();
    const [activePath, setActivePath] = useState<string | null>(null);

    const finalItems = currentUser?.is_superuser
        ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
        : items;

    const listItems = finalItems.map(({ icon, title, path }) => {

        return (
            <Flex
                onClick={() => {
                    setActivePath(path);
                    if (onClose) {
                        onClose();
                    }
                    navigate({ to: path, search: "" });
                }}
                w="100%"
                p={2}
                key={title}
                color={textColor}
                bg={activePath === path ? bgActive : "transparent"}
                borderRadius={activePath === path ? "12px" : "none"}
                _hover={{ background: bgActive, borderRadius: "12px", cursor: "pointer" }}
            >
                <Icon as={icon} alignSelf="center" />
                <Text ml={2}>{title}</Text>
            </Flex>
        );
    });

    return <Box>{listItems}</Box>;
};

export default SidebarItems;
