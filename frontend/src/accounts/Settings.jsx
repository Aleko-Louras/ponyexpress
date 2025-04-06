import {useEffect, useState} from "react";
import { useNavigate } from "react-router";
import {useAuth} from "../providers/AuthProvider"
import { useAccount } from "../queries";
import {ChatList} from "../App";
import api from "../api";

const layoutClass = "flex h-screen";
const contentClass = "flex-1 overflow-y-auto p-8 bg-gradient-to-b from-blue-600 to-violet-600"
const headerClassName = "text-center text-3xl font-bold my-4 text-white";
const sectionClass = "bg-white p-6 rounded shadow mb-6";
const inputClass = "w-full px-3 py-2 mb-4 border rounded text-sm";
const buttonClass = "w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50";

function Settings() {
    const {loggedIn, logout, setLoggedIn} = useAuth();

    const navigate = useNavigate();

    useEffect(() => {
        if(!loggedIn){
            navigate("/login");
        }
    }, [loggedIn, navigate]);

    const { account, error: loadError } = useAccount();

    const [form, setForm] = useState({ username: account.username, email: account.email });
    const [passwordForm, setPasswordForm] = useState({ old: "", new: "", confirm: "" });
    const [error, setError] = useState("");


    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            await api.put("/accounts/me", {}, form);
            setError("");
        } catch (err) {
            setError(err.message);
        }
    };

    const handlePassword = async (e) => {
        e.preventDefault();
        if (passwordForm.new !== passwordForm.confirm) {
            setError("Passwords do not match");
            return;
        }

        try {
            await api.putForm("/accounts/me/password", {}, {
                old_password: passwordForm.old,
                new_password: passwordForm.new,
            });
            setPasswordForm({ old: "", new: "", confirm: "" });
            setError("");
        } catch (err) {
            setError(err.message);
        }
    };

    const handleDelete = async () => {
        try {
            await api.delete("/accounts/me");
            setLoggedIn(false);
        } catch (err) {
            setError(err.message);
        }
    };

    if (account.id === -1) return null;

    return (
        <div className={layoutClass}>
            <ChatList/>
            <div className={contentClass}>
                <h1 className={headerClassName}>Settings</h1>
                {loadError && <p className="text-red-500 text-sm text-center">{loadError.message}</p>}
                {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}
                <form className={sectionClass} onSubmit={handleUpdate}>
                    <h2 className="text-xl font-semibold mb-4">Update Account</h2>
                    <input
                        className={inputClass}
                        value={form.username}
                        onChange={(e) => setForm({ ...form, username: e.target.value })}
                    />
                    <input
                        className={inputClass}
                        value={form.email}
                        onChange={(e) => setForm({ ...form, email: e.target.value })}
                    />
                    <button className={buttonClass}>Update</button>
                </form>

                <form className={sectionClass} onSubmit={handlePassword}>
                    <h2 className="text-xl font-semibold mb-4">Update Password</h2>
                    <input
                        type="password"
                        className={inputClass}
                        placeholder="Current Password"
                        value={passwordForm.old}
                        onChange={(e) => setPasswordForm({ ...passwordForm, old: e.target.value })}
                    />
                    <input
                        type="password"
                        className={inputClass}
                        placeholder="New Password"
                        value={passwordForm.new}
                        onChange={(e) => setPasswordForm({ ...passwordForm, new: e.target.value })}
                    />
                    <input
                        type="password"
                        className={inputClass}
                        placeholder="Confirm New Password"
                        value={passwordForm.confirm}
                        onChange={(e) => setPasswordForm({ ...passwordForm, confirm: e.target.value })}
                    />
                    <button className={buttonClass} disabled={passwordForm.new !== passwordForm.confirm}>
                        Update Password
                    </button>
                </form>

                <div className={sectionClass}>
                    <h2 className="text-xl font-semibold mb-4">Manage Account</h2>
                    <button className={`${buttonClass} mb-2`} onClick={logout}>Logout</button>
                    <button className={`${buttonClass} bg-red-500 hover:bg-red-600`} onClick={handleDelete}>Delete Account</button>
                </div>
            </div>
        </div>
    );
}

export default Settings;