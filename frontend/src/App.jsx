import { BrowserRouter, Routes, Route, NavLink, useParams} from "react-router";
import { QueryClient, QueryClientProvider, useQuery} from "@tanstack/react-query";

const headerClassName = "text-center text-4xl font-extrabold py-4";
const layoutClass = "flex h-screen";
const sidebarClass = "w-64 bg-blue-300 p-4 overflow-y-auto border-r-2";
const navItemClass = ({ isActive }) => 'block px-2 py-1 rounded hover:bg-violet-300 hover:border-solid hover:border-1  ${isActive ? "bg-violet-300 font-semibold border-solid border-1" : ""}';
const contentClass = "flex-1 overflow-y-auto p-4 bg-gradient-to-b from-blue-600 to-violet-600";
const messageClass = "bg-cyan-100 p-3 border-solid border-2 border-purple rounded shadow-lg shadow-purple-900";
const queryClient = new QueryClient();

/**Component for the navbar of chat name links*/
function ChatList() {
    //get our list of chats with queryFunction
    const { data } = useQuery({
      queryKey: ["chats"],
      queryFn: async () => {
        const res = await fetch("http://127.0.0.1:8000/chats");
        return res.json();
      },
    });
  return (
    <div className={sidebarClass}>
      <h1 className="text-xl font-bold mb-4 text-center">Pony Express</h1>
      {data?.chats
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
  return (
    <div className={layoutClass}>
      <ChatList />
      <div className={contentClass}>
      </div>
    </div>
  );
}

/**Component for messages */
function ChatDetailPage() {

  const { chatId } = useParams();

  //get the messages for the chat id we want
  const { data } = useQuery({
    queryKey: ["messages", chatId],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/chats/${chatId}/messages`);
      return res.json();
    },
  });

  //get all the accounts here for usernames
  const { data: accountsData } = useQuery({
    queryKey: ["accounts"],
    queryFn: async () => {
      const res = await fetch("http://127.0.0.1:8000/accounts");
      return res.json();
    },
  });

  //get the username from an id parameter
  const getUsername = (accountId) => {
      const account = accountsData?.accounts?.find(a => a.id === accountId);
      return account ? account.username : "Unknown";
  };

  return (
    <div className={layoutClass}>
      <ChatList />
      <div className={contentClass}>
        <div className="space-y-4">
          {data?.messages?.map((msg) => (
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

function NotFound() {
  return <h1 className={headerClassName}>404: Not Found</h1>;
}

function Home() {
  return <h1 className={headerClassName}>Pony Express</h1>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<NotFound />} />
          <Route path="/chats" element={<ChatsPage/>} />
          <Route path="/chats/:chatId" element={<ChatDetailPage/>}/>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
