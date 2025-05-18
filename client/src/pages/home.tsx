import { Link } from "wouter"
import { usePrograms } from "../api/programs"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"

export default function HomePage() {
	const user = useEnsureAuthenticated(true)
	const { data: programs, isLoading } = usePrograms()

	if (isLoading) return <p className="m-4">Loading...</p>

	if (user?.role === "professor") {
		return (
			<div className="flex flex-col gap-4 p-4">
				<h1 className="text-2xl">
					Welcome, <b>{user.username}</b>
				</h1>
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{programs?.map((program) => (
						<Link key={program.id} href={`/program/${program.id}`}>
							<div className="flex flex-col gap-2 p-4 border border-gray-300 rounded-md cursor-pointer h-full">
								<h2 className="text-lg font-semibold">{program.title}</h2>
								<p>{program.description}</p>
							</div>
						</Link>
					))}
					<Link href="/program/new">
						<div className="flex flex-col gap-2 p-4 justify-center items-center border border-gray-300 rounded-md cursor-pointer h-full min-h-[120px]">
							<h2 className="text-lg font-semibold text-center w-full">
								Add a Program
							</h2>
						</div>
					</Link>
				</div>
			</div>
		)
	}

	return (
		<div className="flex flex-col gap-4 p-4">
			<h1 className="text-xl font-bold">Welcome, {user?.username}</h1>
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{programs?.map((program) => (
					<Link key={program.id} href={`/program/${program.id}`}>
						<div className="flex flex-col gap-2 p-4 border border-gray-300 rounded-md cursor-pointer h-full">
							<h2 className="text-lg font-semibold">{program.title}</h2>
							<p>{program.description}</p>
						</div>
					</Link>
				))}
			</div>
		</div>
	)
}
