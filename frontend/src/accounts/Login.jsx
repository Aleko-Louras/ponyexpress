import { useState } from "react";
import {useNavigate, Link} from "react-router";
import { useAuth } from "../providers/AuthProvider";
import api from "../api";

const headerClassName = "text-center text-4xl font-extrabold py-4";
const formContainerClass = "flex flex-col items-center justify-center h-screen bg-gradient-to-b from-blue-600 to-violet-600";
const formBoxClass = "bg-white p-6 rounded-lg shadow-lg w-80";
const inputClass = "w-full px-3 py-2 mb-4 border rounded text-sm";
const buttonClass = "w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50";

function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();

    const [form, setForm] = useState({username: "", password: ""});
    const [error, setError] = useState("");

    const handleChange = (e) => {
        setForm(prev =>({...prev, [e.target.name]: e.target.value}));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try{
            await api.postForm("/auth/web/login", {}, form);
            login();
            navigate("/chats");
        }
        catch (err) {
            setError("Invalid username or password");
        }
    };

    const {username, password} = form;

    return (
        <div className={formContainerClass}>
            <h1 className={headerClassName}>Pony Express</h1>
            <form onSubmit={handleSubmit} className={formBoxClass}>
                {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
                <label className="text-sm font-medium">Username</label>
                <input
                    name="username"
                    className={inputClass}
                    value={username}
                    onChange={handleChange}
                />
                <label className="text-sm font-medium">Password</label>
                <input
                    type="password"
                    name="password"
                    className={inputClass}
                    value={password}
                    onChange={handleChange}
                />
                <button className={buttonClass} disabled={!username || !password}>
                    Login
                </button>
                <Link to="/register" className="block mt-4 text-center text-sm text-blue-700 hover:underline">
                    Register new account
                </Link>
            </form>
        </div>
    );
}

export default Login;