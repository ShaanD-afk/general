export default function SelectLanguage({
	language,
	setLanguage,
}: {
	language: string
	setLanguage: (language: string) => void
}) {
	return (
		<div className="flex flex-col gap-2">
			<p className="text-sm">Select your language</p>
			<select
				value={language}
				onChange={(e) => setLanguage(e.target.value)}
				className="border-1 border-gray-700 px-2 py-1 rounded-md"
			>
				<option value="ka">Kannada</option>
				<option value="en">English</option>
				<option value="fr">French</option>
				<option value="de">German</option>
			</select>
		</div>
	)
}
