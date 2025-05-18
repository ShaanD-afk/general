import { Link } from "wouter"
import { logoutUser } from "../api/auth"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"

export default function Header() {
	const user = useEnsureAuthenticated(true)

	return (
		<div className="flex flex-row w-full p-4 py-6 bg-blue-900 shadow-md justify-between items-center">
			<Link href="/home">
				<h4 className="font-bold text-white text-xl cursor-pointer">
					BhashaCode
				</h4>
			</Link>
			<div className="flex flex-row gap-4 text-white">
				<p>
					Logged in as <b>{user?.username}</b> |{" "}
					<button
						className="font-medium underline cursor-pointer"
						onClick={() => logoutUser()}
					>
						Logout
					</button>
				</p>
			</div>
		</div>
	)
}
