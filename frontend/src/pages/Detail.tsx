import { useParams } from 'react-router-dom'

export default function Detail() {
  const { ticker } = useParams<{ ticker: string }>()

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">종목 상세: {ticker}</h1>
      <p className="text-gray-600 dark:text-gray-400">상세 페이지 (구현 예정)</p>
    </div>
  )
}

