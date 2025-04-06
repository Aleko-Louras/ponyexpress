import {BrowserRouter, Navigate, Routes, Route, NavLink, useParams} from "react-router";
import { QueryClient, QueryClientProvider} from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./providers/AuthProvider";
import Login from './accounts/Login.jsx';
import Register from './accounts/Register.jsx';
import {useAccount, useChats, useChatAccounts, useChatMessages} from "./queries.js";
import Settings from "./accounts/Settings.jsx";

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

  const { chatId } = useParams();
  const {loggedIn} = useAuth();
  const {messages} = useChatMessages(chatId);
  const {accounts} = useChatAccounts(chatId);

  if(!loggedIn) return <Navigate to="/"/>;

  const getUsername = (accountId) => {
    const acc = accounts.find((a) => a.id === accountId);
    return accountId === null ? "[removed]" : acc?.username || "Unknown";
  };

  return (
    <div className={layoutClass}>
      <ChatList />
      <div className={contentClass}>
        <div className="space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={messageClass}>
              <div className="text-sm font-medium text-purple-700">
                {getUsername(msg.account_id)}
                <span className="float-right text-xs text-purple-500">
                  {new Date(msg.created_at).toLocaleString()}
                </span>
              </div>
              <div>{msg.text}</div>
            </div>
          ))}
        </div>
      </div>
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
