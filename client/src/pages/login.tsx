import { useState } from "react"
import { useLocation } from "wouter"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"
import { loginUser } from "../api/auth"

export default function LoginPage() {
	useEnsureAuthenticated(false)
	const [username, setUsername] = useState("")
	const [password, setPassword] = useState("")
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const [, setLocation] = useLocation()

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setLoading(true)
		setError(null)
		const res = await loginUser({ username, password })
		if (res.ok) {
			setTimeout(() => {
				setLocation("/home")
			}, 2000)
		} else {
			if (res.error === "Request failed with status code 401") {
				setError("Invalid username or password")
			} else {
				setError(res.error || "Login failed")
			}
		}
		setLoading(false)
	}

	return (
		<div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
			<form
				onSubmit={handleSubmit}
				className="bg-white p-8 rounded-sm shadow-sm w-full max-w-sm flex flex-col gap-4"
			>
				<h1 className="text-2xl font-bold text-center mb-2">Login</h1>
				<label className="flex flex-col gap-1">
					<span className="font-light">Username</span>
					<input
						type="text"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						className="border rounded-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200"
						required
						autoFocus
					/>
				</label>
				<label className="flex flex-col gap-1">
					<span className="font-light">Password</span>
					<input
						type="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="border rounded-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200"
						required
					/>
				</label>
				<button
					type="submit"
					disabled={loading}
					className="bg-blue-500 text-white rounded-sm py-2 font-semibold shadow-sm hover:bg-blue-600 transition"
				>
					{loading ? "Logging in..." : "Login"}
				</button>
				{error && (
					<div className="text-red-500 text-sm text-center">{error}</div>
				)}
			</form>
		</div>
	)
}
