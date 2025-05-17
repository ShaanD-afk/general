/* eslint-disable @typescript-eslint/no-explicit-any */
import { Link, useLocation, useParams } from "wouter"
import { deleteProgram, useProgramDetail } from "../api/programs"
import { useState } from "react"
import SelectLanguage from "../components/selectLanguage"
import { API_URL } from "../api/api"
import ReactCodeMirror from "@uiw/react-codemirror"
import { cpp } from "@codemirror/lang-cpp"
import Chatbot from "../components/chatbot"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"
import {
	submitQuiz,
	useQuizzesByProgram,
	type QuizSubmissionResult,
} from "../api/quiz"
import {
	PieChart,
	Pie,
	Cell,
	Tooltip,
	Legend,
	ResponsiveContainer,
} from "recharts"

export default function ProgramPage() {
	const user = useEnsureAuthenticated(true)
	const [, redirect] = useLocation()

	const params = useParams<{ id: string }>()
	const programId = params.id

	const [language, setLanguage] = useState("ka")
	const [code, setCode] = useState("")
	const [submissionLoading, setSubmissionLoading] = useState(false)
	const [submissionResult, setSubmissionResult] =
		useState<QuizSubmissionResult | null>(null)
	const [submissionError, setSubmissionError] = useState<string | null>(null)

	const { data: program, isLoading } = useProgramDetail(programId)
	const { data: quizDetails, isLoading: quizLoading } = useQuizzesByProgram(
		parseInt(programId) ?? 0,
		user?.role ?? "student"
	)

	const summaryForLanguage = program?.summaries?.find(
		(e) => e.language === language
	)

	// Use a key on the audio element to force remount on language/audio change
	const audioKey = summaryForLanguage?.audio_link
	const audioUrl = summaryForLanguage?.audio_link
		? API_URL + "/audio/" + summaryForLanguage.audio_link
		: undefined

	async function handleSubmit() {
		setSubmissionLoading(true)
		const { data, error } = await submitQuiz({
			program_id: parseInt(programId),
			user_id: user!.id,
			code: code,
			language_id: 50,
			quiz_language: language,
		})
		setSubmissionLoading(false)

		if (error) {
			setSubmissionError(error)
			return
		}

		if (!data) {
			setSubmissionError("No data returned")
			return
		}

		setSubmissionResult(data)
	}

	if (isLoading) {
		return <p className="p-4">Loading...</p>
	}

	const quizzesWithMarks = (quizDetails ?? []).filter(
		(e) => e.marks !== null && e.marks !== undefined
	)

	return (
		<div className="flex flex-row p-4 gap-8 h-full min-h-0">
			<div className="flex flex-col gap-4 w-full h-full overflow-y-auto pr-4">
				<SelectLanguage language={language} setLanguage={setLanguage} />
				<h3 className="text-2xl font-bold">{program?.program.title}</h3>
				<p>{program?.program.description}</p>
				{audioUrl && (
					<div className="flex flex-col gap-2 p-4 border border-gray-200 rounded-md">
						<audio key={audioKey} controls>
							<source src={audioUrl} type="audio/mpeg" />
							Your browser does not support the audio element.
						</audio>
						<p className="text-sm">
							Click the play button to listen to the explanation!
						</p>
					</div>
				)}
				<h4 className="font-bold text-lg">Summary</h4>
				<p>{summaryForLanguage?.summary}</p>
				<h4 className="font-bold text-lg">Algorithm</h4>
				<p>
					{(summaryForLanguage?.algorithm ?? "").split("\n").map((e) => (
						<>
							<p>{e}</p>
						</>
					))}
				</p>
				{parseInt(programId) && user?.id && (
					<Chatbot
						programId={parseInt(programId)}
						studentId={user?.id}
						language={language}
					/>
				)}
				{user?.role === "professor" && (
					<button
						className="text-red-700 text-left cursor-pointer underline text-sm"
						onClick={async () => {
							await deleteProgram(parseInt(programId ?? "0"))
							redirect("/home")
						}}
					>
						Delete this program
					</button>
				)}
			</div>
			{user?.role === "student" ? (
				<div className="flex flex-col gap-4 w-full h-full overflow-y-auto">
					<p className="font-bold">Code</p>
					<ReactCodeMirror
						height="700px"
						extensions={[cpp()]}
						value={code}
						onChange={(e) => setCode(e)}
					/>
					<div className="flex flex-row w-full justify-between items-center">
						<div className="flex flex-col gap-2">
							<button
								className="p-2 bg-blue-700 text-white rounded-md shadow-sm w-40 font-bold"
								onClick={handleSubmit}
								disabled={submissionLoading}
							>
								{submissionLoading ? "Submitting..." : "Submit"}
							</button>
							{submissionError && (
								<p className="text-red-500 text-sm">{submissionError}</p>
							)}
						</div>
						{submissionResult &&
							submissionResult.quiz.code_correct === true && (
								<Link href={`/program/${programId}/quiz`}>
									<button className="p-2 bg-green-700 text-white rounded-md shadow-sm w-40 font-bold">
										Attempt a Quiz
									</button>
								</Link>
							)}
					</div>
					{submissionResult && (
						<>
							<div className="flex flex-col gap-2">
								<h3 className="font-bold text-2xl">
									Code{" "}
									{submissionResult.quiz.code_correct ? "Correct" : "Incorrect"}
								</h3>
								{submissionResult.quiz.code_errors?.length > 0 ? (
									<h4 className="font-bold text-lg">Errors</h4>
								) : (
									<></>
								)}
								{(submissionResult.quiz.code_errors ?? []).map((e) => (
									<div className="flex flex-col gap-2 bg-white rounded-md p-4 border border-gray-200">
										<h4 className="font-bold text-lg">{e.error_type}</h4>
										<p>{e.description}</p>
										<p>{e.error_type}</p>
										<code>{e.incorrect_code}</code>
									</div>
								))}
							</div>
							<div className="flex flex-col gap-2">
								{submissionResult?.results.map((result, index) => (
									<div key={index} className="flex flex-col gap-2 w-full">
										<p className="font-bold">Test Case {index + 1}</p>
										<p className="text-sm">Input: {result.stdin}</p>
										<p className="text-sm">Output: {result.stdout}</p>
										<p className="text-sm">Error: {result.stderr}</p>
										<p className="text-sm">
											Compile Output: {result.compile_output}
										</p>
									</div>
								))}
							</div>
						</>
					)}
				</div>
			) : (
				<div className="flex flex-col gap-4 w-full h-full overflow-y-auto">
					<h3 className="font-bold text-2xl">Reports</h3>
					{quizLoading ? (
						<p className="p-4">Loading...</p>
					) : (
						<div className="flex flex-col gap-2">
							{quizzesWithMarks.length === 0 ? (
								<p className="text-gray-500 text-sm">
									No quizzes taken for this program.
								</p>
							) : (
								<>
									<div className="w-full flex flex-row justify-center">
										{typeof window !== "undefined" && (
											<MarksPieChart data={quizzesWithMarks} />
										)}
									</div>
									{/* Table of quizzes sorted by marks */}
									<table className="min-w-full bg-white border border-gray-200 rounded-md mb-4">
										<thead>
											<tr>
												<th className="px-4 py-2 border-b">Student ID</th>
												<th className="px-4 py-2 border-b">Marks</th>
											</tr>
										</thead>
										<tbody>
											{[...quizzesWithMarks]
												.sort((a, b) => a.marks - b.marks)
												.map((quiz) => (
													<tr key={quiz.id}>
														<td className="px-4 py-2 border-b">
															{quiz.student_id}
														</td>
														<td className="px-4 py-2 border-b">{quiz.marks}</td>
													</tr>
												))}
										</tbody>
									</table>
								</>
							)}
						</div>
					)}
				</div>
			)}
		</div>
	)
}

const COLORS = [
	"#0088FE",
	"#00C49F",
	"#FFBB28",
	"#FF8042",
	"#A28CFE",
	"#FF6699",
]

function groupMarks(data: any[]) {
	// Group marks into buckets (e.g., 0-2, 3-5, 6-8, 9-10)
	const buckets = [
		{ name: "0-2", range: [0, 2], value: 0 },
		{ name: "3-5", range: [3, 5], value: 0 },
		{ name: "6-8", range: [6, 8], value: 0 },
		{ name: "9-10", range: [9, 10], value: 0 },
	]
	data.forEach((quiz) => {
		const mark = quiz.marks
		const bucket = buckets.find((b) => mark >= b.range[0] && mark <= b.range[1])
		if (bucket) bucket.value += 1
	})
	return buckets.filter((b) => b.value > 0)
}

function MarksPieChart({ data }: { data: any[] }) {
	const pieData = groupMarks(data)
	return (
		<div style={{ width: 350, height: 300 }}>
			<ResponsiveContainer width="100%" height="100%">
				<PieChart>
					<Pie
						data={pieData}
						dataKey="value"
						nameKey="name"
						cx="50%"
						cy="50%"
						outerRadius={80}
						label
					>
						{pieData.map((_, index) => (
							<Cell
								key={`cell-${index}`}
								fill={COLORS[index % COLORS.length]}
							/>
						))}
					</Pie>
					<Tooltip />
					<Legend />
				</PieChart>
			</ResponsiveContainer>
		</div>
	)
}
