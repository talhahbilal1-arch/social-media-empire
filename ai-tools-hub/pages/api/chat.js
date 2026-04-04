import { streamText } from 'ai';
import { toTextStreamResponse } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import tools from '../../content/tools.json';

// Initialize OpenAI client routed through Vercel AI Gateway
const client = createOpenAI({
  baseURL: process.env.AI_GATEWAY_URL || 'https://gateway.ai.cloudflare.com',
  apiKey: process.env.AI_GATEWAY_OIDC_TOKEN || 'dummy',
  defaultHeaders: process.env.AI_GATEWAY_OIDC_TOKEN ? {
    Authorization: `Bearer ${process.env.AI_GATEWAY_OIDC_TOKEN}`,
  } : {},
});

// Build a summary of available tools for the system prompt
const toolsSummary = tools.map(tool => ({
  name: tool.name,
  slug: tool.slug,
  categories: tool.categories,
  description: tool.description?.split('\n')[0] || '',
  pricing: tool.pricing?.starting_price === 0 ? 'Free' : `$${tool.pricing?.starting_price}/mo`,
  affiliate_url: tool.affiliate_url,
}));

const SYSTEM_PROMPT = `You are an expert AI tool recommendation assistant for PilotTools.ai. Your role is to help users find the perfect AI tools for their specific needs.

Available tools database:
${JSON.stringify(toolsSummary, null, 2)}

When recommending tools:
1. Listen carefully to the user's needs and use case
2. Recommend 2-3 most relevant tools from the database
3. Explain why each tool is perfect for their specific situation
4. Be conversational and helpful
5. Include pricing information if relevant
6. Suggest alternatives if the user asks

Always be specific about why a tool matches their needs. Reference their use case directly.
Format recommendations clearly so they're easy to read.
If the user asks about a tool not in the database, let them know and suggest the closest alternative.`;

export async function POST(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { messages } = await req.json();

    // Validate input
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'Messages array is required' });
    }

    // Stream the response from Claude
    const result = await streamText({
      model: client('claude-3-5-sonnet-20241022'),
      system: SYSTEM_PROMPT,
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      })),
      temperature: 0.7,
      max_tokens: 1024,
    });

    // Return as text stream response
    return toTextStreamResponse(result);
  } catch (error) {
    console.error('Chat API error:', error);
    return res.status(500).json({
      error: 'Failed to process chat request',
      message: error.message
    });
  }
}
