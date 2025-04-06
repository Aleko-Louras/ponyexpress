import { useState } from "react";
import { useNavigate, Link } from "react-router";
import { useAuth } from "../providers/AuthProvider";
import api from "../api";

const headerClassName = "text-center text-4xl font-extrabold py-4";
const formContainerClass = "flex flex-col items-center justify-center h-screen bg-gradient-to-b from-blue-600 to-violet-600";
const formBoxClass = "bg-white p-6 rounded-lg shadow-lg w-80";
const inputClass = "w-full px-3 py-2 mb-4 border rounded text-sm";
const buttonClass = "w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50";

function Register() {
    const { login } = useAuth();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({ username: "", email: "", password: "", confirmPassword: "" });
    const [error, setError] = useState("");

    const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        try {
            await api.postForm("/auth/registration", {}, formData);
            login();
            navigate("/chats");
        }
        catch (err) {
            setError(err.message || "Registration error");
        }
    };

    const {username, email, password, confirmPassword} = formData;

    return (
        <div className={formContainerClass}>
            <h1 className={headerClassName}>Pony Express</h1>
            <form onSubmit={handleSubmit} className={formBoxClass}>
                {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
                <label className="text-sm font-medium">Username</label>
                <input name="username" className={inputClass} value={username} onChange={handleChange} />
                <label className="text-sm font-medium">Email</label>
                <input name="email" className={inputClass} value={email} onChange={handleChange} />
                <label className="text-sm font-medium">Password</label>
                <input type="password" name="password" className={inputClass} value={password} onChange={handleChange} />
                <label className="text-sm font-medium">Confirm Password</label>
                <input type="password" name="confirmPassword" className={inputClass} value={confirmPassword} onChange={handleChange} />
                <button
                    className={buttonClass}
                    disabled={!username || !email || !password || password !== confirmPassword}
                >
                    Register
                </button>
                <Link to="/login" className="block mt-4 text-center text-sm text-blue-700 hover:underline">
                    Login to account
                </Link>
            </form>
        </div>
    );
}

export default Register;