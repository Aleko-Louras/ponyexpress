//tanstack query hooks that hook up to the api, inspired by the class examples
import { useQuery } from "@tanstack/react-query";
import api from "./api";
import { useAuth } from "./providers/AuthProvider";

const nullAccount = {
    id: -1,
    username: "[removed]",
    email: "",
};

const nullChat = {
    id: -1,
    name: "[loading...]",
};

const nullMessage = {
    id: -1,
    text: "[loading...]",
    created_at: new Date().toISOString(),
    account_id: null,
};

export const useAccount = () => {
    const { loggedIn} = useAuth();
    const { data, error } = useQuery({
        queryKey: ["account"],
        queryFn: () => api.get("/accounts/me"),
        enabled: loggedIn,
        retry: false,
    });

    const account = data || nullAccount;
    return { account, error };
};

export const useChats = () => {
    const { data, error, isLoading } = useQuery({
        queryKey: ["chats"],
        queryFn: () => api.get("/chats"),
        retry: false,
    });

    const chats = isLoading ? [nullChat] : data?.chats || [];
    return { chats, error };
};

export const useChatAccounts = (chatId) => {
    const { data, error, isLoading } = useQuery({
        queryKey: ["chatAccounts", chatId],
        queryFn: () => api.get(`/chats/${chatId}/accounts`),
        enabled: !!chatId,
        retry: false,
    });

    const accounts = isLoading ? [] : data?.accounts || [];
    return { accounts, error };
};

export const useChatMessages = (chatId) => {
    const { data, error, isLoading } = useQuery({
        queryKey: ["messages", chatId],
        queryFn: () => api.get(`/chats/${chatId}/messages`),
        enabled: !!chatId,
        retry: false,
    });

    const messages = isLoading ? [nullMessage] : data?.messages || [];
    return { messages, error };
};