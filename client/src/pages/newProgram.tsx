import { useState } from "react"
import { useLocation } from "wouter"
import { createProgram } from "../api/programs"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"
import ReactCodeMirror from "@uiw/react-codemirror"
import { cpp } from "@codemirror/lang-cpp"

export default function NewProgramPage() {
	useEnsureAuthenticated(true)
	const [, setLocation] = useLocation()
	const [title, setTitle] = useState("")
	const [description, setDescription] = useState("")
	const [code, setCode] = useState("")
	const [classId] = useState(1)
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const [success, setSuccess] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setLoading(true)
		setError(null)
		setSuccess(false)
		const res = await createProgram({
			title,
			description,
			code,
			class_id: Number(classId),
		})
		setLoading(false)
		if (res.ok) {
			setSuccess(true)
			setTimeout(() => setLocation("/home"), 1200)
		} else {
			setError(res.error || "Failed to create program")
		}
	}

	return (
		<div className="flex flex-col gap-4 p-4 w-full">
			<h1 className="text-xl font-bold mb-2">Add a Program</h1>
			<form
				onSubmit={handleSubmit}
				className="flex flex-col gap-4 bg-white p-6 rounded-md shadow-sm border border-gray-200"
			>
				{error && (
					<div className="text-red-500 text-sm text-center">{error}</div>
				)}
				{success && (
					<div className="text-green-600 text-sm text-center">
						Program created!
					</div>
				)}
				<label className="flex flex-col gap-1">
					<span className="font-medium">Title</span>
					<input
						type="text"
						value={title}
						onChange={(e) => setTitle(e.target.value)}
						className="border rounded-md px-3 py-2"
						required
					/>
				</label>
				<label className="flex flex-col gap-1">
					<span className="font-medium">Description</span>
					<textarea
						value={description}
						onChange={(e) => setDescription(e.target.value)}
						className="border rounded-md px-3 py-2"
						required
					/>
				</label>
				<label className="flex flex-col gap-1">
					<span className="font-medium">Code</span>
					<ReactCodeMirror
						height="300px"
						extensions={[cpp()]}
						value={code}
						onChange={(e) => setCode(e)}
					/>
				</label>
				<button
					type="submit"
					disabled={loading}
					className="bg-blue-500 text-white rounded-md py-2 font-semibold shadow-sm hover:bg-blue-600 transition"
				>
					{loading ? "Creating..." : "Create Program"}
				</button>
			</form>
		</div>
	)
}
