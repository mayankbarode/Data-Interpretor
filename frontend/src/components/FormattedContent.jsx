export default function FormattedContent({ content }) {
    if (!content) return null

    const parseBold = (text) => {
        const parts = []
        const boldRegex = /\*\*(.+?)\*\*/g
        let lastIndex = 0
        let match
        let key = 0

        while ((match = boldRegex.exec(text)) !== null) {
            if (match.index > lastIndex) {
                parts.push(
                    <span key={key++}>{text.slice(lastIndex, match.index)}</span>
                )
            }
            parts.push(
                <strong key={key++} className="font-bold text-gray-900">
                    {match[1]}
                </strong>
            )
            lastIndex = boldRegex.lastIndex
        }

        if (lastIndex < text.length) {
            parts.push(<span key={key++}>{text.slice(lastIndex)}</span>)
        }

        return parts.length > 0 ? parts : text
    }

    const renderTable = (lines, startIdx) => {
        const tableLines = []
        let idx = startIdx

        while (idx < lines.length && lines[idx].includes('|')) {
            tableLines.push(lines[idx])
            idx++
        }

        if (tableLines.length < 2) return { element: null, nextIdx: startIdx }

        const headers = tableLines[0]
            .split('|')
            .map((h) => h.trim())
            .filter((h) => h)
        const rows = tableLines.slice(2).map((row) =>
            row
                .split('|')
                .map((cell) => cell.trim())
                .filter((cell) => cell)
        )

        return {
            element: (
                <div className="overflow-x-auto my-4">
                    <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden shadow-sm">
                        <thead className="bg-gradient-to-r from-purple-50 to-blue-50">
                            <tr>
                                {headers.map((header, i) => (
                                    <th
                                        key={i}
                                        className="border-b-2 border-purple-200 px-4 py-3 text-left text-sm font-bold text-gray-700"
                                    >
                                        {header}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row, i) => (
                                <tr
                                    key={i}
                                    className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                                >
                                    {row.map((cell, j) => (
                                        <td
                                            key={j}
                                            className="border-b border-gray-200 px-4 py-2 text-sm text-gray-800"
                                        >
                                            {cell}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ),
            nextIdx: idx,
        }
    }

    const lines = content.split('\n')
    const elements = []
    let i = 0

    while (i < lines.length) {
        const line = lines[i]
        const trimmed = line.trim()

        if (line.includes('|') && line.split('|').length > 2) {
            const { element, nextIdx } = renderTable(lines, i)
            if (element) {
                elements.push(<div key={`table-${i}`}>{element}</div>)
                i = nextIdx
                continue
            }
        }

        if (trimmed.startsWith('### ')) {
            elements.push(
                <h3 key={i} className="text-lg font-bold text-purple-700 mt-4 mb-2">
                    {parseBold(trimmed.slice(4))}
                </h3>
            )
        } else if (trimmed.startsWith('## ')) {
            elements.push(
                <h2 key={i} className="text-xl font-bold text-purple-800 mt-5 mb-3">
                    {parseBold(trimmed.slice(3))}
                </h2>
            )
        } else if (trimmed.startsWith('# ')) {
            elements.push(
                <h1 key={i} className="text-2xl font-bold text-purple-900">
                    {parseBold(trimmed.slice(2))}
                </h1>
            )
        } else if (trimmed.startsWith('- ')) {
            elements.push(
                <div key={i} className="flex items-start ml-4 my-1">
                    <span className="text-purple-600 mr-2 mt-1">●</span>
                    <p className="text-gray-700 leading-relaxed flex-1">
                        {parseBold(trimmed.slice(2))}
                    </p>
                </div>
            )
        } else if (trimmed.match(/^\d+\.\s/)) {
            const match = trimmed.match(/^(\d+)\.\s(.+)$/)
            if (match) {
                elements.push(
                    <div key={i} className="flex items-start ml-4 my-1">
                        <span className="text-purple-600 font-semibold mr-2 min-w-[24px]">
                            {match[1]}.
                        </span>
                        <p className="text-gray-700 leading-relaxed flex-1">
                            {parseBold(match[2])}
                        </p>
                    </div>
                )
            }
        } else if (trimmed === '') {
            elements.push(<div key={i} className="h-2"></div>)
        } else {
            elements.push(
                <p key={i} className="text-gray-700 leading-relaxed my-1">
                    {parseBold(line)}
                </p>
            )
        }
        i++
    }

    return <div className="space-y-0.5">{elements}</div>
}
