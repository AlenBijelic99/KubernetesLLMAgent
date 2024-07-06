import {createFileRoute} from "@tanstack/react-router";
import Dashboard from "./index.tsx";

export const Route = createFileRoute("/_layout/$uuid")({
    component: Dashboard,
})