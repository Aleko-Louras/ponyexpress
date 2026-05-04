import {motion} from 'motion/react'
import {BrowserRouter, Navigate, Routes, Route, NavLink, useParams} from "react-router";
import {QueryClient, QueryClientProvider, useQueryClient} from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./providers/AuthProvider";
import Login from './accounts/Login.jsx';
import Register from './accounts/Register.jsx';
import {useAccount, useChats, useChatAccounts, useChatMessages} from "./queries.js";
import Settings from "./accounts/Settings.jsx";
import {useRef, useEffect, useState} from "react";
import api from "./api.js";

const headerClassName = "text-center text-4xl font-extrabold py-4";
const layoutClass = "flex h-screen";
const sidebarClass = "w-64 bg-blue-300 p-4 overflow-y-auto border-r-2";
const navItemClass = ({ isActive }) => 'block px-2 py-1 rounded hover:bg-violet-300 hover:border-solid hover:border-1  ${isActive ? "bg-violet-300 font-semibold border-solid border-1" : ""}';
const contentClass = "flex-1 overflow-y-auto p-4 bg-gradient-to-b from-blue-600 to-violet-600";
const messageClass = "bg-cyan-100 p-3 border-solid border-2 border-purple rounded shadow-lg shadow-purple-900";

const queryClient = new QueryClient();

/**Component for the navbar of chat name links*/
export function ChatList() {
  const {account} = useAccount();
  console.log(account);
  const {chats} = useChats();
  const {logout} = useAuth();


  return (
    <div className={sidebarClass}>
      <h1 className="text-xl font-bold mb-4 text-center">Pony Express</h1>
          <div className="mb-4">
            <p className="text-lg text-center font-bold text-purple-700">{account.username}</p>
            <NavLink to="/settings" className="text-lg text-blue-800 font-bold block hover:underline text-center">
              settings
            </NavLink>
            <button onClick={logout} className="text-lg font-bold text-red-600 hover:underline block mx-auto">
              logout
            </button>
          </div>
      {chats
        ?.sort((a, b) => a.name.localeCompare(b.name))
        .map((chat) => (
          <NavLink key={chat.id} to={`/chats/${chat.id}`} className={navItemClass}>
            {chat.name}
          </NavLink>
        ))}
    </div>
  );
}

/**Component for the chats/ route i.e. no messages, just the navbar and empty messages */
function ChatsPage() {
  const {loggedIn} = useAuth();
  if (!loggedIn) return <Navigate to="/" />;

  return (
    <div className={layoutClass}>
      <ChatList />
      <div className={contentClass}></div>
    </div>
  );
}

/**Component for messages */
function ChatDetailPage() {

  const messagesEnd = useRef(null);
  const { chatId } = useParams();
  const {loggedIn} = useAuth();
  const {messages} = useChatMessages(chatId);
  const {accounts} = useChatAccounts(chatId);

  if(!loggedIn) return <Navigate to="/"/>;

  const getUsername = (accountId) => {
    const acc = accounts.find((a) => a.id === accountId);
    return accountId === null ? "[removed]" : acc?.username || "Unknown";
  };

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
      <div className={layoutClass}>
        <ChatList />
        <div className="flex-1 flex flex-col bg-gradient-to-b from-blue-600 to-violet-600">
          <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: 'calc(100vh - 96px)' }}>
            {messages.map((msg) => (
                <Message key={msg.id} message={msg} getUsername={getUsername} chatId={chatId} />
            ))}
            <div ref={messagesEnd} />
          </div>
          <NewMessageForm chatId={chatId} />
        </div>
      </div>
  );
}

/*Component for new message input*/
function NewMessageForm({ chatId }) {
  const { account } = useAccount();
  const [text, setText] = useState("");
  const queryClient = useQueryClient();
  const { accounts } = useChatAccounts(chatId);
  const isMember = accounts.some((member) => member.id === account.id);
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    await api.post(`/chats/${chatId}/messages`, {}, {
      text,
      account_id: account.id,
    });
    //re-fetch the messages immediately
    await queryClient.invalidateQueries({queryKey: ["messages", chatId]});

    setText("");
  };
  if (!isMember) return null;

  return (
      <form onSubmit={handleSubmit} className="p-4 bg-cyan-100 border-t-2 border-b-2 flex gap-2">
        <input
            type="text"
            className="flex-1 px-3 py-2 border rounded text-sm text-purple-700"
            placeholder="New message"
            value={text}
            onChange={(e) => setText(e.target.value)}
        />
        <button
            className="bg-purple-700 text-white px-4 py-2 border-2 border-black rounded disabled:opacity-50"
            disabled={!text.trim()}
        >
          Send
        </button>
      </form>
  );
}

/*Component for a message, it has two states for editing and viewing*/
function Message({ message, getUsername, chatId }) {
  const { account } = useAccount();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(message.text);

  const isOwner = message.account_id === account.id;

  const handleDelete = async () => {
    await api.delete(`/chats/${chatId}/messages/${message.id}`);
    await queryClient.invalidateQueries({queryKey: ["messages", chatId]});
  };

  const handleSave = async () => {
    await api.put(`/chats/${chatId}/messages/${message.id}`, {}, { text });
    setEditing(false);
    await queryClient.invalidateQueries({queryKey: ["messages", chatId]});
  };

  const handleCancel = () => {
    setText(message.text);
    setEditing(false);
  };

  return (
      <div className="bg-cyan-100 p-3 border-solid border-2 border-purple rounded shadow-lg shadow-purple-900">
        <div className="text-sm font-medium text-purple-700">
          {getUsername(message.account_id)}
          <span className="float-right text-xs text-purple-500">
          {new Date(message.created_at).toLocaleString()}
        </span>
        </div>

        {editing ? (
            <div className="flex items-start gap-2 mt-2">
              <input
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  className="flex-1 px-2 py-1 text-sm border rounded"
              />
              <button
                  className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={handleSave}
              >
                Save
              </button>
              <button
                  className="text-xs px-2 py-1 bg-gray-400 text-white rounded hover:bg-gray-500"
                  onClick={handleCancel}
              >
                Cancel
              </button>
            </div>
        ) : (
            <>
              <div className="mt-2">{message.text}</div>
              {isOwner && (
                  <div className="mt-2 flex gap-2">
                    <button
                        className="text-xs px-2 py-1 bg-yellow-400 text-black rounded hover:bg-yellow-500"
                        onClick={() => setEditing(true)}
                    >
                      Edit
                    </button>
                    <button
                        className="text-xs px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        onClick={handleDelete}
                    >
                      Delete
                    </button>
                  </div>
              )}
            </>
        )}
      </div>
  );
}

//App structure//
function NotFound() {
  return <h1 className={headerClassName}>404: Not Found</h1>;
}

function Home() {
  const {loggedIn} = useAuth();
  return loggedIn ? <Navigate to="/chats"/> : <Navigate to="/login"/>
}

function App() {

  return (
    <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<NotFound />} />
          <Route path="/chats" element={<ChatsPage/>} />
          <Route path="/chats/:chatId" element={<ChatDetailPage/>}/>
          <Route path="/login" element={<Login/>}/>
          <Route path="/register" element={<Register/>}/>
          <Route path="/settings" element={<Settings/>}/>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
