import fs from 'fs'
import path from 'path'

export interface Article {
  title: string
  slug: string
  html: string
  meta_description: string
  word_count: number
  keyword: string
  created_at: string
  image_prompt?: string
}

const CONTENT_DIR = path.join(process.cwd(), 'content', 'articles')

export function getAllArticles(): Article[] {
  if (!fs.existsSync(CONTENT_DIR)) return []

  const files = fs.readdirSync(CONTENT_DIR).filter(f => f.endsWith('.json'))

  const articles = files.map(file => {
    const raw = fs.readFileSync(path.join(CONTENT_DIR, file), 'utf-8')
    return JSON.parse(raw) as Article
  })

  // Sort by created_at descending (newest first)
  articles.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  return articles
}

export function getArticleBySlug(slug: string): Article | null {
  const filePath = path.join(CONTENT_DIR, `${slug}.json`)
  if (!fs.existsSync(filePath)) return null
  const raw = fs.readFileSync(filePath, 'utf-8')
  return JSON.parse(raw) as Article
}

export function getAllSlugs(): string[] {
  if (!fs.existsSync(CONTENT_DIR)) return []
  return fs
    .readdirSync(CONTENT_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => f.replace('.json', ''))
}
