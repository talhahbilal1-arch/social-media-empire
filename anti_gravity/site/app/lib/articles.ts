import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { marked } from 'marked'

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

function parseMarkdownArticle(filePath: string): Article {
  const raw = fs.readFileSync(filePath, 'utf-8')
  const { data, content } = matter(raw)

  const html = marked.parse(content, { async: false }) as string
  const wordCount = content.split(/\s+/).filter(Boolean).length

  return {
    title: data.title || '',
    slug: data.slug || path.basename(filePath, '.md'),
    html,
    meta_description: data.description || '',
    word_count: wordCount,
    keyword: data.category || '',
    created_at: data.date || new Date().toISOString(),
  }
}

export function getAllArticles(): Article[] {
  if (!fs.existsSync(CONTENT_DIR)) return []

  const files = fs.readdirSync(CONTENT_DIR).filter(f => f.endsWith('.md'))

  const articles = files.map(file => {
    return parseMarkdownArticle(path.join(CONTENT_DIR, file))
  })

  // Sort by created_at descending (newest first)
  articles.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  return articles
}

export function getArticleBySlug(slug: string): Article | null {
  const filePath = path.join(CONTENT_DIR, `${slug}.md`)
  if (!fs.existsSync(filePath)) return null
  return parseMarkdownArticle(filePath)
}

export function getAllSlugs(): string[] {
  if (!fs.existsSync(CONTENT_DIR)) return []
  return fs
    .readdirSync(CONTENT_DIR)
    .filter(f => f.endsWith('.md'))
    .map(f => f.replace('.md', ''))
}
