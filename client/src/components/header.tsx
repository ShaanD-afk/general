import { Link } from "wouter"
import { logoutUser } from "../api/auth"

export default function Header() {
	return (
		<div className="flex flex-row w-full p-4 bg-white shadow-md justify-between items-center">
			<Link href="/home">
				<h4 className="font-bold text-lg cursor-pointer">BhashaCode</h4>
			</Link>
			<div className="flex flex-row gap-4">
				<button
					className="text-red-700 font-bold cursor-pointer"
					onClick={() => logoutUser()}
				>
					Logout
				</button>
			</div>
		</div>
	)
}
