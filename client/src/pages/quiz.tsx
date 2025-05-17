import { Link, useParams } from "wouter"
import { useState } from "react"
import { useQuizByProgramUser, markQuizAnswers } from "../api/quiz"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"

export default function QuizPage() {
	const user = useEnsureAuthenticated(true)
	const params = useParams<{ programId: string }>()
	const programId = Number(params.programId)
	const studentId = user?.id ?? 0

	const {
		data: quiz,
		isLoading,
		mutate,
	} = useQuizByProgramUser(programId, studentId)
	const [current, setCurrent] = useState(0)
	const [answers, setAnswers] = useState<{ [key: string]: string }>({})
	const [submitted, setSubmitted] = useState(false)
	const [submitting, setSubmitting] = useState(false)
	const [result, setResult] = useState<{ marks: number; total: number } | null>(
		null
	)

	if (isLoading) {
		return <div className="p-8">Loading quiz...</div>
	}
	if (!quiz) {
		return <div className="p-8">Quiz not found.</div>
	}

	const questions = quiz.questions || []

	const handleSelect = (option: string) => {
		setAnswers((prev) => ({
			...prev,
			[String(current)]: option,
		}))
	}

	const handlePrev = () => setCurrent((c) => Math.max(0, c - 1))
	const handleNext = () =>
		setCurrent((c) => Math.min(questions.length - 1, c + 1))

	const handleSubmit = async () => {
		setSubmitting(true)
		const res = await markQuizAnswers({ quiz_id: quiz.id, answers })
		setSubmitting(false)
		setSubmitted(true)
		if (res && res.data) {
			setResult({ marks: res.data.marks, total: res.data.total })
			mutate() // refresh quiz data
		}
	}

	const q = questions[current]

	return (
		<div className="max-w-xl mx-auto mt-10 text-center p-6">
			<h2 className="text-2xl font-bold mb-4 ">Quiz</h2>
			{q && (
				<div>
					<div className="mb-4 text-lg font-medium">
						Q{current + 1}: {q.question}
					</div>
					<div className="flex flex-col gap-2 mb-6">
						{q.options.map((opt: string, idx: number) => (
							<button
								key={idx}
								className={`px-4 py-2 rounded border text-left ${
									answers[String(current)] === opt
										? "bg-blue-500 text-white border-blue-700"
										: "bg-blue-50 border-blue-300 text-blue-900 hover:bg-blue-100"
								}`}
								onClick={() => handleSelect(opt)}
								disabled={submitted}
							>
								{opt}
							</button>
						))}
					</div>
					<div className="flex justify-between">
						<button
							className="px-4 py-2 rounded bg-blue-100  font-semibold disabled:opacity-50"
							onClick={handlePrev}
							disabled={current === 0}
						>
							Prev
						</button>
						<button
							className="px-4 py-2 rounded bg-blue-100  font-semibold disabled:opacity-50"
							onClick={handleNext}
							disabled={current === questions.length - 1}
						>
							Next
						</button>
					</div>
					{current === questions.length - 1 && !submitted && (
						<button
							className="mt-6 w-full px-4 py-2 rounded bg-blue-600 text-white font-bold hover:bg-blue-700 disabled:opacity-50"
							onClick={handleSubmit}
							disabled={
								Object.keys(answers).length !== questions.length || submitting
							}
						>
							{submitting ? "Submitting..." : "Submit Quiz"}
						</button>
					)}
					{submitted && result && (
						<>
							<div className="mt-6 text-xl  font-bold text-center">
								You scored {result.marks} out of {result.total}
							</div>
							<p>
								Your response has been recorded. You may go back to the home
								page.
							</p>
							<Link href="/home">
								<button className="mt-4 w-full px-4 py-2 rounded bg-blue-600 text-white font-bold hover:bg-blue-700">
									Go to Home
								</button>
							</Link>
						</>
					)}
				</div>
			)}
		</div>
	)
}
